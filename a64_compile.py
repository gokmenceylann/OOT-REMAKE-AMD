"""Ahead-of-time compiler for a bounded integer AArch64 subset."""
import argparse
from dataclasses import dataclass
from pathlib import Path
import re

from a64_analyze import analyze

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM


@dataclass(frozen=True)
class Reg:
    index: int
    width: int
    zero: bool = False


@dataclass(frozen=True)
class Mem:
    base: Reg
    offset: int
    writeback: bool = False
    post: bool = False
    index: Reg | None = None
    extension: str = ''
    shift: int = 0


@dataclass(frozen=True)
class Instruction:
    pc: int
    op: str
    args: tuple


def register(token):
    if token in ("sp", "wsp"):
        return Reg(31, 64 if token == "sp" else 32)
    if token in ("xzr", "wzr"):
        return Reg(31, 64 if token == "xzr" else 32, True)
    if not re.fullmatch(r"[wx](?:[0-9]|[12][0-9]|30)", token):
        raise ValueError(f"unsupported register {token}")
    return Reg(int(token[1:]), 64 if token[0] == "x" else 32)


def immediate(token):
    if not token.startswith("#"):
        raise ValueError(f"expected immediate, got {token}")
    return int(token[1:], 0)


def value(token):
    return immediate(token) if token.startswith("#") else register(token)


CONDITIONS = {
    "eq": "z", "ne": "!z", "hs": "c", "lo": "!c", "mi": "n", "pl": "!n",
    "vs": "v", "vc": "!v", "hi": "c && !z", "ls": "!c || z",
    "ge": "n == v", "lt": "n != v", "gt": "!z && n == v", "le": "z || n != v",
}
ARITHMETIC = {"add", "adds", "sub", "subs", "cmp", "cmn"}
LOGICAL = {"and", "ands", "orr", "eor", "tst", "bic", "bics"}
MEMORY = {
    "ldr": 0, "ldur": 0, "str": 0, "stur": 0,
    "ldrb": 1, "ldurb": 1, "strb": 1, "sturb": 1,
    "ldrh": 2, "ldurh": 2, "strh": 2, "sturh": 2,
}


