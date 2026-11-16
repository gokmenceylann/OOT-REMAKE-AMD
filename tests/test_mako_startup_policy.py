"""Check the compiled Mako startup policy with the Release define set."""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--cxx", required=True)
    args = parser.parse_args()

    source = (args.source / "gpu/vk/vk_draw.cpp").read_text(encoding="utf-8")
    start = source.index("bool precompile_wanted() {")
    stop = source.index("\n}", start) + len("\n}")
    fixture = """
#include <cstdlib>
#include <cstring>
static const char* override_value;
static const char* lookup(const char* key) {
    return std::strcmp(key, "RX_VK_PRECOMPILE") == 0 ? override_value : nullptr;
}
#define getenv lookup
""" + source[start:stop] + """
int main() {
    if (precompile_wanted()) return 1;
    override_value = "1";
    if (!precompile_wanted()) return 2;
    override_value = "0";
    if (precompile_wanted()) return 3;
    return 0;
}
"""
    with tempfile.TemporaryDirectory(prefix="mako-startup-policy-") as directory:
        workspace = Path(directory)
        test = workspace / "startup.cpp"
        exe = workspace / "startup.exe"
        test.write_text(fixture, encoding="utf-8")
        subprocess.run([args.cxx, "-std=c++20", "-DHOOKSHOT_RELEASE", str(test), "-o", str(exe)], check=True)
        subprocess.run([str(exe)], check=True, timeout=10)
    print("PASS: Release defaults to on-demand; RX_VK_PRECOMPILE=1/0 overrides it")


if __name__ == "__main__":
    main()
