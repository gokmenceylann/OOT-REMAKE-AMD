"""Resolve ELF64 dynamic symbols between local NSO images."""
import argparse
from collections import Counter
from dataclasses import dataclass, field
import json
from pathlib import Path
from struct import pack_into, unpack_from

from map_exefs import MODULES, relocate

GNU_HASH = 0x6ffffef5
ABS64, GLOB_DAT, JUMP_SLOT = 257, 1025, 1026
SHN_ABS = 0xfff1


@dataclass
class Module:
    base: int
    image: bytearray
    report: dict
    tags: dict
    ranges: list
    bss: int
    tables: list
    symbols: list = field(default_factory=list)

    def check(self, offset, size):
        if not any(start <= offset <= end and size <= end - offset for start, end in self.ranges):
            raise ValueError(f"{self.report['module']}: metadata outside segment at {offset:#x}")

    def parse(self):
        address, strings, size = (self.tags.get(tag, 0) for tag in (6, 5, 10))
        if self.tags.get(11) != 24 or not address or not strings or not size:
            raise ValueError("invalid symbol table metadata")
        self.check(strings, size)
        if GNU_HASH not in self.tags:
            raise ValueError("GNU hash table required")
        start = self.tags[GNU_HASH]
        self.check(start, 16)
        buckets, first, bloom, _ = unpack_from("<IIII", self.image, start)
        bucket_start = start + 16 + 8 * bloom
        self.check(bucket_start, 4 * buckets)
        end = max((unpack_from("<I", self.image, bucket_start + i * 4)[0]
                   for i in range(buckets)), default=0)
        if end and end < first:
            raise ValueError("GNU hash bucket precedes symbol offset")
        chain = bucket_start + 4 * buckets
        if end:
            while True:
                entry = chain + (end - first) * 4
                self.check(entry, 4)
                end += 1
                if unpack_from("<I", self.image, entry)[0] & 1:
                    break
        count = max(first, end)
        self.check(address, count * 24)
        for index in range(count):
            offset, info, visibility, section, value, _ = unpack_from(
                "<IBBHQQ", self.image, address + index * 24)
            if offset >= size:
                raise ValueError("symbol name offset outside string table")
            end = self.image.find(b"\0", strings + offset, strings + size)
            if end < 0:
                raise ValueError("unterminated symbol name")
            name = bytes(self.image[strings + offset:end])
            self.symbols.append((name, info >> 4, visibility & 3, section, value))


def symbol_address(module, section, value):
    return value if section == SHN_ABS else module.base + value


def resolve(symbol, module, exports):
    name, binding, _, section, value = symbol
    if section:
        return symbol_address(module, section, value)
    match = exports.get(name)
    if match:
        return match[1]
    return 0 if binding == 2 else None


def link(root):
    if not (root / "main").is_file():
        raise ValueError("expected extracted ExeFS containing main")
    modules = []
    exports = {}
    # Deterministic local scope. No symbol versioning or external libraries.
    for name in ("rtld", *(name for name in MODULES if name != "rtld")):
        path = root / name
        if path.is_file():
            base = 0x80000000 + len(modules) * 0x20000000
            module = Module(base, *relocate(path, base, metadata=True))
            module.parse()
            modules.append(module)
            for symbol, binding, visibility, section, value in module.symbols:
                if not symbol or not section or binding not in (1, 2) or visibility not in (0, 3):
                    continue
                previous = exports.get(symbol)
                if previous is None or (previous[0] == 2 and binding == 1):
                    exports[symbol] = binding, symbol_address(module, section, value)
    for module in modules:
        missing, counts = Counter(), Counter()
        applied = set()
        data_start, data_end = module.ranges[2]
        for start, end in sorted(set(module.tables)):
            for offset in range(start, end, 24):
                target, packed, addend = unpack_from("<QQq", module.image, offset)
                kind, index = packed & 0xffffffff, packed >> 32
                if kind not in (ABS64, GLOB_DAT, JUMP_SLOT):
                    if kind not in (0, 256, 1027):
                        counts[f"unsupported_{kind}"] += 1
                    continue
                if index >= len(module.symbols) or target % 8 or target in applied or not (
                    data_start <= target <= data_end + module.bss - 8
                ):
                    raise ValueError(f"invalid symbol relocation at {target:#x}")
                applied.add(target)
                address = resolve(module.symbols[index], module, exports)
                if address is None:
                    missing[module.symbols[index][0].decode("utf-8", "backslashreplace")] += 1
                    continue
                value = address + addend
                if not 0 <= value < (1 << 64):
                    raise ValueError(f"overflowing symbol relocation at {target:#x}")
                pack_into("<Q", module.image, target, value)
                counts["applied"] += 1
        yield dict(module=module.report["module"], applied=counts.pop("applied", 0),
                   unsupported=dict(counts), missing=dict(missing))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exefs", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(list(link(args.exefs)), indent=2))
    except (OSError, ValueError, ImportError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
