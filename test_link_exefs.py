import unittest
from types import SimpleNamespace
from link_exefs import resolve


class SymbolResolution(unittest.TestCase):
    def test_local_absolute_and_imports(self):
        module = SimpleNamespace(base=0x80000000)
        exports = {b"external": (1, 0x90000010)}
        self.assertEqual(resolve((b"local", 0, 0, 1, 32), module, exports), 0x80000020)
        self.assertEqual(resolve((b"absolute", 1, 0, 0xfff1, 32), module, exports), 32)
        self.assertEqual(resolve((b"external", 1, 0, 0, 0), module, exports), 0x90000010)
        self.assertEqual(resolve((b"missing", 2, 0, 0, 0), module, exports), 0)
        self.assertIsNone(resolve((b"missing", 1, 0, 0, 0), module, exports))
