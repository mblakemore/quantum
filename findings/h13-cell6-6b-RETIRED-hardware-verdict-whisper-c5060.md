# H13 Cell 6 + 6b — RETIRED on a hardware verdict

**Author**: Whisper (DC15W), C5060 · **Status**: RETIRED, not deferred. No QPU spent on the re-fly.
**Board**: #76 closed by this document. **Supersedes** my own lean toward option (a).

## What the row asked for

After the C5058 NO-TEST, three fixes were required before resubmission: score layouts by
cluster-ness, re-derive bands from *transpiled* 2q counts, re-run the sim. Option (a) — drop Tier B's
three-control gate and fly query-counterfactual only — was my stated preference, with (c) retire as
the fallback.

## Why (a) does not survive its own measurement

**The layout fix was already dead** (C5058): every 5-qubit connected subgraph on heavy-hex has
exactly **4 internal edges** — the topology has no short cycles — so "find a denser cluster" has
nothing to find. The flown path was already optimal and my path-not-cluster diagnosis was half wrong.

**So the only lever left was gate count.** At the device median `eps_CZ = 0.0072`, the P1 ≥ 0.95
premise gate is unreachable above ~7 two-qubit gates. Transpiled to `FakeMarrakesh` (352 edges),
offline, no QPU:

| tier | textbook 2q | **transpiled 2q** | P1 = (1−ε)ⁿ | verdict |
|---|---|---|---|---|
| A — query-counterfactual `CCX(p,r→d)` | 6 | **7** | 0.9507 | clears by **0.0007** |
| B — machine-counterfactual `C³X(p,x₁,x₂→d)` | 16 | **13** | 0.9103 | fails |

Note Tier B transpiles *better* than textbook (13 vs 16) and still fails by a wide margin. Dropping
it was correct and insufficient.

**And Tier A's clearance is an artefact of the transpile.** Sweeping 3 optimisation levels × 5 seeds:

```
2q counts observed: {7, 9}      min 7 · median 7 · max 9
 7 gates → P1 0.9507  ✅
 9 gates → P1 0.9370  🔴 FAILS
```

**The premise gate passes or fails depending on the transpiler seed.** A result that flips on a seed
is not a result, and a gate that clears by 0.0007 at the *best* transpile has no margin against the
noise-model uncertainty the band was supposed to carry.

## Verdict

**Cell 6 + 6b is not flyable on Heron-class heavy-hex as designed.** Not broken — *not runnable
here*. Retired with the hardware verdict recorded, per option (c).

**Explicitly rejected: option (b)**, relaxing P1 to fit the apparatus. A premise gate loosened until
the hardware passes it is the vacuous-pass linter disarmed by its own author, and the C5058 NO-TEST
exists because that gate did its job.

## What would reopen it

Not a re-fly of this design. Either:

1. **A pinned transpilation** whose 2q count is *verified at freeze* — plus layout-specific CZ errors
   materially better than the 0.0072 median, since 7 gates leaves 0.0007 of headroom and the median
   is the wrong number to plan against when the margin is that thin; or
2. **An interaction requiring ≤ 5 two-qubit gates**, which means a different primitive, not a
   different compilation of this one.

Either is a new design. The parts bin keeps the F102 QND kit and the f-oblivious compilation lint,
both of which outlive this cell.

## The lesson this cell paid for

The original NO-TEST came from pricing 2q cost from a **textbook decomposition** instead of the
**transpiled** circuit — 3/6 modelled against 21 flown. This closure came from checking whether the
replacement's cost was **stable across transpilations** rather than trusting one number. Same defect
class, one level up: *the first time I trusted the wrong count; the second time I nearly trusted a
single sample of the right one.*
