"""Verify payloads of locally extracted, plain or LZ4 NSO0 modules."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from inspect_exefs import inspect_module, MODULES


def verify_module(path: Path) -> dict:
    info = inspect_module(path)
    flags = int(info["flags"], 16)
    if flags & 0x80:
        raise ValueError(f"{path.name}: ZBIC payload is unsupported; use a locally unpacked NSO")
    with path.open("rb") as stream:
        header = stream.read(0x100)
        for index, (name, segment) in enumerate(info["segments"].items()):
            decoded = segment["decoded_bytes"]
            stored = segment["stored_bytes"]
            if max(decoded, stored) > 256 * 1024 * 1024:
                raise ValueError(f"{path.name}: {name} exceeds the verifier's 256 MiB segment limit")
            stream.seek(segment["file_offset"])
            payload = stream.read(stored)
            if len(payload) != stored:
                raise ValueError(f"{path.name}: short read for {name}")
            if segment["compressed_flag"]:
                import lz4.block
                try:
                    payload = lz4.block.decompress(payload, uncompressed_size=decoded)
                except lz4.block.LZ4BlockError as exc:
                    raise ValueError(f"{path.name}: invalid LZ4 {name}") from exc
            if len(payload) != decoded:
                raise ValueError(f"{path.name}: incorrect decoded size for {name}")
            if flags & (8 << index):
                start = 0xA0 + 32 * index
                if hashlib.sha256(payload).digest() != header[start:start + 32]:
                    raise ValueError(f"{path.name}: SHA-256 mismatch for {name}")
                segment["hash_status"] = "verified"
            else:
                segment["hash_status"] = "not provided"
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exefs", type=Path)
    args = parser.parse_args()
    try:
        if not (args.exefs / "main").is_file():
            raise ValueError("expected extracted ExeFS containing main")
        print(json.dumps([verify_module(args.exefs / name) for name in MODULES
                          if (args.exefs / name).is_file()], indent=2))
    except (ValueError, OSError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
