"""Build and execute a selected RTLD function against its mapped NSO image."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

from a64_compile import compile_block
from map_exefs import relocate
from verify_exefs import read_module

ROOT = Path(__file__).resolve().parent
BASE = 0x80000000


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rtld", type=Path)
    p.add_argument("--clang", required=True, type=Path)
    args = p.parse_args()
    if hashlib.sha256(args.rtld.read_bytes()).hexdigest() != "219f25ef4a64a704e86dacfeb25d9e8977045f2145e629268b94baf34d5e0bbe":
        p.error("the bootstrap addresses are pinned to the tested RTLD revision")
    image, _, tags, ranges, _, _ = relocate(args.rtld, BASE, metadata=True)
    start, end = ranges[0]
    if start != 0 or image[0x4008:0x4010] == bytes(8) or 7 not in tags:
        p.error("unexpected RTLD layout for the local bootstrap probe")
    source = compile_block(bytes(image[start:end]), BASE + start, entry=BASE + 0x100)
    env = os.environ.copy()
    env["PATH"] = str(args.clang.resolve().parent) + os.pathsep + env["PATH"]
    with tempfile.TemporaryDirectory() as folder:
        tmp = Path(folder)
        cpp, data, exe = [tmp / name for name in ("rtld.cpp", "memory.bin", "rtld.exe")]
        # This boot routine performs its own relocation. Use original segment bytes.
        info, contents, _ = read_module(args.rtld)
        for name, segment in info["segments"].items():
            offset = segment["memory_offset"]
            image[offset:offset + len(contents[name])] = contents[name]
        data.write_bytes(image)
        cpp.write_text(source + """
#include <cstdio>
#include <fstream>
#include <iterator>
#include <vector>
int main(int argc, char** argv) {
    if (argc != 2) return 1;
    std::ifstream input(argv[1], std::ios::binary);
    if (!input) return 1;
    std::vector<std::uint8_t> image((std::istreambuf_iterator<char>(input)), {});
    A64State state;
    state.memory_base = 0x80000000;
    state.memory = image;
    state.x[0] = 0x80000000;
    state.x[1] = 0x80004008;
    const auto status = run_a64(state, 1000000);
    std::printf("RTLD status=%d pc=%llx unresolved=%llx\\n", int(status),
                static_cast<unsigned long long>(state.pc),
                static_cast<unsigned long long>(state.stop_target));
    return status == Status::returned ? 0 : 2;
}
""", encoding="utf-8")
        subprocess.run([str(args.clang.resolve()), "-std=c++20", "-O2", "-I", str(ROOT),
                        str(cpp), "-o", str(exe)], check=True, env=env)
        subprocess.run([str(exe), str(data)], check=True, env=env)


if __name__ == "__main__":
    main()
