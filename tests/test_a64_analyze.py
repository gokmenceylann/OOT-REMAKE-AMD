from struct import pack
import unittest
from a64_analyze import analyze

class ControlFlow(unittest.TestCase):
    def test_call_and_indirect_tail(self):
        code = pack("<III", 0x94000002, 0xd65f03c0, 0xd61f0000)
        graph = analyze(code, [0x1000], 0x1000)
        self.assertEqual(graph[0x1000]["calls"], [0x1008])
        self.assertEqual(graph[0x1000]["instructions"], [0x1000, 0x1004])
        self.assertEqual(graph[0x1008]["indirect_sites"], [0x1008])
