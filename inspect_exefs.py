"""Inspect already extracted ExeFS NSO headers without exporting game data."""
import argparse
import json
from pathlib import Path
import struct

MODULES = ("main", "rtld", "sdk", *(f"subsdk{i}" for i in range(13)))
SEGMENTS = ("text", "rodata", "data")


def inspect_module(path: Path) -> dict:
    with path.open("rb") as stream:
        header = stream.read(0x100)
        size = stream.seek(0, 2)
    if len(header) != 0x100 or header[:4] != b"NSO0":
        raise ValueError(f"{path.name}: expected an NSO0 header")
    flags = struct.unpack_from("<I", header, 12)[0]
    segments = {}
    file_ranges, memory_ranges = [], []
    for i, name in enumerate(SEGMENTS):
        offset, address, decoded = struct.unpack_from("<III", header, 0x10 + 16 * i)
        compressed = bool(flags & (1 << i))
        stored = struct.unpack_from("<I", header, 0x60 + 4 * i)[0] if compressed else decoded
        if offset > size or stored > size - offset or (stored and offset < len(header)):
            raise ValueError(f"{path.name}: {name} exceeds file bounds")
        if decoded and address + decoded > 1 << 32:
            raise ValueError(f"{path.name}: {name} exceeds the module address range")
        if stored:
            file_ranges.append((offset, offset + stored))
        if decoded:
            memory_ranges.append((address, address + decoded))
        segments[name] = dict(file_offset=offset, memory_offset=address, stored_bytes=stored,
                              decoded_bytes=decoded, compressed_flag=compressed)
    for label, ranges in (("file", file_ranges), ("memory", memory_ranges)):
        ranges.sort()
        if any(end > following for (_, end), (following, _) in zip(ranges, ranges[1:])):
            raise ValueError(f"{path.name}: overlapping {label} segments")
    return dict(module=path.name, flags=f"0x{flags:08x}", segments=segments)


def inspect_exefs(root: Path) -> list[dict]:
    if not (root / "main").is_file():
        raise ValueError("expected an already extracted ExeFS directory containing main")
    return [inspect_module(root / name) for name in MODULES if (root / name).is_file()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exefs", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_exefs(args.exefs), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
