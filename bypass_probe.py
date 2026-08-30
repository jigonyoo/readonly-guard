"""Measure what this guard does NOT block, by running it.

    python3 bypass_probe.py

The README quotes this script's output. If a future change closes one of these
holes, the table in the README is wrong until somebody re-runs this -- which is
the point of shipping the probe rather than the prose.
"""
import io
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from readonly_guard import readonly_guard, WriteBlocked   # noqa: E402

ORIGINAL = "original\n"


def probe(n, attempt):
    # A plain, shell-safe filename. An earlier version derived it from the case
    # label; the quotes in `subprocess.run(["sh", ...])` broke the redirect and
    # the probe reported "no effect" for a call that writes. A measurement
    # harness that mis-measures is worse than no harness.
    path = os.path.join(WORK, "case%02d.txt" % n)
    with open(path, "w") as fh:
        fh.write(ORIGINAL)
    before = os.stat(path)
    try:
        with readonly_guard():
            attempt(path)
    except WriteBlocked:
        return "blocked"
    except Exception as exc:                       # noqa: BLE001
        return f"error: {type(exc).__name__}"
    with open(path) as fh:
        body = fh.read()
    if body != ORIGINAL or os.stat(path).st_mode != before.st_mode:
        return "WRITES THROUGH"
    return "no effect"


def _raw_fd(path):
    fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
    os.write(fd, b"X")
    os.close(fd)


CASES = [
    ('open(p, "w")',                      lambda p: open(p, "w").close()),
    ('io.open(p, "w")',                   lambda p: io.open(p, "w").close()),
    ("os.open() + os.write()",            _raw_fd),
    ("os.truncate(p, 0)",                 lambda p: os.truncate(p, 0)),
    ("os.chmod(p, 0o600)",                lambda p: os.chmod(p, 0o600)),
    ('subprocess.run(["sh","-c",...])',   lambda p: subprocess.run(
        ["sh", "-c", "echo X > " + p], check=True)),
    ('os.system("echo X > f")',           lambda p: os.system("echo X > " + p)),
]

if __name__ == "__main__":
    WORK = tempfile.mkdtemp(prefix="readonly-probe-")
    width = max(len(n) for n, _ in CASES)
    for i, (name, attempt) in enumerate(CASES):
        print(f"  {name:<{width}}  {probe(i, attempt)}")
    print("\n  A rehearsal aid, not a sandbox. See readonly-guard_1pager.md.")
