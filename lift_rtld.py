"""Generate a Windows x64 entry probe using the shared AArch64 backend."""
import argparse
import hashlib
from pathlib import Path

from a64_compile import compile_block
from verify_exefs import read_module

BASE = 0x80000000
FILL_TEXT_SHA256 = "efcc6ebfac7d2a23068bff8a8b451e3556c9837e811e5f20b2bd7bbd2ef23f52"


def generate(code, fill_window=None):
    if fill_window and hashlib.sha256(code).hexdigest() != FILL_TEXT_SHA256:
        raise ValueError("host fill is supported only for the verified rtld text revision")
    fill = (BASE + 0x30, BASE + 0x21e0) if fill_window else None
    start, size = fill_window or (0, 0)
    return compile_block(code, BASE, stop_calls=True, host_fill=fill) + f"""
#include <cstdio>
#include <vector>
int main() {{
    std::vector<std::uint8_t> memory({size}, 0xa5);
    A64State state;
    state.memory_base = {start}ULL;
    state.memory = memory;
    const auto result = run_a64(state, 64);
    std::printf("status %d, stopped at guest %llx, target %llx\\n",
                int(result), static_cast<unsigned long long>(state.pc),
                static_cast<unsigned long long>(state.stop_target));
    return result == Status::external_branch ? 0 : 1;
}}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exefs", type=Path)
    parser.add_argument("cpp", type=Path)
    parser.add_argument("--host-fill", action="store_true")
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
