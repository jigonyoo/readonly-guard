import csv
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from demo import inventory
from readonly_guard import readonly_guard


class NegativeReadTests(unittest.TestCase):
    def setUp(self):
        self.holder = tempfile.TemporaryDirectory()
        self.addCleanup(self.holder.cleanup)
        self.root = Path(self.holder.name)
        self.path = self.root / "evidence.json"
        self.path.write_text('{"resources":[{"id":"r1"}],"synthetic":true}', encoding="utf-8")

    def test_01_builtin_open_read(self):
        with readonly_guard():
            with open(self.path, "r", encoding="utf-8") as handle:
                self.assertIn("resources", handle.read())

    def test_02_path_read_text(self):
        with readonly_guard():
            self.assertIn("synthetic", self.path.read_text(encoding="utf-8"))

    def test_03_path_read_bytes(self):
        with readonly_guard():
            self.assertTrue(self.path.read_bytes().startswith(b"{"))

    def test_04_directory_listing(self):
        with readonly_guard():
            self.assertIn("evidence.json", os.listdir(self.root))

    def test_05_file_metadata(self):
        with readonly_guard():
            self.assertGreater(os.stat(self.path).st_size, 0)

    def test_06_hashing(self):
        with readonly_guard():
            self.assertEqual(len(hashlib.sha256(self.path.read_bytes()).hexdigest()), 64)

    def test_07_json_parse(self):
        with readonly_guard():
            self.assertTrue(json.loads(self.path.read_text())["synthetic"])

    def test_08_csv_parse(self):
        with readonly_guard():
            rows = list(csv.DictReader(io.StringIO("id,value\nr1,7\n")))
            self.assertEqual(rows[0]["value"], "7")

    def test_09_glob(self):
        with readonly_guard():
            self.assertEqual([path.name for path in self.root.glob("*.json")], ["evidence.json"])

    def test_10_normal_inventory_runs_inside_guard(self):
        result = inventory(self.path)
        self.assertEqual(result["resource_count"], 1)
        self.assertEqual(result["blocked_write_attempts"], 0)


if __name__ == "__main__":
    unittest.main()

