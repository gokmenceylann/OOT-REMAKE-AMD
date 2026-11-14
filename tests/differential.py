"""Assemble the A64 fixture, compare it with Unicorn, and run the x64 result."""
import argparse
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn import arm64_const as arm

ROOT = Path(__file__).resolve().parents[1]
BASE, RAM, RETURN = 0x1000, 0x2000, 0x3000
REGS = [getattr(arm, f"UC_ARM64_REG_X{i}") for i in range(31)] + [arm.UC_ARM64_REG_SP]


def oracle(code, x0):
    cpu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    cpu.mem_map(BASE, 0x3000)
    cpu.mem_write(BASE, code)
    cpu.reg_write(REGS[0], x0)
    cpu.reg_write(REGS[1], RAM + 16)
    cpu.reg_write(REGS[30], RETURN)
    cpu.reg_write(REGS[31], RAM)
    cpu.emu_start(BASE, RETURN, count=64)
    if cpu.reg_read(arm.UC_ARM64_REG_PC) != RETURN:
        raise RuntimeError("guest did not return")
    regs = [cpu.reg_read(reg) for reg in REGS]
    flags = cpu.reg_read(arm.UC_ARM64_REG_NZCV) >> 28
    return regs, flags, bytes(cpu.mem_read(RAM, 32))


def check(code, initial):
    regs, flags, memory = oracle(code, initial)
    regs = ", ".join(f"{value}ULL" for value in regs)
    memory = ", ".join(map(str, memory))
    return f"""
    {{
        A64State s;
        std::array<std::uint8_t, 32> ram{{}};
        s.memory = ram;
        s.memory_base = {RAM};
        s.x[0] = {initial}ULL;
        s.x[1] = {RAM + 16};
        s.x[30] = {RETURN};
        s.x[31] = {RAM};
        if (run_a64(s, 64, {RETURN}) != Status::returned) return 1;
        if (s.x != std::array<std::uint64_t, 32>{{{regs}}}) return 2;
        if ((8 * s.n + 4 * s.z + 2 * s.c + s.v) != {flags}) return 3;
        if (ram != std::array<std::uint8_t, 32>{{{memory}}}) return 4;
    }}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llvm-bin", type=Path)
    args = parser.parse_args()
    env = os.environ.copy()
    suffix = ".exe" if os.name == "nt" else ""
    if args.llvm_bin:
        env["PATH"] = str(args.llvm_bin.resolve()) + os.pathsep + env["PATH"]

    def run(*command):
        executable = shutil.which(command[0], path=env['PATH']) or command[0]
        subprocess.run((executable, *command[1:]), env=env, check=True)

    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        obj, binary, cpp = (temp / name for name in ("fixture.o", "fixture.bin", "generated.cpp"))
        run("clang" + suffix, "--target=aarch64-none-elf", "-c", str(ROOT / "tests/tests_a64.S"), "-o", str(obj))
        run("llvm-objcopy" + suffix, "-O", "binary", "--only-section=.text", str(obj), str(binary))
        run(sys.executable, str(ROOT / "a64_compile.py"), str(binary), str(cpp), "--base", hex(BASE))
        cases = (0, 1, 2, 0x80000000, 0x100000103, 0xffffffffffffffff)
        code = binary.read_bytes()
        harness = temp / "oracle.cpp"
        harness.write_text('#include "a64_state.hpp"\nint main() {\n' +
                           "".join(check(code, case) for case in cases) + "}\n", encoding="utf-8")
        for source in (harness, ROOT / "tests/tests_a64.cpp"):
            executable = temp / (source.stem + suffix)
            run("clang++" + suffix, "-std=c++20", "-O2", "-Wall", "-Wextra", "-Werror",
                "-I", str(ROOT), str(cpp), str(source), "-o", str(executable))
            run(str(executable))
        print(f"{len(cases)} Unicorn comparisons passed (registers, flags and memory); fault tests passed")


if __name__ == "__main__":
    main()
