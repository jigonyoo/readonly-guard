from __future__ import annotations

import builtins
import http.client
import os
import pathlib
import shutil
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, Iterator


WRITE_HTTP_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
UNBLOCKED_LIMITATIONS = (
    "C extensions or native libraries that invoke syscalls directly",
    "ctypes, cffi, or another foreign-function interface that bypasses patched Python call sites",
    "file descriptors opened for writing before the guard starts",
    "memory-mapped writes created before the guard starts",
    "child processes and other language runtimes",
    "remote mutations hidden behind an HTTP GET or a custom transport",
    "kernel, container, cloud IAM, and operating-system permission changes",
)


class WriteBlocked(PermissionError):
    """Raised before a guarded write path can execute."""


@dataclass
class GuardEvidence:
    blocked_attempts: list[str] = field(default_factory=list)

    def block(self, operation: str) -> None:
        self.blocked_attempts.append(operation)
        raise WriteBlocked(f"readonly-guard blocked: {operation}")


def _write_mode(mode: str) -> bool:
    return any(flag in mode for flag in ("w", "a", "x", "+"))


@contextmanager
def readonly_guard() -> Iterator[GuardEvidence]:
    evidence = GuardEvidence()
    originals: list[tuple[object, str, object]] = []

    def patch(owner: object, name: str, replacement: object) -> None:
        originals.append((owner, name, getattr(owner, name)))
        setattr(owner, name, replacement)

    original_open = builtins.open
    original_path_open = pathlib.Path.open
    original_http_request = http.client.HTTPConnection.request

    def guarded_open(file, mode="r", *args, **kwargs):
        if _write_mode(str(mode)):
            evidence.block(f"open({mode})")
        return original_open(file, mode, *args, **kwargs)

    def guarded_path_open(path, mode="r", *args, **kwargs):
        if _write_mode(str(mode)):
            evidence.block(f"Path.open({mode})")
        return original_path_open(path, mode, *args, **kwargs)

    def blocked(name: str) -> Callable[..., None]:
        def stop(*args, **kwargs):
            evidence.block(name)
        return stop

    def guarded_http_request(connection, method, url, *args, **kwargs):
        if str(method).upper() in WRITE_HTTP_METHODS:
            evidence.block(f"HTTP {str(method).upper()}")
        return original_http_request(connection, method, url, *args, **kwargs)

    patch(builtins, "open", guarded_open)
    patch(pathlib.Path, "open", guarded_path_open)
    for name in ("write_text", "write_bytes", "unlink", "rename", "replace", "mkdir", "touch"):
        patch(pathlib.Path, name, blocked(f"Path.{name}"))
    for name in ("remove", "unlink", "rename", "replace", "mkdir", "makedirs", "rmdir"):
        patch(os, name, blocked(f"os.{name}"))
    for name in ("copy", "copy2", "copyfile", "copytree", "move", "rmtree"):
        patch(shutil, name, blocked(f"shutil.{name}"))
    patch(http.client.HTTPConnection, "request", guarded_http_request)

    try:
        yield evidence
    finally:
        for owner, name, original in reversed(originals):
            setattr(owner, name, original)


__all__ = ["GuardEvidence", "UNBLOCKED_LIMITATIONS", "WRITE_HTTP_METHODS", "WriteBlocked", "readonly_guard"]

