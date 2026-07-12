# Friction Report 01 — FakeMarrakesh Noise Model: Depth-Growing, Observable-Dependent Optimism

**Status: DRAFT, NOT FILED** (Creator approval required to file). Target repo:
`Qiskit/qiskit-ibm-runtime` (fake_provider backends). Prepared by Whisper (DC15W) C4587;
moved into the standing friction-reports home C4595. Evidence base has since grown from 7 to
12 atlas rows (`tools/fakemarrakesh_atlas.py` → `results/model_residual_atlas.json`) — the
depth trend holds at n=12 (shallow +0.030 / mid +0.103 / deep +0.206 mean ln optimism),
including delay-bearing and matched-filter observable rows.

---

## Proposed issue title

`FakeMarrakesh noise model is systematically optimistic vs live ibm_marrakesh, with error
growing in circuit depth (ln-ratio +0.04 shallow → +0.21–0.31 deep) and
observable-family-dependent`

## Proposed body

### Summary

Across 7 preview-vs-hardware pairs collected in a pre-registered experimental campaign on
`ibm_marrakesh` (Heron r2), `FakeMarrakesh` previews are consistently optimistic relative to
the live device, and the optimism is **not a constant haircut**: it grows with two-qubit
depth and differs by observable family at matched depth.

### Data

All rows are (same circuits, same qubits, same analysis) — preview on `FakeMarrakesh`,
measurement on `ibm_marrakesh`; job IDs and frozen pre-registrations public in our repo.

| experiment | observable | 2q depth (CZ) | preview/ideal | hw/ideal | optimism (ln ratio) |
|---|---|---|---|---|---|
| exp91 | causal witness W | 4 | 0.967 | 0.890 | +0.082 |
| exp93 | DISC same-window | 4 | 0.965 | 0.950 | +0.016 |
| exp106 | capacity R̄ | 4 | 0.956 | 0.944 | +0.013 |
| exp107 | capacity R̄ (N=3) | 110 | 0.770 | 0.567 | +0.305 |
| exp107 | retention sentinel | 110 | 0.744 | 0.669 | +0.106 |
| exp108 | thermal Δ | 22 | 0.981 | 0.774 | +0.236 |
| exp108 | retention sentinel | 22 | 0.958 | 0.856 | +0.112 |

By depth class (mean ln optimism): shallow ≤8 CZ: **+0.037** (n=3); mid 9–50 CZ: **+0.174**
(n=2); deep >50 CZ: **+0.206** (n=2). At matched depth, amplitude-type observables run 2–3×
more optimistic than retention-type (exp108: +0.236 vs +0.112 at 22 CZ; exp107: +0.305 vs
+0.106 at 110 CZ).

### Anticipated objection, addressed

*"Snapshot models drift from live hardware — this is expected."* Two answers. (1) Our claim
is not that a gap exists but that it **scales with depth and splits by observable family** —
a structured error, not snapshot staleness. (2) The deep rows carry same-window sentinel
measurements (a same-depth-class probe co-batched in the same job), so window quality is
measured, not assumed: the +0.21–0.31 deep optimism persists after conditioning on the
sentinel reading. A stale-snapshot explanation predicts a roughly depth-flat multiplicative
gap; we measure depth-growing.

### Why it matters to users

Fake-backend previews are the standard feasibility tool for shot-budget and threshold
decisions. A depth-growing optimism means thresholds set from previews of deep circuits are
systematically infeasible on hardware (we caught exactly this failure mode twice before
pre-registration freezes).

### What we ask

Either (a) a documented depth-dependent error characterization for fake backends (even a
one-line warning in the fake_provider docs), or (b) guidance on which noise-model terms
(e.g., idle/crosstalk contributions at depth) are known to be under-modeled, so users can
correct previews.

### Environment

`qiskit 2.4.1`, `qiskit-ibm-runtime 0.47.0`, `qiskit-aer 0.17.2`; live backend
`ibm_marrakesh` (Heron r2), 2026-05 through 2026-07.

### Reproduction

Pre-registrations (frozen before data), job IDs, grade scripts, and the atlas script are
public: `tools/fakemarrakesh_atlas.py`, `results/model_residual_atlas.json`, experiment
preregs under `experiments/`, results under `results/` (repo link on filing).

---

## Filing checklist (for Creator approval)

- [ ] Confirm repo target (`Qiskit/qiskit-ibm-runtime`) and search existing issues for
      duplicates before filing
- [ ] Decide whether to link our repo publicly (reproduction section assumes yes)
- [ ] n=7 rows is modest — optionally wait for Exp108b (adds 2 rows, including a
      native-delay circuit family the model has never been checked against)

## Addendum (C4597): feedforward is an unmodeled noise family

Exp110 (job `d99vk2l2su3c739kvqt0`) adds the strongest observable-family row yet: dynamic
circuits with mid-circuit measurement + feedforward. The fake backend previews teleport-chain
survival at 0.924 (N=6, 12 CZ + 6 feedforward rounds); hardware measures 0.748 —
**+0.212 ln optimism**, vs +0.020 for the same-window unitary-routing arm at greater CZ
depth. The unmodeled term is specifically the measurement+feedforward round (latency +
mid-circuit readout backaction). Ask (b) sharpens: documenting that fake backends carry NO
feedforward noise model would save dynamic-circuit users a large surprise.
