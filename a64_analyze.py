"""Discover direct control flow from explicit A64 function entry points."""
import argparse
import json
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM, CS_GRP_JUMP
from capstone.arm64 import ARM64_OP_IMM

def analyze(code, entries, base):
    decoder = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    decoder.detail = True
    results = {}
    pending = set(entries)
    while pending:
        entry = min(pending)
        pending.remove(entry)
        if entry in results:
            continue
        blocks, calls, indirect, exits = set(), set(), set(), set()
        todo = [entry]
        while todo:
            pc = todo.pop()
            if pc in blocks:
                continue
            offset = pc - base
            if offset < 0 or offset % 4 or offset + 4 > len(code):
                exits.add(pc)
                continue
            ins = next(decoder.disasm(code[offset:offset + 4], pc), None)
            if ins is None:
                exits.add(pc)
                continue
            blocks.add(pc)
            op = ins.mnemonic
            if op in ("ret", "retab", "retaa", "brk", "udf"):
                continue
            if op.startswith(("br", "blr")):
                indirect.add(pc)
                if op.startswith("blr"):
                    todo.append(pc + 4)
                continue
            if op == "bl":
                target = ins.operands[0].imm
                calls.add(target)
                if 0 <= target - base <= len(code) - 4 and not (target - base) % 4:
                    pending.add(target)
            elif ins.group(CS_GRP_JUMP):
                if not ins.operands or ins.operands[-1].type != ARM64_OP_IMM:
                    indirect.add(pc)
                    continue
                todo.append(ins.operands[-1].imm)
                if op == "b":
                    continue
            todo.append(pc + 4)
        results[entry] = dict(instructions=sorted(blocks), calls=sorted(calls),
                              indirect_sites=sorted(indirect), exits=sorted(exits))
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", type=Path)
    parser.add_argument("--base", type=lambda x: int(x, 0), default=0)
    parser.add_argument("--entry", type=lambda x: int(x, 0), action="append")
    args = parser.parse_args()
    print(json.dumps(analyze(args.text.read_bytes(), args.entry or [args.base], args.base), indent=2))
