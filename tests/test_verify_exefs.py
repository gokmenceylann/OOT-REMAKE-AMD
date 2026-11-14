import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import lz4.block
from verify_exefs import verify_module


class VerifyExeFs(unittest.TestCase):
    def test_lz4_and_hash_failure(self):
        payload = b"synthetic fixture" * 32
        packed = lz4.block.compress(payload, store_size=False)
        header = bytearray(256)
        struct.pack_into("<4s", header, 0, b"NSO0")
        struct.pack_into("<I", header, 12, 9)
        struct.pack_into("<III", header, 0x10, 256, 0, len(payload))
        struct.pack_into("<I", header, 0x60, len(packed))
        header[0xA0:0xC0] = hashlib.sha256(payload).digest()
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "main"
            path.write_bytes(header + packed)
            self.assertEqual(verify_module(path)["segments"]["text"]["hash_status"], "verified")
            header[0xA0] ^= 1
            path.write_bytes(header + packed)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                verify_module(path)
