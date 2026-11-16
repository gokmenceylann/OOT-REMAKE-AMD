"""Exercise the production Windows pipeline-cache commit policy without memory pressure."""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--cxx", required=True)
    args = parser.parse_args()

    renderer = args.source / "gpu/vk"
    draw = (renderer / "vk_draw.cpp").read_text(encoding="utf-8")
    start = draw.index("bool pipeline_cache_import_allowed(")
    stop = draw.index("\n}", start) + 2
    for function, args_text in (("size_t play_files_merge()", "path, bytes"),
                                ("void pcache_init()", "pcache_path, data.size()")):
        body = draw[draw.index(function):]
        body = body[:body.index("\n}")]
        assert 0 <= body.index(f"pipeline_cache_import_allowed({args_text})") < body.index("vkCreatePipelineCache(")

    fixture = """
#include <cstdint>
#include <string>
#include "pipeline_cache_budget.h"
using mkwvk::pipeline_cache_fits_commit;
struct MEMORYSTATUSEX {
    unsigned dwLength;
    uint64_t ullTotalPageFile, ullAvailPageFile;
};
static uint64_t total, available;
static bool measured = true;
static bool GlobalMemoryStatusEx(MEMORYSTATUSEX* info) {
    if (info->dwLength != sizeof(*info)) return false;
    info->ullTotalPageFile = total;
    info->ullAvailPageFile = available;
    return measured;
}
template<class... Args> void logf(const char*, Args...) {}
""" + draw[start:stop] + """
int main() {
    constexpr uint64_t GiB = 1ull << 30;
    total = 16 * GiB;
    available = 6 * GiB;
    if (!pipeline_cache_import_allowed("main", GiB)) return 1;
    if (pipeline_cache_import_allowed("large", GiB + 1)) return 2;
    available = 4 * GiB;
    if (pipeline_cache_import_allowed("play", 1)) return 3;
    available = 17 * GiB;
    if (pipeline_cache_import_allowed("invalid", 1)) return 4;
    measured = false;
    available = 8 * GiB;
    if (pipeline_cache_import_allowed("unmeasured", 1)) return 5;
    return 0;
}
"""
    with tempfile.TemporaryDirectory(prefix="mako-cache-commit-") as directory:
        workspace = Path(directory)
        test = workspace / "commit.cpp"
        exe = workspace / "commit.exe"
        test.write_text(fixture, encoding="utf-8")
        subprocess.run([args.cxx, "-std=c++20", "-I", str(renderer), str(test), "-o", str(exe)], check=True)
        subprocess.run([str(exe)], check=True, timeout=10)
    print("PASS: main and play caches check commit before driver import; boundary and missing measurement handled")


if __name__ == "__main__":
    main()
