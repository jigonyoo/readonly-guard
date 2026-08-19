import unittest
from pathlib import Path

from readonly_guard import UNBLOCKED_LIMITATIONS


ROOT = Path(__file__).resolve().parents[1]


class LimitationTests(unittest.TestCase):
    def test_01_limitations_are_machine_visible(self):
        self.assertGreaterEqual(len(UNBLOCKED_LIMITATIONS), 6)

    def test_02_native_syscalls_are_disclosed(self):
        self.assertTrue(any("syscalls directly" in item for item in UNBLOCKED_LIMITATIONS))

    def test_03_preopened_descriptors_are_disclosed(self):
        self.assertTrue(any("opened for writing before" in item for item in UNBLOCKED_LIMITATIONS))

    def test_04_child_processes_are_disclosed(self):
        self.assertTrue(any("child processes" in item for item in UNBLOCKED_LIMITATIONS))

    def test_05_http_get_mutation_is_disclosed(self):
        self.assertTrue(any("HTTP GET" in item for item in UNBLOCKED_LIMITATIONS))

    def test_06_client_document_lists_six_limits(self):
        text = (ROOT / "readonly-guard_1pager.md").read_text(encoding="utf-8")
        for number in range(1, 7):
            self.assertIn(f"{number}.", text)


if __name__ == "__main__":
    unittest.main()

