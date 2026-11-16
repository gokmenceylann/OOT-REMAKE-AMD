"""Compile the actual opt-in texture profile against a deterministic clock."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--cxx", required=True)
    args = parser.parse_args()
    source = (args.source / "gpu/vk/vk_draw.cpp").read_text(encoding="utf-8")
    first = source.index("enum TextureDetail {")
    last = source.index("\nbool no_a2c()", first)
    fixture = """
#include <array>
#include <cstdint>
#include <cstdlib>
#include <thread>
static bool env_on(const char* key) { return std::getenv(key) != nullptr; }
thread_local int64_t fake_ns = 0;
static int64_t prof_now() { return fake_ns; }
static unsigned logged = 0;
template<class... Args> static void logf(const char*, Args...) { ++logged; }
""" + source[first:last] + """
int main() {
    for (unsigned i = 0; i < 33; ++i) {
        TextureDetailScope view(TD_VIEW);
        fake_ns += 200;
        {
            TextureDetailScope prep(TD_PREPARE);
            fake_ns += 300;
        }
    }
    std::thread other([] {
        TextureDetailScope sampler(TD_SAMPLER);
        fake_ns += 100;
    });
    other.join();
    const auto view = texture_detail[TD_VIEW];
    const auto prep = texture_detail[TD_PREPARE];
    if (texture_detail[TD_SAMPLER].calls) return 1;
    if (texture_detail_on) {
        if (view.calls != 33 || view.samples != 3 || view.ns != 1500) return 2;
        if (prep.calls != 33 || prep.samples != 3 || prep.ns != 900) return 3;
    } else if (view.calls || view.samples || view.ns || prep.calls) {
        return 4;
    }
    texture_detail_report(120);
    if (logged != (texture_detail_on ? TD_COUNT : 0)) return 5;
    if (texture_detail[TD_VIEW].calls || texture_detail[TD_VIEW].ns) return 6;
}
"""
    with tempfile.TemporaryDirectory(prefix="mako-texture-profile-") as directory:
        work = Path(directory)
        test = work / "texture.cpp"
        exe = work / "texture.exe"
        test.write_text(fixture, encoding="utf-8")
        subprocess.run([args.cxx, "-std=c++20", "-pthread", str(test), "-o", str(exe)], check=True)
        import os
        env = os.environ.copy()
        env.pop("RX_VK_TEXTURE_PROFILE", None)
        subprocess.run([str(exe)], env=env, check=True, timeout=10)
        env["RX_VK_TEXTURE_PROFILE"] = "1"
        subprocess.run([str(exe)], env=env, check=True, timeout=10)
    print("PASS: off/on, 1-in-16 sampling, nested timing, thread isolation and interval reset")


if __name__ == "__main__":
    main()
