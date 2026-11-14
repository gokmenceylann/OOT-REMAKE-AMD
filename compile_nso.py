"""Compile a selected function from a verified, extracted NSO text segment."""
import argparse
from pathlib import Path

from a64_compile import compile_block
from verify_exefs import read_module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--base", type=lambda s: int(s, 0), default=0x80000000,
                        help="guest module base")
    parser.add_argument("--offset", type=lambda s: int(s, 0), required=True,
                        help="module-relative function address")
    parser.add_argument("--target-offset", type=lambda s: int(s, 0), action="append", default=[])
    args = parser.parse_args()
    try:
        metadata, segments, _ = read_module(args.module)
        base = args.base + metadata["segments"]["text"]["memory_offset"]
        source = compile_block(segments["text"], base, entry=args.base + args.offset,
                               targets=[args.base + target for target in args.target_offset])
        with args.output.open("x", encoding="utf-8") as output:
            output.write(source)
    except (OSError, ImportError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
