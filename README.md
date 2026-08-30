# readonly-guard

A narrow Python guard for audit, inventory, and verification tools that are meant to
read evidence without changing the connected environment.

> **One of five.** This repo is the read-only enforcement layer. If your agent needs more than
> one of them, see [*Part of a set*](#part-of-a-set) at the bottom.

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

## What it does not block — measured, not asserted

The limitation most guards like this leave to the reader. `bypass_probe.py` runs each
call inside the guard and reports whether the file changed:

```bash
python3 bypass_probe.py
```

```
  open(p, "w")                     blocked
  io.open(p, "w")                  WRITES THROUGH
  os.open() + os.write()           WRITES THROUGH
  os.truncate(p, 0)                WRITES THROUGH
  os.chmod(p, 0o600)               WRITES THROUGH
  subprocess.run(["sh","-c",...])  WRITES THROUGH
  os.system("echo X > f")          WRITES THROUGH
```

`io.open` is the one to take seriously: it is not an evasion, it is what a normal
library does. The guard replaces `builtins.open`, and `io.open` is a separate name for
the same function. Anything that shells out, uses a C extension or `ctypes`, holds a
descriptor opened before the guard started, or speaks HTTP over a transport other than
`http.client` is likewise unaffected — `UNBLOCKED_LIMITATIONS` in `readonly_guard.py`
lists those categories.

**Use it to catch the write you forgot about in your own tool during a dry run. Do not
use it as a containment boundary for code you do not trust.** For that you need a
container, a read-only mount, or a seccomp profile, and none of those is a Python
context manager.

28 tests, standard library only, no network: `python3 -m unittest discover -s tests`.

> **The paid composition publishes its evidence, including where this layer has no number.**
> GuardStack (bottom of this file) carries this guard as `with gs.readonly():`; its benchmark
> report is public — **[evidence report](https://claude.ai/code/artifact/b9435c65-2173-4e40-90d7-54eb67a080fa)** — and it prices gates 1
> through 5 by ablation. Read-only is not among them: it has no row there. Better to know
> that from the report than to find it afterwards.

---

## Part of a set

This repo is one of five agent-safety layers I maintain. All MIT, all free, and
staying that way.

| Layer | Repo |
|---|---|
| Input / output guard | [`llm-guardrails`](https://github.com/jigonyoo/llm-guardrails) |
| Permission grants + audit log | [`mcp-permission-server`](https://github.com/jigonyoo/mcp-permission-server) |
| Approval gate | [`agent-approval-gate`](https://github.com/jigonyoo/agent-approval-gate) |
| Retry / timeout / circuit breaker | [`agent-reliability-kit`](https://github.com/jigonyoo/agent-reliability-kit) |
| Read-only enforcement | [`readonly-guard`](https://github.com/jigonyoo/readonly-guard) ← you are here |

They were built as five separate demos, so they **do not compose**: each carries its
own config, its own audit log, and its own idea of what "denied" means. Wiring them
into one agent is a real job.

**[GuardStack](https://buy.polar.sh/polar_cl_Zgd01SZaW8RwTEc8j7MMpWryCwLBFmoeMoPt53a4yoV)** is that job, already done — five gates in a
fixed order, one call each, writing to **one shared hash-chained audit log**, so
*"what did the agent try, and under which rule was it allowed"* is answerable from a
single file. It ships with framework adapters (OpenAI-compatible wrapper, FastAPI
middleware), a test suite written against the composition rather than the five demos,
and a benchmark you re-run **on your own corpus**, with an ablation that prices gates
1-5 (input, permission, approval, reliability, output) and labels which numbers came
from your traffic and which from the shipped fixtures. The current test count and every
other figure live in the [evidence report](https://claude.ai/code/artifact/b9435c65-2173-4e40-90d7-54eb67a080fa),
which is regenerated from the benchmark — this file deliberately does not repeat them,
because a version-dependent number copied into five repos is a number that goes stale in
five places at once. It did, twice.

It also ships `docs/LIMITS.md`, which is the part worth reading first: the input guard
stops **27/27 of our corpus and 5/42 of a corpus written to break it** — and that
second corpus ships in the box, so the bad number is one command away rather than a
sentence you have to take on trust. Budgets are per-process, and the audit log assumes
a single writer. Gates 2, 3 and 5 are where it earns its keep. You should know that
before you pay, not after.

**$49.** Assembling the five yourself is a legitimate choice, and the repos above are
the right place to start — this is the two weeks of wiring you skip.