def lower(op, text):
    tokens = text.split(", ") if text else []
    if op in ("add", "sub", "mul", "fadd", "fsub", "fmul", "fdiv") and len(tokens) == 3:
        vectors = [re.fullmatch(r"v([0-9]|[12][0-9]|3[01])\.(8b|16b|4h|8h|2s|4s|2d)", token) for token in tokens]
        if all(vectors):
            shape = vectors[0][2]
            if not all(vector[2] == shape for vector in vectors):
                raise ValueError("mismatched vector arrangements")
            if (op.startswith("f") and shape not in ("2s", "4s", "2d")) or (op == "mul" and shape == "2d"):
                raise ValueError("unsupported vector arrangement")
            return shape, *(int(vector[1]) for vector in vectors)
    if op in ("eor", "and", "orr") and len(tokens) == 3 and all(
        re.fullmatch(r"v(?:[0-9]|[12][0-9]|3[01])\.16b", token) for token in tokens
    ):
        return tuple(int(token[1:].split(".")[0]) for token in tokens)
    if op in ARITHMETIC | LOGICAL:
        compare = op in ("cmp", "cmn", "tst")
        if len(tokens) == (2 if compare else 3):
            lhs, rhs = register(tokens[-2]), value(tokens[-1])
            dest = Reg(31, lhs.width, True) if compare else register(tokens[0])
            if dest.width == lhs.width and (not isinstance(rhs, Reg) or rhs.width == lhs.width):
                return dest, lhs, rhs
    elif op in ("clz", "rbit", "neg") and len(tokens) == 2:
        dest, src = map(register, tokens)
        if dest.width == src.width:
            return dest, src
    elif op in ("madd", "msub") and len(tokens) == 4:
        regs = tuple(map(register, tokens))
        if all(reg.width == regs[0].width for reg in regs):
            return regs
    elif op in ("fadd", "fsub", "fmul", "fdiv") and len(tokens) == 3:
        if all(re.fullmatch(r"[sd](?:[0-9]|[12][0-9]|3[01])", token) for token in tokens) and all(
            token[0] == tokens[0][0] for token in tokens
        ):
            return (32 if tokens[0][0] == "s" else 64, *(int(token[1:]) for token in tokens))
    elif op == "mov" and len(tokens) == 2:
        dest, src = register(tokens[0]), value(tokens[1])
        if not isinstance(src, Reg) or src.width == dest.width:
            return dest, src
    elif op == "movk" and len(tokens) in (2, 3):
        dest = register(tokens[0])
        shift = immediate(tokens[2].removeprefix("lsl ")) if len(tokens) == 3 else 0
        imm = immediate(tokens[1])
        if len(tokens) == 3 and not tokens[2].startswith("lsl "):
            raise ValueError("unsupported MOVK modifier")
        if shift % 16 == 0 and 0 <= shift < dest.width and 0 <= imm <= 65535:
            return dest, imm, shift
    elif op in ("lsl", "lsr", "asr") and len(tokens) == 3:
        dest, source = map(register, tokens[:2])
        count = value(tokens[2])
        valid = count.width == dest.width if isinstance(count, Reg) else 0 <= count < dest.width
        if dest.width == source.width and valid:
            return dest, source, count
    elif op in ("ldp", "stp") or op in MEMORY:
        pair = op in ("ldp", "stp")
        registers = r"(\w+), (\w+), " if pair else r"(\w+), "
        number = r"#-?(?:0x[0-9a-f]+|[0-9]+)"
        if not pair:
            indexed = re.fullmatch(r"(\w+), \[(\w+), (\w+)(?:, (lsl|uxtw|sxtw|sxtx)(?:,? #([0-9]+))?)?\]", text)
            if indexed:
                dest, base, index = map(register, indexed.groups()[:3])
                extension, shift = indexed.groups()[3:]
                extension = extension or "lsl"
                if (base.width == 64 and not base.zero and
                        index.width == (32 if extension.endswith("tw") else 64) and int(shift or 0) < 64):
                    return dest, Mem(base, 0, index=index, extension=extension, shift=int(shift or 0))
        match = re.fullmatch(registers + rf"\[(\w+)(?:, ({number}))?\](!|, {number})?", text)
        if match:
            *regs, base, offset, suffix = match.groups()
            regs = tuple(map(register, regs))
            base = register(base)
            post = bool(suffix and suffix.startswith(", "))
            if base.width != 64 or base.zero or (post and offset):
                raise ValueError("invalid memory addressing")
            if any(reg.width != regs[0].width for reg in regs):
                raise ValueError("mismatched pair widths")
            if suffix and any(reg == base or (reg.index == base.index and not reg.zero) for reg in regs):
                raise ValueError("unsupported base/register writeback overlap")
            if op == "ldp" and regs[0] == regs[1] and not regs[0].zero:
                raise ValueError("unsupported overlapping LDP destinations")
            delta = immediate(suffix[2:]) if post else immediate(offset) if offset else 0
            return (*regs, Mem(base, delta, bool(suffix), post))
    elif op in ("b", "bl") or (op.startswith("b.") and op[2:] in CONDITIONS):
        if len(tokens) == 1:
            return (immediate(tokens[0]),)
    elif op in ("tbz", "tbnz") and len(tokens) == 3:
        return register(tokens[0]), immediate(tokens[1]), immediate(tokens[2])
    elif op in ("cbz", "cbnz") and len(tokens) == 2:
        return register(tokens[0]), immediate(tokens[1])
    elif op in ("adr", "adrp") and len(tokens) == 2:
        return register(tokens[0]), immediate(tokens[1])
    elif op in ("br", "blr") and len(tokens) == 1:
        return (register(tokens[0]),)
    elif op == "ret" and len(tokens) <= 1:
        return (register(tokens[0] if tokens else "x30"),)
    elif op == "mrs" and len(tokens) == 2 and tokens[1] in ("fpcr", "fpsr"):
        return register(tokens[0]), tokens[1]
    elif op == "msr" and len(tokens) == 2 and tokens[0] in ("fpcr", "fpsr"):
        return register(tokens[1]), tokens[0]
    elif op == "svc" and len(tokens) == 1:
        return (immediate(tokens[0]),)
    elif op == "nop" and not tokens:
        return ()
    raise ValueError(f"unsupported form: {op} {text}")


