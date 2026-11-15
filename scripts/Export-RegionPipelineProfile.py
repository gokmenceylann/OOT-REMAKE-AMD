"""Export observed pipeline keys for a confirmed map from renderer logs."""
import argparse
from collections import Counter
import os
from pathlib import Path
import re
import tempfile

REGIONS = {"CastleTown": "Market", "HyruleField": "HyruleField", "TempleOfTime": "TempleOfTime"}
CAPABILITY = re.compile(r"vk: capability device=.*? vendor=0x([0-9a-f]+) deviceID=0x([0-9a-f]+) API=\S+ driver=0x([0-9a-f]+)\b", re.I)
TELEPORT = re.compile(r"\] cheats: teleport (?:child|adult) to (\w+) .*: request sent, result 0x1\s*$")
MAP = re.compile(r"\] map: (\w+) \((?:child|adult)\)\s*$")
PIPELINE = re.compile(r"\[hos Presentation Thread\] vk: graphics pipeline .*: SLOW build, (\d+) ms; pipeline_key=([0-9a-f]{16}) VkResult=0\b")

USE = re.compile(r"vk: region pipeline use (g|c) ([0-9a-f]{16})(?: ([0-9a-f]{16}))?\s*$")


def collect(lines, region, age=None):
    prefix = REGIONS[region]
    maps = {prefix, prefix + "_Child", prefix + "_Adult"}
    if age:
        maps = {prefix + "_" + age.capitalize()}
    device = None
    active = False
    pending = None
    keys = {}
    for line in lines:
        match = CAPABILITY.search(line)
        if match:
            identity = tuple(format(int(value, 16), "x") for value in match.groups())
            if device and device != identity:
                raise ValueError("The capture contains multiple Vulkan device identities.")
            device = identity
        match = TELEPORT.search(line)
        if match:
            active = False
            pending = {} if match[1] in maps else None
            continue
        match = MAP.search(line)
        if match:
            active = match[1] in maps
            if active and pending is not None:
                for key, duration in pending.items():
                    keys[key] = max(duration, keys.get(key, 0))
            pending = None
            continue
        if not active and pending is None:
            continue
        target = keys if active else pending
        match = PIPELINE.search(line)
        if match:
            duration, key = match.groups()
            target[key] = max(int(duration), target.get(key, 0))
            continue
        match = USE.search(line)
        if match:
            kind, key, variant = match.groups()
            if kind == "g" and variant is None:
                target.setdefault(key, 0)
            elif kind == "c" and variant:
                target.setdefault(f"c {key} {variant}", 0)
    if not device or not keys:
        raise ValueError("Expected a Vulkan device identity and pipeline keys for a confirmed region.")
    return device, keys


def format_profile(captures):
    device = captures[0][0]
    keys = {}
    frequency = Counter()
    for identity, observed in captures:
        if identity != device:
            raise ValueError("Captures must use the same Vulkan device and driver.")
        frequency.update(observed.keys())
        for key, duration in observed.items():
            keys[key] = max(duration, keys.get(key, 0))
    ordered = sorted(keys, key=lambda key: (-keys[key], not key.startswith("c "), -frequency[key], key))
    return "OOT_PIPELINE_REGION_1 " + " ".join(device) + "\n" + "\n".join(ordered) + "\n"


def profile(lines, region):
    return format_profile([collect(lines, region)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, action="append", type=Path)
    parser.add_argument("--cache-directory", required=True, type=Path)
    parser.add_argument("--region", required=True, choices=REGIONS)
    parser.add_argument("--age", choices=("child", "adult"))
    args = parser.parse_args()
    try:
        captures = []
        for path in args.log:
            with path.open(encoding="utf-8-sig", errors="replace") as capture:
                captures.append(collect(capture, args.region, args.age))
        data = format_profile(captures)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    target = args.cache_directory / f"hookshot_pipeline_region_{args.region}.txt"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="ascii", newline="\n", dir=target.parent, delete=False) as out:
            temporary = Path(out.name)
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    print(f"{len(data.splitlines()) - 1} pipeline keys: {target}")


if __name__ == "__main__":
    main()
