# Read-only by construction: tested application guard

## What the client receives

The audit or inventory command runs inside `readonly_guard()`. The same test suite
proves two things: the normal read path still completes, and deliberate write attempts
are stopped before the patched operation runs.

## Write paths this sample blocks

- Python `open` and `Path.open` when the mode contains `w`, `a`, `x`, or `+`.
- `Path.write_text`, `write_bytes`, `unlink`, `rename`, `replace`, `mkdir`, and `touch`.
- Selected `os` removal, rename, replacement, and directory-creation functions.
- Selected `shutil` copy, move, and removal functions.
- HTTP `POST`, `PUT`, `PATCH`, and `DELETE` through `http.client.HTTPConnection.request`.

## Read paths that remain available

Opening and hashing a file, parsing JSON and CSV, listing a directory, reading file
metadata, globbing paths, and running the sample inventory are exercised while the
guard is active.

## What this guard cannot block

1. C extensions or native libraries that invoke syscalls directly.
2. `ctypes`, `cffi`, or another foreign-function interface that bypasses patched Python call sites.
3. File descriptors and memory maps opened for writing before the guard starts.
4. Child processes and other language runtimes.
5. Remote mutations hidden behind HTTP `GET` or a custom transport.
6. Kernel, container, cloud IAM, or operating-system permission changes.

## Honest boundary

This is a narrow, tested application policy for this Python process. It is not a
complete sandbox and does not replace a read-only account, least-privilege API scopes,
filesystem permissions, a container policy, or human review. The production control
is strongest when those independent layers are also read-only.