def decode(code, base=0, reachable=False, stop_calls=False, host_fill=None, selected=None):
    if not code or len(code) % 4 or base % 4 or not 0 <= base <= (1 << 64) - len(code) - 4:
        raise ValueError("expected aligned guest base and complete instruction words")
    decoder = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    result = []
    offsets = [pc - base for pc in selected] if selected is not None else ([0] if reachable else list(range(0, len(code), 4)))
    seen = set()
    while offsets:
        offset = offsets.pop()
        if offset in seen:
            continue
        if offset < 0 or offset + 4 > len(code) or offset % 4:
            raise ValueError(f"invalid instruction target at {base + offset:#x}")
        seen.add(offset)
        pc = base + offset
        ins = next(decoder.disasm(code[offset:offset + 4], pc), None)
        if ins is None:
            raise ValueError(f"{pc:#x}: invalid A64 encoding")
        try:
            args = lower(ins.mnemonic, ins.op_str)
        except ValueError as exc:
            raise ValueError(f"{pc:#x}: {exc}") from exc
        result.append(Instruction(pc, ins.mnemonic, args))
        if reachable and ins.mnemonic != "ret":
            direct = ins.mnemonic in ("b", "bl", "cbz", "cbnz", "tbz", "tbnz") or ins.mnemonic.startswith("b.")
            if direct:
                if not stop_calls or ins.mnemonic == "b":
                    offsets.append(args[-1] - base)
            if ins.mnemonic not in ("b", "bl") or (ins.mnemonic == "bl" and (not stop_calls or (pc, args[0]) == host_fill)):
                if offset + 4 < len(code):
                    offsets.append(offset + 4)
    result.sort(key=lambda ins: ins.pc)
    addresses = {ins.pc for ins in result}
    for ins in result:
        if ins.op in ("b", "bl", "cbz", "cbnz", "tbz", "tbnz") or ins.op.startswith("b."):
            if ins.op == "bl" and stop_calls:
                if ins.args[0] < base or ins.args[0] >= base + len(code) or ins.args[0] % 4:
                    raise ValueError(f"{ins.pc:#x}: invalid call target")
            elif ins.args[-1] not in addresses and not (stop_calls and ins.op != "b") and not (selected is not None and ins.op == "bl"):
                raise ValueError(f"{ins.pc:#x}: branch target outside input")
    return result


def literal(number):
    return f"0x{number & ((1 << 64) - 1):x}ULL"


def read(operand):
    if isinstance(operand, int):
        return literal(operand)
    expr = "0ULL" if operand.zero else f"s.x[{operand.index}]"
    return f"std::uint32_t({expr})" if operand.width == 32 else expr


def write(dest, expr):
    if dest.zero:
        return []
    return [f"s.x[{dest.index}] = std::uint{dest.width}_t({expr});"]


