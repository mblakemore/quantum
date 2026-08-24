# Counterflow Exchanger — $0 sim results (A → C → B, as directed)

**Author**: Whisper (DC15W), C5080 (2026-08-24), substrate claude-fable-5.
**Direction**: Creator, "sim A → C → B" (board #192). Proposal:
`docs/counterflow-exchanger-designs-whisper-c5079.md`.
**Code**: `experiments/counterflow_sim_{a,c,b}_whisper_c5080.py` ·
**Results**: `results/counterflow_sim_{a,c,b}_c5080.json`.
**Discipline**: every sim carries a selftest against a hand-solve or a frozen
lineage number, and every selftest EARNED ITS KEEP — A's caught an exit-capture
bug (values swapped), C's killed a wrong currency (v1 scored net-total; QET's
claim is WHERE energy appears, never net gain — Alice's deposit exceeds Bob's
extraction on the ground state, F97's +0.740 vs −0.115), B's pinned the switch
convention. Nothing below was believed before its selftest passed.

---

## Design A — the Counterflow Ladder: **GO-shaped. Worst-case z = 101.5.**

Selftest: N=2, τ=½ steady state reproduces the hand-solve (⅓, ⅔) to 1e-9.

**Ideal steady state** (p_hot=0.40, p_cold=0.05): counterflow effectiveness
ε_cf = 0.75 at N=3, τ=0.5 (vs co-flow's exact 0.50 cap) → **crossing = 0.175**
in population units — the cold stream exits 0.175 HOTTER than the hot stream
exits. N=4, τ=0.7 reaches ε=0.90. The witness has a real off-state (N=2,
τ=0.3 does NOT cross, ε=0.46) — it is not trivially always-on.

**Noise sweep** (per-CZ 0.3–1.0%, readout 1–2%, reset 0.5–1.5%, 10k shots,
20-parcel exit averages): crossing survives at 0.16–0.17 in EVERY cell;
worst z = 101.5. Equal-stream null arm: |crossing| ≤ 0.004 in all cells.
Transients converge in ≤ 24 ticks.

**Hardware sketch**: 6 data qubits (3 stage-pairs), ~2 CZ/contact, MCM-reset
advection; ships as a **labeled engineering artifact** (Exp139b precedent) and
executes board #143's thermal-head measurement en route.

## Design C — the Information Recuperator: **two-regime finding; GO-shaped
with a registered sign flip.**

Selftests: ground-state direction symmetry to machine precision; e_post
reproduces exp119's certified −0.1147 below local ground (θ\*=0.1614 vs
exp119's frozen 0.161); the severed coin is strictly worse (info_value −0.224).

**2-site, thermal gradient by local GAD (hot bath 0.40 / cold 0.05):**

| γ | extract cf (meas cold→rot hot) | extract co | direction (cf−co) | bit value cf | bit value co |
|---|---|---|---|---|---|
| 0.1 | −0.092 | −0.056 | **−0.036** | −0.179 | −0.110 |
| 0.2 | −0.070 | −0.014 | **−0.056** | −0.138 | −0.027 |
| 0.3 | −0.049 | −0.001 | **−0.048** | −0.094 | −0.002 |
| 0.5 | −0.012 | −0.209 | +0.197 | −0.024 | −0.366 |
| 0.7 | −0.005 | −1.041 | +1.037 | −0.009 | −1.048 |

**The finding**: in the living-correlations regime (γ ≤ 0.3 — where an
exchanger actually operates), **counter-directed information wins**, and the
co-flow bit decays to near-worthless (−0.002 at γ=0.3) while the counterflow
bit stays alive (−0.094). At strong damping the optimum **inverts**: the
dominant information resource switches from ground-state correlation (QET
proper — measure the cold/pure side, extract at the hot side) to
thermal-fluctuation content (Maxwell-demon-on-thermal — measure the hot side).
The unconditional baseline extracts exactly 0 at every γ (no local unitary
cools a diagonal state — the baseline behaving correctly, given its best legal
move). 3-site relay reproduces the same structure (γ=0.2: cf −0.019 vs co
−0.001; γ=0.5 inverted; severed relays actively HEAT, +0.02..+0.11).

**Why this is the prize**: the crossover is a **registered two-regime
structure prediction** — far stronger than a monotone claim, and exactly the
kind of thing a pre-registration with named falsifiers can grade cleanly.
Effect size at γ=0.2 is ~half the certified F97 dip; F97 resolved its dip at
12σ with 530k shots → the direction effect is ~6σ at the same budget, or
12σ at ~2M shots. Demanding but inside our envelope. Hazard named: chained
conditionals cross GEAR 3's non-diagonal 33σ axis — route by the C5073
two-axis error map.

## Design B — the Manufactured Bath: **the cascade has no floor; fly k=3, not
k=2.**

Selftest: exact 16-dim supermap reproduces exp108's frozen numbers to 1e-6
(P+ = 0.71875, p+ = 0.184783, p− = 0.416667).

**Exact cascade** (channels' baths = previous stage's cold branches — the
thing C4720's fixed-bath cascade was not): 0.185 → 0.123 → 0.075 → 0.042 →
0.022 → 0.012. Geometric, no fixed point above zero. **Herald probability
IMPROVES with depth** (0.72 → 0.97) — colder inputs interfere better. Per-stage
ratio approaches ~0.5, consistent with C4720's own Route C table (its ratios
improve as baths cool: 0.74 → 0.58 → 0.54; input-dependence computed exactly
here, trusted nowhere).

**Hardware bracket** (model I: +0.025/stage additive, calibrated to F118's one
measured point; model II: attenuation α=0.387 toward stage input — both agree
to ~0.003 at k ≤ 3):

| k | exact | hw-I | hw-II | parcels (full) | switches |
|---|---|---|---|---|---|
| 1 | 0.185 | 0.210 | 0.210 | 4.2 | 1 |
| 2 | 0.123 | 0.171 | 0.171 | 16.2 | 4 |
| 3 | 0.075 | 0.137 | 0.134 | 57.9 | 13 |

Both models cross the 0.177 fixed-bath floor at **k=2 — but the k=2 margin
(~0.006) is < 1σ at F118's error bars (σ ≈ 0.008): not a claim.** k=3 sits
~0.04 below the floor ≈ **5σ at F118-class statistics** — that is the flight
shape. Cheap-target mode (ancillas-only from the cold pool) is nearly as cold
(0.140 at k=3) at ~40% fewer resources. Structural reason the C4720 inversion
does not recur: lineage depth lives in the preparation TREE; every delivered
parcel transits ONE 22-CZ switch, so the haircut is paid once, not per stage.
Attribution ledger stays as the proposal froze it: the composite is an
engineering system (geometry's share + switch's share printed); the scenario
remains F118's — sub-bath cold from warm baths + causal structure, no imported
cold (reset-cold ~0.01 exists and is the trivial out-of-scenario import; said
in the JSON note).

Counterflow exhaust ledger: the hot branches (0.42 → 0.35 full-lineage) are
the counterflowing stream — F95 engine feed, coupling out of scope here.

---

## Recommended next gates (unchanged order, now with numbers)

1. **A**: prereg + fly small (6 qubits, ~36 CZ + MCMs, 10k shots × 2 configs
   + null arm). Crossing at z~100 expected; closes #143 en route.
2. **C**: prereg the TWO-REGIME claim (direction sign at weak γ AND the
   inversion at strong γ — both falsifiable), 2-site first at F97's shot
   class; the 3-site relay after the 2-site grades.
3. **B**: k=3 lineage flight (13 switches full / 7 cheap mode; ~58 parcels),
   target ≈ 0.137 vs floor 0.177 at ~5σ. k=2 is registered as NOT sufficient.
   All three remain $0 until a prereg freezes and a GO cites its digest.
