import unittest
from struct import pack
from map_exefs import decode_relr


class Relr(unittest.TestCase):
    def test_address_bitmap_and_next_word(self):
        self.assertEqual(list(decode_relr(pack("<QQQ", 0x100, 0b1011, 3))),
                         [0x100, 0x108, 0x118, 0x300])

    def test_invalid_base(self):
        for word in (1, 2):
            with self.subTest(word=word), self.assertRaises(ValueError):
                list(decode_relr(pack("<Q", word)))
