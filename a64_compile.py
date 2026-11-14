"""Ahead-of-time compiler for a bounded integer AArch64 subset."""
import argparse
from dataclasses import dataclass
from pathlib import Path
import re

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
LOGICAL = {"and", "ands", "orr", "eor", "tst"}
MEMORY = {
    "ldr": 0, "ldur": 0, "str": 0, "stur": 0,
    "ldrb": 1, "ldurb": 1, "strb": 1, "sturb": 1,
    "ldrh": 2, "ldurh": 2, "strh": 2, "sturh": 2,
}


def lower(op, text):
    tokens = text.split(", ") if text else []
    if op in ARITHMETIC | LOGICAL:
        compare = op in ("cmp", "cmn", "tst")
        if len(tokens) == (2 if compare else 3):
            lhs, rhs = register(tokens[-2]), value(tokens[-1])
            dest = Reg(31, lhs.width, True) if compare else register(tokens[0])
            if dest.width == lhs.width and (not isinstance(rhs, Reg) or rhs.width == lhs.width):
                return dest, lhs, rhs
    elif op == "mov" and len(tokens) == 2:
        dest, src = register(tokens[0]), value(tokens[1])
        if not isinstance(src, Reg) or src.width == dest.width:
            return dest, src
    elif op in MEMORY:
        match = re.fullmatch(r"(\w+), \[(\w+)(?:, (#-?(?:0x[0-9a-f]+|[0-9]+)))?\]", text)
        if match:
            dest, base, offset = match.groups()
            dest, base = register(dest), register(base)
            if base.width == 64 and not base.zero:
                return dest, Mem(base, immediate(offset) if offset else 0)
    elif op in ("b", "bl") or (op.startswith("b.") and op[2:] in CONDITIONS):
        if len(tokens) == 1:
            return (immediate(tokens[0]),)
    elif op in ("cbz", "cbnz") and len(tokens) == 2:
        return register(tokens[0]), immediate(tokens[1])
    elif op in ("adr", "adrp") and len(tokens) == 2:
        return register(tokens[0]), immediate(tokens[1])
    elif op == "ret" and len(tokens) <= 1:
        return (register(tokens[0] if tokens else "x30"),)
    elif op == "nop" and not tokens:
        return ()
    raise ValueError(f"unsupported form: {op} {text}")


def decode(code, base=0):
    if not code or len(code) % 4 or base % 4 or not 0 <= base <= (1 << 64) - len(code) - 4:
        raise ValueError("expected aligned guest base and complete instruction words")
    decoder = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    result = []
    for offset in range(0, len(code), 4):
        pc = base + offset
        ins = next(decoder.disasm(code[offset:offset + 4], pc), None)
        if ins is None:
            raise ValueError(f"{pc:#x}: invalid A64 encoding")
        try:
            args = lower(ins.mnemonic, ins.op_str)
        except ValueError as exc:
            raise ValueError(f"{pc:#x}: {exc}") from exc
        result.append(Instruction(pc, ins.mnemonic, args))
    addresses = {ins.pc for ins in result}
    for ins in result:
        if ins.op in ("b", "bl", "cbz", "cbnz") or ins.op.startswith("b."):
            if ins.args[-1] not in addresses:
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


def emit(ins, last):
    op, args = ins.op, ins.args
    out = []
    if op in ARITHMETIC | LOGICAL:
        dest, lhs, rhs = args
        width = dest.width
        operator = ("+" if op in ("add", "adds", "cmn") else "-" if op in ("sub", "subs", "cmp")
                    else "&" if op in ("and", "ands", "tst") else "|" if op == "orr" else "^")
        out.extend([f"const auto a = std::uint{width}_t({read(lhs)});",
                    f"const auto b = std::uint{width}_t({read(rhs)});",
                    f"const auto r = std::uint{width}_t(a {operator} b);"])
        if op in ("adds", "cmn", "subs", "cmp", "ands", "tst"):
            out.append(f"s.set_flags(a, b, r, {width}, '{operator}');")
        out += write(dest, "r")
        if not dest.zero or op in ("adds", "cmn", "subs", "cmp", "ands", "tst"):
            return out + (["return Status::fell_through;"] if last else [])
        out = []
    elif op in ("mov", "adr", "adrp"):
        out += write(args[0], read(args[1]))
    elif op in MEMORY:
        dest, mem = args
        size = MEMORY[op] or dest.width // 8
        out.append(f"const auto address = {read(mem.base)} + {literal(mem.offset)};")
        if op.startswith("ld"):
            out += ["std::uint64_t data;", f"if (!s.load(address, {size}, data)) return Status::memory_fault;"]
            out += write(dest, "data")
        else:
            out.append(f"if (!s.store(address, {size}, {read(dest)})) return Status::memory_fault;")
    elif op == "b":
        return [f"goto L{args[0]:x};"]
    elif op == "bl":
        return [f"s.x[30] = {literal(ins.pc + 4)};", f"goto L{args[0]:x};"]
    elif op == "ret":
        return [f"target = {read(args[0])};", "goto indirect;"]
    elif op.startswith("b."):
        expr = re.sub(r"\b[nzcv]\b", lambda m: "s." + m[0], CONDITIONS[op[2:]])
        out.append(f"if ({expr}) goto L{args[0]:x};")
    elif op in ("cbz", "cbnz"):
        comparison = "==" if op == "cbz" else "!="
        out.append(f"if ({read(args[0])} {comparison} 0) goto L{args[1]:x};")
    if last:
        out.append("return Status::fell_through;")
    return out


def compile_block(code, base=0):
    ir = decode(code, base)
    has_return = any(ins.op == "ret" for ins in ir)
    lines = ['#include "a64_state.hpp"', "Status run_a64(A64State& s, std::uint64_t budget) {"]
    if has_return:
        lines.append("    std::uint64_t target = 0;")
    targets = {ins.pc for ins in ir} if has_return else {
        ins.args[-1] for ins in ir if ins.op in ("b", "bl", "cbz", "cbnz") or ins.op.startswith("b.")
    }
    for i, ins in enumerate(ir):
        if ins.pc in targets:
            lines.append(f"L{ins.pc:x}:")
        lines += ["    {", "        if (!budget--) return Status::budget_exhausted;"]
        lines += ["        " + line for line in emit(ins, i == len(ir) - 1)]
        lines.append("    }")
    if has_return:
        lines += ["indirect:", "    if (target == A64State::return_to_host) return Status::returned;",
                  "    switch (target) {"]
        lines += [f"    case {literal(ins.pc)}: goto L{ins.pc:x};" for ins in ir]
        lines += ["    default: return Status::bad_return;", "    }"]
    return "\n".join(lines + ["}", ""])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--base", type=lambda s: int(s, 0), default=0)
    args = parser.parse_args()
    try:
        source = compile_block(args.input.read_bytes(), args.base)
        with args.output.open("x", encoding="utf-8") as file:
            file.write(source)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")
