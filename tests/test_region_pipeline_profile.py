import runpy
from pathlib import Path
import unittest


exporter = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/Export-RegionPipelineProfile.py"))
profile = exporter["profile"]
GPU = "[hos host] vk: capability device=GPU vendor=0x1002 deviceID=0x73df API=1.4.315 driver=0x800161"


def work(key, ms, thread="Presentation Thread", result=0):
    return f"[hos {thread}] vk: graphics pipeline of a: SLOW build, {ms} ms; pipeline_key={key} VkResult={result} feedback=0x1"


class RegionProfileTest(unittest.TestCase):
    def test_confirmed_transition_and_region_order(self):
        before = "[hos BaseProc] cheats: teleport child to Market_Child at Gate: request sent, result 0x1"
        arrived = "[hos BaseProc] map: Market_Child (child)"
        leave = "[hos BaseProc] map: HyruleField_Child (child)"
        short = "0000000000000001"
        long = "0000000000000002"
        excluded = "0000000000000003"
        result = profile([GPU, work(excluded, 9000), before, work(short, 300), arrived,
                          work(long, 4000), work(short, 350), work(excluded, 9000, "host"),
                          work(excluded, 9000, result=-2), leave, work(excluded, 9000)], "CastleTown")
        self.assertEqual(result.splitlines(), ["OOT_PIPELINE_REGION_1 1002 73df 800161", long, short])

    def test_unconfirmed_transition_and_mix_of_devices(self):
        start = "[hos BaseProc] cheats: teleport child to Market_Child at Gate: request sent, result 0x1"
        with self.assertRaises(ValueError):
            profile([GPU, start, work("0000000000000001", 500)], "CastleTown")
        with self.assertRaises(ValueError):
            profile([GPU, GPU.replace("800161", "abcdef")], "CastleTown")


    def test_successful_usage_and_multiple_captures(self):
        collect = exporter["collect"]
        combine = exporter["format_profile"]
        mark = "[hos guest] map: Market_Child (child)"
        adult = "[hos guest] map: Market_Adult (adult)"
        graphic = "0000000000000001"
        compute = "c 0000000000000002 0000000000000003"
        other = "0000000000000004"
        first = collect([GPU, mark, f"vk: region pipeline use g {graphic}", f"vk: region pipeline use {compute}",
                         adult, f"vk: region pipeline use g {other}"], "CastleTown", "child")
        second = collect([GPU, mark, work(other, 800)], "CastleTown")
        self.assertEqual(combine([first, second]).splitlines()[1:], [other, compute, graphic])
        with self.assertRaises(ValueError):
            combine([first, (("1002", "73df", "abcd"), second[1])])


if __name__ == "__main__":
    unittest.main()
