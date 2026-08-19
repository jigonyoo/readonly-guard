# readonly-guard

A narrow Python guard for audit, inventory, and verification tools that are meant to
read evidence without changing the connected environment.

```bash
python3 demo.py sample_read/inventory.json
python3 -m unittest discover -s tests -v
```

The context manager blocks the common write paths used by this sample: write-capable
`open` modes, selected `pathlib`, `os`, and `shutil` mutations, plus HTTP `POST`,
`PUT`, `PATCH`, and `DELETE` requests. The demo inventory still runs inside the guard.

This is a tested application-level policy, not an operating-system sandbox. Read
`readonly-guard_1pager.md` before presenting it to a client; the limitations are part
of the contract.

