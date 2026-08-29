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
middleware), 187 tests written against the composition rather than the five demos, and
a benchmark you re-run **on your own corpus**, with an ablation that prices all five
gates and labels which numbers came from your traffic and which from the shipped
fixtures.

It also ships `docs/LIMITS.md`, which is the part worth reading first: the input guard
stops **27/27 of our corpus and 6/41 of an outside reviewer's**, budgets are
per-process, and the audit log assumes a single writer. Gates 2, 3 and 5 are where it
earns its keep. You should know that before you pay, not after.

**$49.** Assembling the five yourself is a legitimate choice, and the repos above are
the right place to start — this is the two weeks of wiring you skip.
