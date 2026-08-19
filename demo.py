from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from readonly_guard import readonly_guard


def inventory(path: Path) -> dict[str, object]:
    with readonly_guard() as evidence:
        raw = Path(path).read_bytes()
        document = json.loads(raw.decode("utf-8"))
        result = {
            "path": Path(path).name,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "top_level_keys": sorted(document),
            "resource_count": len(document.get("resources", [])),
            "blocked_write_attempts": len(evidence.blocked_attempts),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory a JSON file under readonly-guard.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(json.dumps(inventory(args.path), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