def emit(ins, last, addresses, stop_calls, host_fill):
    op, args = ins.op, ins.args
    out = []

    def jump(target):
        if target in addresses:
            return f"goto L{target:x};"
        return f"{{ s.stop_target = {literal(target)}; return Status::external_branch; }}"

    if op in ("fadd", "fsub", "fmul", "fdiv"):
        out.append("if (s.fpcr) return Status::unsupported_fp_mode;")
    if isinstance(args[0] if args else None, str):
        shape, dest, lhs, rhs = args
        width = {"b": 8, "h": 16, "s": 32, "d": 64}[shape[-1]]
        count = int(shape[:-1])
        operator = {"add": "+", "sub": "-", "mul": "*",
                    "fadd": "+", "fsub": "-", "fmul": "*", "fdiv": "/"}[op]
        out += ["std::array<std::uint64_t, 2> result{};",
                f"for (unsigned lane = 0; lane < {count}; ++lane) {{",
                f"    const auto a = A64State::read_lane<{width}>(s.q[{lhs}], lane);",
                f"    const auto b = A64State::read_lane<{width}>(s.q[{rhs}], lane);"]
        if op.startswith("f"):
            typ = "float" if width == 32 else "double"
            bits = f"std::uint{width}_t"
            out += [f"    const auto computed = std::bit_cast<{typ}>({bits}(a)) {operator} std::bit_cast<{typ}>({bits}(b));",
                    f"    A64State::write_lane<{width}>(result, lane, std::bit_cast<{bits}>(computed));"]
        else:
            out += [f"    A64State::write_lane<{width}>(result, lane, a {operator} b);"]
        out += ["}", f"s.q[{dest}] = result;"]
    elif op in ("fadd", "fsub", "fmul", "fdiv"):
        width, dest, lhs, rhs = args
        typ = "float" if width == 32 else "double"
        bits = f"std::uint{width}_t"
        operator = {"fadd": "+", "fsub": "-", "fmul": "*", "fdiv": "/"}[op]
        out.append(f"const auto a = std::bit_cast<{typ}>({bits}(s.q[{lhs}][0]));")
        out.append(f"const auto b = std::bit_cast<{typ}>({bits}(s.q[{rhs}][0]));")
        out.append(f"s.q[{dest}] = {{std::bit_cast<{bits}>(a {operator} b), 0}};")
    elif op in ("eor", "and", "orr") and isinstance(args[0], int):
        dest, lhs, rhs = args
        operator = {"eor": "^", "and": "&", "orr": "|"}[op]
        for lane in range(2):
            out.append(f"s.q[{dest}][{lane}] = s.q[{lhs}][{lane}] {operator} s.q[{rhs}][{lane}];")
    elif op in ARITHMETIC | LOGICAL:
        dest, lhs, rhs = args
        width = dest.width
        operator = ("+" if op in ("add", "adds", "cmn") else "-" if op in ("sub", "subs", "cmp")
                    else "&" if op in ("and", "ands", "tst", "bic", "bics") else "|" if op == "orr" else "^")
        rhs_expr = ("~" if op in ("bic", "bics") else "") + read(rhs)
        out.extend([f"const auto a = std::uint{width}_t({read(lhs)});",
                    f"const auto b = std::uint{width}_t({rhs_expr});",
                    f"const auto r = std::uint{width}_t(a {operator} b);"])
        if op in ("adds", "cmn", "subs", "cmp", "ands", "tst", "bics"):
            out.append(f"s.set_flags(a, b, r, {width}, '{operator}');")
        out += write(dest, "r")
        if not dest.zero or op in ("adds", "cmn", "subs", "cmp", "ands", "tst", "bics"):
            return out + (["return Status::fell_through;"] if last else [])
        out = []
    elif op in ("madd", "msub"):
        dest, a, b, c = args
        operator = "+" if op == "madd" else "-"
        out += write(dest, f"{read(c)} {operator} ({read(a)} * {read(b)})")
    elif op in ("mov", "adr", "adrp"):
        out += write(args[0], read(args[1]))
    elif op == "neg":
        out += write(args[0], f"0ULL - {read(args[1])}")
    elif op == "rbit":
        dest, source = args
        out += [f"auto input = {read(source)};", "std::uint64_t reversed = 0;",
                f"for (unsigned bit = 0; bit < {dest.width}; ++bit) {{",
                "    reversed = (reversed << 1) | (input & 1);",
                "    input >>= 1;",
                "}"]
        out += write(dest, "reversed")
    elif op == "clz":
        dest, source = args
        out += write(dest, f"std::countl_zero(std::uint{dest.width}_t({read(source)}))")
    elif op == "movk":
        dest, imm, shift = args
        out += write(dest, f"({read(dest)} & ~{literal(65535 << shift)}) | {literal(imm << shift)}")
    elif op in ("lsl", "lsr", "asr"):
        dest, source, count = args
        if isinstance(count, Reg):
            amount = f"({read(count)} & {dest.width - 1})"
            if op == "asr":
                expr = f"(std::int{dest.width}_t({read(source)}) >> {amount})"
            else:
                expr = f"{read(source)} {'<<' if op == 'lsl' else '>>'} {amount}"
            out += write(dest, expr)
            return out + (["return Status::fell_through;"] if last else [])
        if op == "asr":
            sign = f"({read(source)} >> {dest.width - 1})"
            mask = literal(((1 << count) - 1) << (dest.width - count))
            expr = f"({read(source)} >> {count}) | ((0ULL - {sign}) & {mask})"
        else:
            expr = f"{read(source)} {'<<' if op == 'lsl' else '>>'} {count}"
        out += write(dest, expr)
    elif op in ("ldp", "stp") or op in MEMORY:
        *regs, mem = args
        size = MEMORY.get(op, 0) or regs[0].width // 8
        delta = literal(mem.offset)
        if mem.index is not None:
            index = read(mem.index)
            if mem.extension == "sxtw":
                index = f"(std::uint64_t({index}) - ((std::uint64_t({index}) >> 31) << 32))"
            delta = f"(std::uint64_t({index}) << {mem.shift})"
        out.append(f"const auto updated = {read(mem.base)} + {delta};")
        out.append(f"const auto address = {read(mem.base) if mem.post else 'updated'};")
        out.append(f"if (!s.contains(address, {size * len(regs)})) return Status::memory_fault;")
        for index, dest in enumerate(regs):
            location = f"address + {size * index}"
            if op.startswith("ld"):
                temp = f"data{index}"
                out += [f"std::uint64_t {temp};", f"if (!s.load({location}, {size}, {temp})) return Status::memory_fault;"]
                out += write(dest, temp)
            else:
                out.append(f"if (!s.store({location}, {size}, {read(dest)})) return Status::memory_fault;")
        if mem.writeback:
            out += write(mem.base, "updated")
    elif op == "mrs":
        out += write(args[0], f"s.{args[1]}")
    elif op == "msr":
        mask = "0x07ff9f07u" if args[1] == "fpcr" else "0xf800009fu"
        out.append(f"s.{args[1]} = std::uint32_t({read(args[0])}) & {mask};")
    elif op == "svc":
        out += [f"const auto service = s.invoke_service({args[0]});",
                "if (service != ServiceResult::resume) return service == ServiceResult::exit_process",
                "    ? Status::guest_exit : Status::unsupported_service;"]
    elif op == "b":
        return [f"goto L{args[0]:x};"]
    elif op == "bl":
        link = f"s.x[30] = {literal(ins.pc + 4)};"
        if (ins.pc, args[0]) == host_fill:
            return [link, "if (!s.fill(s.x[0], s.x[1], s.x[2])) return Status::memory_fault;"]
        if stop_calls:
            return [link, f"s.stop_target = {literal(args[0])};", "return Status::external_branch;"]
        return [link, jump(args[0])] if args[0] in addresses else [link, f"if (!s.invoke_host({literal(args[0])})) {jump(args[0])}"]
    elif op in ("ret", "br", "blr"):
        out = [f"target = {read(args[0])};"]
        if op == "blr":
            out.append(f"s.x[30] = {literal(ins.pc + 4)};")
        if op == "blr":
            out.append("if (!s.invoke_host(target)) goto indirect;")
        else:
            return out + ["goto indirect;"]
    elif op.startswith("b."):
        expr = re.sub(r"\b[nzcv]\b", lambda m: "s." + m[0], CONDITIONS[op[2:]])
        out.append(f"if ({expr}) {jump(args[0])}")
    elif op in ("tbz", "tbnz"):
        comparison = "==" if op == "tbz" else "!="
        out.append(f"if ((({read(args[0])} >> {args[1]}) & 1) {comparison} 0) {jump(args[2])}")
    elif op in ("cbz", "cbnz"):
        comparison = "==" if op == "cbz" else "!="
        out.append(f"if ({read(args[0])} {comparison} 0) {jump(args[1])}")
    if last:
        out.append("return Status::fell_through;")
    return out


