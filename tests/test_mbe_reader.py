import io
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from mbe_reader import read_mbe


class PackedBoolTests(unittest.TestCase):
    def test_separate_bool_groups_preserve_following_field_guide_slot(self):
        columns = (2, 9, 9, 2, 9, 2)
        name = b"status\0\0"
        header = struct.pack("<i", len(name)) + name + struct.pack("<i6i", len(columns), *columns)
        header += struct.pack("<ii", 20, 1)
        row = struct.pack("<5i", 110, 1, 27, 1, 508)
        data = b"EXPA" + struct.pack("<i", 1) + header.ljust((len(header) + 7) & ~7, b"\0") + row
        self.assertEqual(read_mbe(io.BytesIO(data))[0]["rows"], [[110, 1, 0, 27, 1, 508]])
