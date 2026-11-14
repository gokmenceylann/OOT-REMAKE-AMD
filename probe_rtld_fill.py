"""Compare the local rtld startup call with a bounded host memory fill.

Unicorn is a test oracle only. The host replacement runs on a bytearray.
"""
import argparse
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_PROT_READ, UC_PROT_EXEC
from unicorn.arm64_const import UC_ARM64_REG_PC, UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2, UC_ARM64_REG_X30

from verify_exefs import read_module

CODE_BASE = 0x80000000
DATA_BASE = 0x90000000
PAGE = 4096


def host_fill(memory, offset, value, length):
    if offset < 0 or length < 0 or offset > len(memory) or length > len(memory) - offset:
        raise ValueError("fill outside guest memory")
    memory[offset:offset + length] = bytes([value & 255]) * length
    return offset


def compare(code, entry, length, value):
    if entry % 4 or not 0 <= entry <= len(code) - 4:
        raise ValueError("callee entry outside text")
    if length < 0 or length > PAGE - 64:
        raise ValueError("test fill exceeds the isolated guest page")
    guest = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mapped = (len(code) + PAGE - 1) // PAGE * PAGE
    guest.mem_map(CODE_BASE, mapped)
    guest.mem_write(CODE_BASE, code)
    guest.mem_protect(CODE_BASE, mapped, UC_PROT_READ | UC_PROT_EXEC)
    guest.mem_map(DATA_BASE, PAGE)
    expected = bytearray([0xA5] * PAGE)
    guest.mem_write(DATA_BASE, bytes(expected))
    sentinel = CODE_BASE + mapped
    guest.reg_write(UC_ARM64_REG_X0, DATA_BASE + 32)
    guest.reg_write(UC_ARM64_REG_X1, value)
    guest.reg_write(UC_ARM64_REG_X2, length)
    guest.reg_write(UC_ARM64_REG_X30, sentinel)
    guest.emu_start(CODE_BASE + entry, sentinel, timeout=1_000_000, count=30_000)
    if guest.reg_read(UC_ARM64_REG_PC) != sentinel:
        raise ValueError("guest function did not return within the probe budget")
    expected_return = DATA_BASE + host_fill(expected, 32, value, length)
    if guest.mem_read(DATA_BASE, PAGE) != expected or guest.reg_read(UC_ARM64_REG_X0) != expected_return:
        raise ValueError(f"guest routine differs from memory fill for length {length}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rtld", type=Path)
    parser.add_argument("--entry", type=lambda value: int(value, 0), required=True)
    args = parser.parse_args()
    code = read_module(args.rtld)[1]["text"]
    cases = ((0, 0), (1, 0x153), (3, 0xff), (8, 1), (16, 0x5a), (64, 7), (0x108, 0))
    for length, value in cases:
        compare(code, args.entry, length, value)
    print(f"{len(cases)} guest/host memory-fill cases matched, including return values")


if __name__ == "__main__":
    main()
