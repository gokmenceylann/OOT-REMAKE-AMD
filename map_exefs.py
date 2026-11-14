"""Map local NSO modules and apply symbol-free AArch64 relocations."""
import argparse
from collections import Counter
import json
from pathlib import Path
from struct import unpack_from, pack_into

from inspect_exefs import MODULES
from verify_exefs import read_module

RELA, RELASZ, RELAENT, JMPREL, PLTRELSZ, PLTREL = 7, 8, 9, 23, 2, 20
RELATIVE = 1027


def decode_relr(entries):
    cursor = None
    for index in range(0, len(entries), 8):
        word = unpack_from("<Q", entries, index)[0]
        if word & 1 == 0:
            if word % 8:
                raise ValueError("unaligned RELR entry")
            yield word
            cursor = word + 8
        else:
            if cursor is None:
                raise ValueError("RELR bitmap has no base entry")
            bits = word >> 1
            while bits:
                lowest = bits & -bits
                yield cursor + (lowest.bit_length() - 1) * 8
                bits ^= lowest
            cursor += 63 * 8


def relocate(path, base, metadata=False):
    info, contents, bss = read_module(path)
    ranges = [(part["memory_offset"], part["memory_offset"] + len(contents[name]))
              for name, part in info["segments"].items()]
    text, _, (data_start, data_end) = ranges
    image_end = max(*(end for _, end in ranges), data_end + bss)
    if image_end > 512 * 1024 * 1024 or not 0 <= base < (1 << 64) - image_end:
        raise ValueError("module image or guest base exceeds bounds")
    image = bytearray(image_end)
    for (start, end), payload in zip(ranges, contents.values()):
        image[start:end] = payload

    def require_read(offset, size):
        if not any(start <= offset <= end and size <= end - offset
                   for start, end in ranges):
            raise ValueError(f"metadata outside backed segment at {offset:#x}")

    require_read(text[0], 8)
    mod = text[0] + unpack_from("<i", image, text[0] + 4)[0]
    require_read(mod, 8)
    if image[mod:mod + 4] != b"MOD0":
        raise ValueError("MOD0 header not found")
    dynamic = mod + unpack_from("<i", image, mod + 4)[0]
    tags = {}
    for offset in range(dynamic, dynamic + 4096 * 16, 16):
        require_read(offset, 16)
        tag, value = unpack_from("<qQ", image, offset)
        if tag == 0:
            break
        tags[tag] = value
    else:
        raise ValueError("dynamic table has no terminator")

    tables = []
    for address_tag, size_tag in ((RELA, RELASZ), (JMPREL, PLTRELSZ)):
        size = tags.get(size_tag, 0)
        if size:
            address = tags.get(address_tag)
            if address is None or size % 24 or tags.get(RELAENT, 24) != 24:
                raise ValueError("invalid RELA metadata")
            if address_tag == JMPREL and tags.get(PLTREL) != RELA:
                raise ValueError("PLT uses a non-RELA relocation table")
            require_read(address, size)
            tables.append((address, address + size))
    patches, pending = {}, Counter()
    def patch(target, value):
        if target % 8 or not data_start <= target <= data_end + bss - 8:
            raise ValueError(f"invalid relocation target at {target:#x}")
        if target in patches or not 0 <= value < 1 << 64:
            raise ValueError(f"duplicate or overflowing relocation at {target:#x}")
        patches[target] = value

    for start, end in sorted(set(tables)):
        for offset in range(start, end, 24):
            target, packed, addend = unpack_from("<QQq", image, offset)
            kind, symbol = packed & 0xFFFFFFFF, packed >> 32
            if kind == RELATIVE:
                value = base + addend
                if symbol:
                    raise ValueError("relative relocation unexpectedly references a symbol")
                patch(target, value)
            elif kind not in (0, 256):
                pending[kind] += 1
    rela_count = len(patches)
    relr_size = tags.get(35, 0)
    if relr_size:
        address = tags.get(36)
        if address is None or tags.get(37) != 8 or relr_size % 8:
            raise ValueError("invalid RELR metadata")
        require_read(address, relr_size)
        for target in decode_relr(memoryview(image)[address:address + relr_size]):
            if not data_start <= target <= data_end + bss - 8:
                raise ValueError(f"invalid RELR target at {target:#x}")
            patch(target, base + unpack_from("<Q", image, target)[0])
    for target, value in patches.items():
        pack_into("<Q", image, target, value)
    report = dict(module=path.name, relative_rela_applied=rela_count, relative_relr_applied=len(patches) - rela_count,
                       unresolved_rela=dict(pending),
                       other_table_tags=[tag for tag in (17, 18, 19) if tag in tags])
    if metadata:
        return image, report, tags, ranges, bss, tables
    return image, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exefs", type=Path)
    args = parser.parse_args()
    try:
        if not (args.exefs / "main").is_file():
            raise ValueError("expected extracted ExeFS containing main")
        results = []
        for name in MODULES:
            path = args.exefs / name
            if path.is_file():
                _, result = relocate(path, 0x80000000 + len(results) * 0x20000000)
                results.append(result)
        print(json.dumps(results, indent=2))
    except (OSError, ValueError, ImportError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
