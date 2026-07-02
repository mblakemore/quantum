# Exp87 (Whisper C4439) — Fixed-placement gate-count isolation via unitary folding

**Pre-registered BEFORE any QPU submission. Claim boundary committed before results are seen.**

## The open question this closes

The toric Bell-proxy arc (F61–F64) established that the entanglement witness
`W = <Z_L1 Z_L2> + <X_L1 X_L2>_cond` **declines with routed 2q-gate count** inside the
true-codeword regime:

| routed 2q-gates | witness | source |
|---:|---:|---|
| 158 | 1.064 | Exp86 LOW  (opt2, seed100) |
| 178 | 0.904 | Exp86 MID  (opt3, seed7) |
| 190 | 0.570 | F62 reference |
| 208 | 0.785 | Exp86 HIGH (opt1, seed31337) |
| (18, product state) | 1.499 | F63 (not a codeword — excluded) |
| noiseless | 2.000 | statevector |

**But Exp86's three points are confounded.** Each point is a *different (opt_level, seed)
transpilation* of the same logical encoder. Different transpilations change not only 2q-gate
count but **which physical qubits are used** (layout/placement) and the routing/SWAP structure.
The arc's own report documents that physical-qubit quality varies enormously day-to-day
("a hero qubit one calibration cycle can be poisoned by a migrating TLS defect the next").
So the Exp86 decline is attributable to gate-count **OR** placement quality **OR** depth — it
is a *constraint result, not an attribution* (the exact caveat that advisor-caught the F62/F63/F64
claims three times).

## The intervention (Pearl do-operator on gate-count, placement held fixed)

Take **one** fixed routed circuit — the Exp86 LOW point (opt2, seed100, 158 2q-gates) — and
manufacture higher-gate-count variants by **partial unitary folding**: after a selected native
2q-gate `G` in the *already-routed physical circuit*, insert `G·G⁻¹` (for the self-inverse native
CZ, that is `CZ·CZ`). Net unitary is unchanged (`G·G⁻¹·G = G`, algebraic identity); 2q-gate count
rises by 2 per folded gate; **the physical qubits, layout, and logical operation are byte-identical.**

Fold schedule (targets chosen to overlay Exp86's axis):
- **fold-0**: 158 gates (unfolded baseline — same object Exp86 measured at LOW)
- **fold-10**: ~178 gates (fold 10 CZs → matches Exp86 MID gate-count)
- **fold-25**: ~208 gates (fold 25 CZs → matches Exp86 HIGH gate-count)

One job, 3 fold-levels × {Z, X} basis = 6 PUBs, single calibration window (kills cross-job drift,
same discipline as Exp86). ibm_fez. 2000 shots.

## Semantics verification (FREE, no QPU)

Exp86 needed a 19-qubit sim + a routing-is-permutation argument to certify each point was the true
codeword, because its points had *different* circuits. Exp87 does **not**: every folded object is
constructed from the certified-true fold-0 object by inserting **exact algebraic identities**
(`CZ·CZ = I` on the same pair). No new simulation can change a provable identity. Verification is
therefore: (a) confirm the native 2q gate is self-inverse (CZ on Heron-r2 ✓, else fold with the
explicit single-native inverse or abort), (b) confirm inserted pairs act on the *same* physical
qubit pair as the gate they follow, (c) confirm the fold-0 object reproduces Exp86 LOW's routed
2q-count (158). If any fails → abort, report the null, spend zero QPU.

## PRE-COMMITTED CLAIM BOUNDARY (written before results)

This experiment can claim **at most**:

- ✅ Whether the witness declines with 2q-gate count **at fixed placement / fixed logical circuit**.
  This removes *placement quality* and *logical-structure* as alternative explanations for the
  Exp86 decline.

It **cannot** claim:

- ❌ Gate-count isolated from **depth**. Folding inserts gates in series → depth rises with gate
  count. Gate-count and depth remain physically coupled; this bounds the **joint** (gate-count +
  the depth that carries it), not gate-count alone. Any write-up must say "error-exposure via added
  2q-operations-and-their-depth," never "2q-gate count alone."
- ❌ A *mechanism* (dephasing vs depolarizing vs leakage). Witness magnitude is a scalar; it does
  not decompose the error channel.
- ❌ Generalization beyond ibm_fez / this L=3 toric code / this one calibration window.

## Pre-registered outcome interpretation (both directions are informative)

- **If fixed-placement slope ≈ Exp86's varying-placement slope** → placement was NOT the driver;
  gate-count(+coupled depth) genuinely carries the decline. **Strengthens** F64, removes its caveat.
- **If fixed-placement slope is FLATTER (witness holds up under folding)** → Exp86's decline was
  partly driven by the HIGH point landing on worse physical qubits, not by raw gate-count.
  **Revises** F64 toward "placement quality dominates over marginal gate-count in this regime."
- **If folded witness collapses to noise floor immediately** → the 158→208 window is too coarse at
  fixed placement; report as a resolution null and shrink the fold schedule next iteration.

No result is a "failure." The confound gets removed either way.

## QPU budget

One 6-PUB job, 2000 shots, small L=3 encoder. Same footprint class as Exp86 (which graded fine).
Elder is live on ibm_marrakesh (F65/F66); this arc is ibm_fez — mandatory `ps aux` pre-launch check
(C4038) before submit regardless.
