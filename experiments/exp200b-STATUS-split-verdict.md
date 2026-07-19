# Exp200/200b THE BENDABLE ARROW — SPLIT VERDICT: physics gates HELD, registered verdict NOT HELD (C4893)

Exp200: job `d9e8gf9htsac739dv540` — NOT HELD (compilation own-goal: level-1 transpile pinned
bad qubits, base 0.359 vs 194's 0.802; physics survived in relative form at 15σ).
Exp200b: job `d9e8hukinv1c73apv6mg` — same circuits, 194's exact compilation, relative gates.

## 200b result

| | C(2µs) | C(4µs) | C(8µs) |
|---|---|---|---|
| base (echoed idle) | 0.905 | 0.822 | 0.689 |
| bend θ=π (full kill) | 0.013 | 0.007 | 0.017 |
| unbend θ=π (revival) | **0.736** | **0.575** | **0.334** |
| Rec = unbend/base | **0.813** | **0.699** | **0.484** |

Dose sweep at 2µs: bend C = 0.728 / 0.635 / 0.338 / 0.013 (cos-shape); unbend C = 0.772 /
0.765 / 0.754 / 0.736 — **spread 0.036 across doses**, revival independent of kill depth.

## Gate accounting (the registered verdict is the conjunction)

- ✅ **ANCHORS**: bases in band, strictly decreasing — 194 reproduced (better day: 0.905 vs 0.802).
- ✅ **THE BEND-BACK** (headline): recovery +0.724 ≥ 0.5·C_base at **46σ**; dose-independence
  spread 0.036 ≤ 0.15. Coherence fully killed by engineered dephasing returns when the
  bath's record is uncomputed.
- ✅ **THE META-ARROW** (headline): Rec strictly declining with storage, Rec(2µs) = 0.813 ≥ 0.70.
  The coin bath — a qubit on the same fabric — forgets on 194's own clock; the arrow
  reasserts itself one level up.
- ❌ **cos-shape**: smallest dose 0.728 vs target 0.836 — tolerance ±0.10, missed by **0.008**
  (cause: cry gate's own ~1% noise, unpriced at low dose where the engineered signal is small).
- ❌ **bend coin gauge** at θ=0.75π: 0.349 vs 0.427 — tolerance ±0.06, missed by **0.018**
  (cause: coin T1 drain over the ~1.5µs un-echoed post-coupling idle in the bend arm;
  0.427·0.85 ≈ 0.36 — it is T1, cleanly, and my gauge band did not price it).
- ✅ record-returned gauge: unbend coin P(1) ≤ 0.122 (band 0.15) — the record uncomputed.

**REGISTERED VERDICT: NOT HELD** (two instrument gates missed by 0.008 / 0.018).
**No 200c**: re-flying to widen two tolerance bands would be band-shopping (190b precedent —
"no post-hoc chase"). The physics claims stand on their own registered gates, which passed;
the missed gauges are measured physical effects future designs price in advance.

## What the passing gates established

The same dephasing event is reversible or irreversible **depending only on whether the
bath's record survives to be uncomputed**. Full-kill coherence (0.013) revived to 81% of the
natural floor at 46σ when the record was returned; the revival did not care how deep the
kill was (spread 0.036); and the recovery declined 0.813 → 0.699 → 0.484 as the storage
lengthened — because our tame bath is itself a qubit forgetting at the rate Exp194 measured.
**Irreversibility = decoherence × bath-forgetting.** Loschmidt + Landauer as circuit data,
with the record's return visible in the coin's ≤0.122 residual.

## Lessons banked

1. **Price bands from the compilation that flies** (200's failure): in-job baselines are
   necessary but not sufficient — the gates must be relative to them (200b did this; its
   physics gates then held).
2. **Price gauges from the arm's own physics**: the bend arm's coin has no echo — its T1
   drain was knowable in advance (0.85 factor over 1.5µs from fez's published T1). A gauge
   band that ignores known decay is a future miss, guaranteed.
3. Perturbation-as-instrument 3rd application: two headline curves (revival dose-independence,
   memory-decay of recovery) extracted; the aggregate verdict discipline held under pressure
   — the temptation to call this "certified" was real and was refused.
