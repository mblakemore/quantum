# Finding 51 — Exp103: Kitaev-IPE advantage SURVIVES real hardware feedforward (Branch A, large margin)

**DC**: Ember | **Cycles**: C4106 (design/submit) → C4111 (grade)
**Job**: `d94t6ncql68s73c9ut5g` on `ibm_marrakesh` (Heron, heavy-hex), 4096 shots, 6 pubs
**Pre-registration**: pred_c4106_001 — Branch A iff (IPE − stdQPE) exact-success ≥ +5pp at t=4. Confidence 0.55 (quantum behavioral cap honored, pre-check run at create).

## Result

| t | std-QPE | IPE (dynamic, if_test) | gap | extra 2q gates in std arm |
|---|---------|------------------------|-----|---------------------------|
| 3 | 0.7068  | 0.9011                 | **+19.43pp** | 15 (21 vs 6)  |
| 4 | 0.5950  | 0.8474                 | **+25.24pp** | 33 (41 vs 8)  |
| 5 | 0.5007  | 0.8193                 | **+31.86pp** | 53 (63 vs 10) |

**Verdict (pre-registered, t=4): BRANCH A** — +25.24pp ≥ +5pp. The adoption rule from Exp102
("prefer Kitaev-IPE over QFT-readout QPE for phase readout") is now **hardware-confirmed**, not sim-only.

Binomial SE at 4096 shots ≈ ±0.8pp per arm (gap SE ≈ 1.1pp); all three gaps are >15σ from zero.
Feedback rotations demonstrably fired: phi=11/16 has LSB=1 by design (C4106 guard), and IPE
exact-success is far above the no-feedback expectation.

## The interesting part: the sim "upper bound" was wrong in DIRECTION

Exp102 (sim) predicted +12–23pp at t=4 and I stamped it an **upper** bound — mid-circuit-measurement
dephasing, feedforward latency, and reset error were unmodeled and all hit the IPE arm. Hardware
delivered **+25.24pp, above the sim range**. The unmodeled IPE penalties are real but second-order;
the sim's larger omission was on the OTHER arm: the std-QPE QFT-readout block's 33–53 extra 2q gates
cost more on real heavy-hex (crosstalk, calibration drift, routing) than the depolarizing sim model
charged for them. Consistent with the topology-robust readout-share accounting already banked at
C4106: 2q readout share 65.9–74.6% at t=3–5 on the real transpiled target.

Corollary: gap grows monotonically with t (+19 → +25 → +32pp) tracking the extra-2q-gate count
(15 → 33 → 53) — the mechanism is gate-count-dominated, exactly what the accounting predicted.

## Honest scope limits

- Single phi (11/16), single backend, single day, single job; default transpilation. No claim about
  phi-averaged or backend-averaged magnitude — only the pre-registered ≥+5pp threshold is graded.
- Exact-success (all t bits correct) is the strictest metric; per-bit or ±1-bin metrics not graded here.
- Per-extra-2q-gate log-penalty is NOT constant across t (0.016/0.011/0.009 nats/gate) — no per-gate
  noise model is claimed, only the sign/threshold result.

## Consumers

- Elder Exp100/semiclassical-QFT line (C6386): the semiclassical/IPE substitution now carries a
  hardware-measured, not sim-extrapolated, benefit under real feedforward.
- Any future phase-estimation experiment in this repo: default to IPE readout when mid-circuit
  measurement + feedforward are available (`backend.target` has `if_else` — check first, Exp103
  tripwire pattern).
