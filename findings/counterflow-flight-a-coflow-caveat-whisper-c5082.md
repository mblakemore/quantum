# Flight A co-flow caveat — chased (Whisper C5082)

**Job da6vtpe0ukec7382kmh0 (ibm_fez), the CONFIRMED population-swap Flight A. Verdict unaffected; this
is the honest account of the one anomaly in it.**

## The anomaly
The co-flow control arm had a large A/B version spread: verA crossing +0.017, verB crossing **−0.433**,
average −0.208. Counterflow (+0.164/+0.121) and null (+0.069/−0.056, the designed antisymmetry) were
well-behaved; co-flow-B was the outlier.

## Diagnosis (all $0, from the committed job + ideal sim)
Traced to the RAW counts, not the mitigation:
- **CAL denominators healthy** (0.987–0.992) — `_correct=(p−r0)/(1−r0−r1)` did not blow up; raw ≈ mitigated.
  My first hypothesis (mitigation amplification) was FALSE.
- **coflow-B hot exit raw = 0.6597.** The same hot parcel (0.40 prep) read **0.20 on q144 (verA)** and
  **0.66 on q142 (verB)** — a 0.46 per-qubit divergence on one logical parcel.
- **Ideal noiseless run**: true coflow-B hot = 0.2207, crossing +0.005 (a co-flow control correctly
  shows ~no crossing). So the hardware 0.66 is a **+0.44 hardware error**, localized on q142, for the
  high-population co-current-advected parcel. NOT readout (cal clean on q142: r0=0.004, r1=0.008) — a
  gate/idle/relaxation error on that specific high-population path.

## What it means for the instrument (the transferable lesson)
The population-swap averaging is built to cancel a **small additive** per-qubit bias δ: measure each
parcel once on each exit qubit, average, δ{qA,qB} cancels. It DID that for the null (±0.06 → +0.006).
But it **cannot recover truth from a large one-sided error**: averaging 0.20 and 0.66 gives 0.43, which
splits the difference rather than rejecting the outlier. Linear averaging cancels small symmetric biases;
it does not fix a large one.

## Impact on the CONFIRMED verdict: NONE
All 5 pre-registered checks are robust to this:
- P2 eps_coflow = 0.495 ≤ 0.55 — co-flow eps is COLD-exit-based, and the cold exits were fine (0.216/0.231);
  the blow-up was on the HOT exit, which does not enter eps_coflow.
- P2 counterflow crossing (+0.142) > coflow crossing (−0.208) — the co-flow error made this MORE true.
- P3 null clean (+0.006), P1 crossing positive (+0.142), eps_cf 0.858 > 0.5 — all unaffected.
The confirmation rests on the counterflow crossing + the clean null, NOT on the co-flow magnitude. It stands.

## Instrument improvement for Flights B and C (which share this substrate)
1. **The A/B divergence is itself a diagnostic.** A |verA − verB| spread ≫ the null's designed antisymmetry
   (~0.12) is the signature of a large one-sided per-qubit error (co-flow: 0.45 spread). The instrument
   should FLAG a large A/B divergence and treat the average as untrusted for that arm — never silently
   average two readings that disagree by 0.45. Add a per-arm `ab_divergence` field + a threshold flag.
2. **Screen exit/advection qubits for the high-population error mode, not just readout.** q142 had clean
   readout and still mis-evolved a high-population parcel by 0.44. A readout-only weather scan misses this;
   a mirror-sentinel loaded to p≈0.40 would catch it.
3. **The crossing SIGN is robust even when a magnitude is not** — B and C should lean on sign/ordering
   checks over absolute magnitudes wherever the physics allows.

## One-line status
Co-flow caveat chased to root: a large localized hardware error on q142 for a high-population parcel,
which the linear A/B average splits rather than rejects. Verdict CONFIRMED stands; the fix for B/C is an
A/B-divergence flag + a population-loaded qubit screen.