def compile_block(code, base=0, *, stop_calls=False, host_fill=None, entry=None, targets=()):
    selected = None
    if entry is not None:
        graph = analyze(code, [entry, *targets], base)
        if entry not in graph or not graph[entry]["instructions"]:
            raise ValueError("entry outside decoded text")
        selected = {pc for node in graph.values() for pc in node["instructions"]}
    ir = decode(code, base, reachable=stop_calls, stop_calls=stop_calls, host_fill=host_fill, selected=selected)
    addresses = {ins.pc for ins in ir}
    has_return = any(ins.op in ("ret", "br", "blr") for ins in ir)
    lines = ['#include "a64_state.hpp"', '#include <bit>', "Status run_a64(A64State& s, std::uint64_t budget, [[maybe_unused]] std::uint64_t return_address) {"]
    if has_return:
        lines.append("    std::uint64_t target = 0;")
    targets = {ins.pc for ins in ir} if has_return else {
        ins.args[-1] for ins in ir if ins.op in ("b", "bl", "cbz", "cbnz", "tbz", "tbnz") or ins.op.startswith("b.")
    }
    targets &= addresses
    if stop_calls and not has_return:
        targets = {ins.args[-1] for ins in ir if ins.op != 'bl' and (ins.op in ('b', 'cbz', 'cbnz') or ins.op.startswith('b.'))} & addresses
    if entry is not None:
        targets.add(entry)
        lines.append(f"    goto L{entry:x};")
    for i, ins in enumerate(ir):
        if ins.pc in targets:
            lines.append(f"L{ins.pc:x}:")
        lines += ["    {", "        if (!budget--) return Status::budget_exhausted;", f"        s.pc = {literal(ins.pc)};"]
        lines += ["        " + line for line in emit(ins, i == len(ir) - 1 or ir[i + 1].pc != ins.pc + 4, addresses, stop_calls, host_fill)]
        lines.append("    }")
    if has_return:
        lines += ["indirect:", "    if (target == return_address) return Status::returned;",
                  "    switch (target) {"]
        lines += [f"    case {literal(ins.pc)}: goto L{ins.pc:x};" for ins in ir]
        lines += ["    default: s.stop_target = target; return Status::bad_return;", "    }"]
    return "\n".join(lines + ["}", ""])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--base", type=lambda s: int(s, 0), default=0)
    parser.add_argument("--entry", type=lambda s: int(s, 0))
    parser.add_argument("--target", action="append", type=lambda s: int(s, 0), default=[])
    args = parser.parse_args()
    try:
        source = compile_block(args.input.read_bytes(), args.base, entry=args.entry, targets=args.target)
        with args.output.open("x", encoding="utf-8") as file:
            file.write(source)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")
