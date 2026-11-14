"""Generate a bounded C++20 probe of the rtld AArch64 entry path."""
import argparse
import hashlib
from pathlib import Path
import re

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
from verify_exefs import read_module

BASE = 0x80000000


def reg(text):
    if not re.fullmatch(r"[xw](?:[0-9]|[12][0-9]|30)", text):
        raise ValueError(f"unsupported register: {text}")
    slot = f"x[{text[1:]}]"
    return slot, f"std::uint32_t({slot})" if text[0] == "w" else slot


FILL_TEXT_SHA256 = "efcc6ebfac7d2a23068bff8a8b451e3556c9837e811e5f20b2bd7bbd2ef23f52"


def generate(code, fill_window=None):
    decoder = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    # The bounded probe starts with X0=X1=0 and verifies a forward-only path.
    pc, visited, lines = 0, set(), []
    filled = False
    if fill_window is not None and hashlib.sha256(code).hexdigest() != FILL_TEXT_SHA256:
        raise ValueError("host fill is supported only for the verified rtld text revision")
    while 0 <= pc <= len(code) - 4 and pc % 4 == 0 and pc not in visited and len(visited) < 64:
        visited.add(pc)
        ins = next(decoder.disasm(code[pc:pc + 4], pc), None)
        if ins is None:
            raise ValueError(f"invalid instruction at {pc:#x}")
        op = ins.mnemonic
        args = ins.op_str.split(", ")
        if op == "b":
            target = int(args[0].removeprefix("#"), 0)
            if target <= pc:
                raise ValueError(f"non-forward branch at {pc:#x}")
            pc = target
            continue
        if op == "cmp" and args == ["x0", "#0"]:
            lines.append("    const bool zero = x[0] == 0;")
        elif op == "b.ne" and "    const bool zero = x[0] == 0;" in lines:
            target = int(args[0].removeprefix("#"), 0)
            lines.append(f'    if (!zero) {{ std::printf("outside probe: branch to 0x{target:x}\\n"); return 2; }}')
        elif op == "mov":
            dest, source = args
            out, _ = reg(dest)
            rhs = int(source[1:], 0) if source.startswith("#") else reg(source)[1]
            cast = "uint32_t" if dest.startswith("w") else "uint64_t"
            lines.append(f"    {out} = std::{cast}({rhs});")
        elif op == "adr":
            out, _ = reg(args[0])
            value = BASE + int(args[1].removeprefix("#"), 0)
            lines.append(f"    {out} = 0x{value:x}ULL;")
        elif op == "sub" and len(args) == 3 and all(arg.startswith("x") for arg in args):
            lines.append(f"    {reg(args[0])[0]} = {reg(args[1])[1]} - {reg(args[2])[1]};")
        elif op == "bl":
            target = int(args[0].removeprefix("#"), 0)
            if target % 4 or not 0 <= target <= len(code) - 4:
                raise ValueError("call target outside text")
            lines.append(f"    x[30] = 0x{BASE + pc + 4:x}ULL;")
            if fill_window is not None and not filled and pc == 0x30 and target == 0x21e0:
                lines += [
                    '    if (x[0] < memoryBase || x[0] - memoryBase > memory.size() ||',
                    '        x[2] > memory.size() - (x[0] - memoryBase)) return 3;',
                    '    std::memset(memory.data() + (x[0] - memoryBase), int(x[1] & 255), x[2]);',
                    '    std::printf("host fill completed: %llu bytes\\n", static_cast<unsigned long long>(x[2]));',
                ]
                filled = True
                pc += 4
                continue
            lines.append(f'    std::printf("paused before BL at 0x{pc:x} to 0x{target:x}; AAPCS args %llx %llx %llx\\n",')
            lines.append("        static_cast<unsigned long long>(x[0]), static_cast<unsigned long long>(x[1]), static_cast<unsigned long long>(x[2]));")
            lines.append("    return 0;")
            prefix = '#include <cstdint>\n#include <cstdio>\nint main() {\n    std::uint64_t x[31]{};\n'
            if fill_window is not None:
                if not filled:
                    raise ValueError("expected verified startup fill call")
                start, size = fill_window
                prefix = "#include <vector>\n#include <cstring>\n" + prefix
                prefix += f"    const std::uint64_t memoryBase = {start}ULL;\n"
                prefix += f"    std::vector<unsigned char> memory({size}, 0xA5);\n"
            return prefix + "\n".join(lines) + "\n}\n"
        elif op != "nop":
            raise ValueError(f"unsupported instruction {op} at {pc:#x}")
        pc += 4
    raise ValueError("bounded entry path did not reach a call")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exefs", type=Path)
    parser.add_argument("cpp", type=Path)
    parser.add_argument("--host-fill", action="store_true", help="apply the verified startup fill to an isolated buffer")
    args = parser.parse_args()
    try:
        info, segments, bss = read_module(args.exefs / "rtld")
        data = info["segments"]["data"]
        size = data["decoded_bytes"] + bss
        if args.host_fill and not 0 < size <= 512 * 1024 * 1024:
            raise ValueError("invalid data/BSS size")
        window = (BASE + data["memory_offset"], size) if args.host_fill else None
        source = generate(segments["text"], window)
        with args.cpp.open("x", encoding="utf-8") as output:
            output.write(source)
    except (OSError, ValueError, ImportError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
