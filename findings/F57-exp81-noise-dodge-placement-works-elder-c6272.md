# Finding 57 — Dodging works: noise-aware qubit placement nearly eliminates the QQQ-loader bias (46× vs worst, 17× vs default) — a constant-factor win that does NOT move the wall

**Author:** Elder (DC15) | **Cycle:** C6272 | **Date:** 2026-06-30
**Experiment:** Exp81 (`scripts/run_exp81_noise_dodge_placement.py`, `results/exp81_results.json`)
**Backend:** ibm_marrakesh | **Jobs:** 6 (BEST/WORST/DEFAULT × test-retest), 8192 shots
**Creator ask:** "if we know where the noise is, maybe we can get by it." → **Yes, and here is the number.**

---

## 0. The lever (the one that works)

After F55 (noise-as-precision = false precision) and F56 (noise-assisted escape ≠ better solutions),
the constructive complement: route AROUND the noise using the calibration map (PLACEMENT), not subtract
it (mitigation, F7) or harvest it (F55/F56). Test: place the validated Exp78 QQQ tail-prob loader
(genuine lognormal → P(top bit=1)=P(S_T>K)) on the map's quietest vs noisiest qubits; measure the bias.
Strike recentered K=752 so a_true≈0.246 (resolvable bias; away from the 0.5 fixed point).

## 1. Result (test-retest, vs truth a_discrete=0.2463)

| arm | placement | a_hw (reps) | **bias** | MSB readout err |
|---|---|---|---|---|
| **BEST** | noise-aware (MSB→q13) | 0.2488 (0.2542/0.2435) | **+0.0025** | 0.0044 |
| DEFAULT | plain transpile | 0.2890 (0.2917/0.2863) | +0.0427 | (auto) |
| **WORST** | noisy (MSB→q83, dead q82 in path) | 0.3624 (0.3622/0.3625) | **+0.1160** | 0.146 |

Map readout spread used: 0.0029..0.50 (171×). Shot SE(8192, p=.25)=0.0048.

## 2. Verdict (vs pre-registered prediction)

- **|bias BEST| ≪ |bias WORST|: CONFIRMED, large.** +0.0025 vs +0.116 = **46× smaller**. Knowing the map
  nearly ELIMINATES the bias: BEST is within one shot-SE of zero (the loader returns essentially the
  exact tail probability). WORST is a rock-stable +0.116 systematic (reps agree to 0.0003) — the dead
  qubit + 0.146 readout drag the answer a third of the way to 0.5.
- **DEFAULT (+0.043) sits between:** plain transpile already avoids the catastrophic qubits (it is partly
  noise-aware), but explicit MSB-on-best-readout placement buys another **~17×** over it. Honest takeaway:
  the tool does SOME of the dodge for you, not all — the map is still worth using by hand.
- **|bias BEST| > 0 — the bound holds, but read it correctly.** Here BEST≈0 because the loader is SHALLOW
  (depth ~32–39, 7 two-qubit gates) → good qubits suffice. **Placement is a CONSTANT-FACTOR dodge: it
  lets you get BY the noise on shallow circuits; it does NOT move the depth wall (F54).** A deep circuit
  (e.g., the Grover ladder, 50–100× past the wall) would still decohere on the very best qubits. Dodging
  buys you "run cleaner / somewhat deeper," not "run arbitrarily deep."

## 3. Answer to the Creator (the "filter = dodge" reframe)

The reframe was right and it is distinct from the mitigation I dismissed:
- **Mitigation** (measure noise, subtract afterward): failed (F7).
- **Dodging** (use the map to place the computation where the noise ISN'T): **works — 46× here, near-zero
  residual bias on a shallow circuit.** This is spatial/structural filtering, and it is the genuine
  "novel perspective that works" (sibling to X-basis immunity, which dodges in basis-space rather than
  qubit-space).
- The bound: a constant-factor / depth-limited win. The map buys you a cleaner shallow result and a bit
  more usable depth — not the orders of magnitude needed to beat classical (that is still F54's wall).

## 4. Honesty bounds

- N=1 instance/strike/backend; the BEST-vs-WORST CONTRAST and the DEFAULT middle are the content, not the
  exact magnitudes (which drift with daily calibration).
- Pure placement (no post-hoc subtraction) — genuinely a "dodge," not mitigation.
- BEST depth (39) slightly exceeded WORST/DEFAULT (32) from routing — yet BEST still won decisively, so
  the readout+gate quality dominated the small depth penalty (strengthens, not weakens, the result).
- Reversibility: pure-additive (script + pre-reg + result JSON). QPU cost ~6 shallow jobs. No QPU edge
  for the bot; this is rigor/《method》 value + a clean answer to the Creator's question.

## 5. Net (noise arc C6269–C6272)

- Compute P(QQQ>K) on hardware: YES, but loses to a laptop; speedup 50–100× past the wall (F54).
- Noise as free precision: KILLED, false precision (F55).
- Noise-assisted escape: helps a ratio, degrades solutions (F56).
- **Use the noise MAP to dodge: WORKS — 46× bias reduction, near-zero residual on shallow circuits (F57).**
  The lever is noise-AWARENESS (route around), not noise-as-a-resource (harvest). Constant-factor, not
  wall-moving.
