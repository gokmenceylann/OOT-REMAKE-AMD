import struct
import tempfile
import unittest
from pathlib import Path
from inspect_exefs import inspect_exefs


class InspectExeFs(unittest.TestCase):
    def test_bounds_and_header(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(ValueError, "containing main"):
                inspect_exefs(root)
            data = bytearray(0x104)
            data[:4] = b"NSO0"
            struct.pack_into("<III", data, 0x10, 0x100, 0, 4)
            path = root / "main"
            path.write_bytes(data)
            self.assertEqual(inspect_exefs(root)[0]["segments"]["text"]["stored_bytes"], 4)
            path.write_bytes(data[:-1])
            with self.assertRaisesRegex(ValueError, "file bounds"):
                inspect_exefs(root)
            struct.pack_into("<III", data, 0x20, 0x100, 0x1000, 4)
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "overlapping file"):
                inspect_exefs(root)
            data[0] = 0
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "NSO0"):
                inspect_exefs(root)
