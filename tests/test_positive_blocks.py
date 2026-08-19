import http.client
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from readonly_guard import WriteBlocked, readonly_guard


class PositiveBlockTests(unittest.TestCase):
    def setUp(self):
        self.holder = tempfile.TemporaryDirectory()
        self.addCleanup(self.holder.cleanup)
        self.root = Path(self.holder.name)
        self.source = self.root / "source.txt"
        self.source.write_text("evidence", encoding="utf-8")

    def assert_blocked(self, action):
        with readonly_guard():
            with self.assertRaises(WriteBlocked):
                action()

    def test_01_builtin_open_write(self):
        self.assert_blocked(lambda: open(self.root / "new.txt", "w"))

    def test_02_builtin_open_append(self):
        self.assert_blocked(lambda: open(self.source, "a"))

    def test_03_path_write_text(self):
        self.assert_blocked(lambda: (self.root / "new.txt").write_text("x"))

    def test_04_os_remove(self):
        self.assert_blocked(lambda: os.remove(self.source))
        self.assertTrue(self.source.exists())

    def test_05_os_rename(self):
        self.assert_blocked(lambda: os.rename(self.source, self.root / "renamed.txt"))

    def test_06_shutil_copyfile(self):
        self.assert_blocked(lambda: shutil.copyfile(self.source, self.root / "copy.txt"))

    def test_07_path_mkdir(self):
        self.assert_blocked(lambda: (self.root / "new-dir").mkdir())

    def test_08_http_post(self):
        self.assert_blocked(lambda: http.client.HTTPConnection("127.0.0.1").request("POST", "/"))

    def test_09_http_put(self):
        self.assert_blocked(lambda: http.client.HTTPConnection("127.0.0.1").request("PUT", "/"))

    def test_10_http_delete(self):
        self.assert_blocked(lambda: http.client.HTTPConnection("127.0.0.1").request("DELETE", "/"))

    def test_11_guard_records_blocked_operation(self):
        with readonly_guard() as evidence:
            with self.assertRaises(WriteBlocked):
                os.remove(self.source)
            self.assertEqual(evidence.blocked_attempts, ["os.remove"])

    def test_12_patches_are_restored(self):
        original = os.remove
        with readonly_guard():
            self.assertIsNot(os.remove, original)
        self.assertIs(os.remove, original)


if __name__ == "__main__":
    unittest.main()

