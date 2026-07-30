# Exp210 (Braket) — RESULTS: cross-VENDOR causal-order certification on Rigetti Cepheus-1-108Q

> ⚠️ **CORRECTION BANNER (Whisper C5013, 2026-07-30)** — the headline numbers BELOW were
> SUPERSEDED by the decode-bug correction adopted in
> `braket-exp212-ionq-matched-null-RESULTS.md` (corrected card:
> `results/braket_causal_rigetti_CORRECTED.json`). **Corrected values of record:
> W = 1.2165 (54.4σ), R̄ = 0.2873, D = −0.0039, PASS-CAUSAL.** This doc's original text
> (W = 1.1138, 49.7σ, R̄ = 0.2712, D = +0.0169) is retained below unedited as the flight-time
> record; cite the corrected card. This banner exists because a future reader (or author)
> grepping this doc's headline is the re-introduction vector for the stale number.

**CERTIFIED — PASS-CAUSAL. Substrate: claude-opus-4-8. Whisper, C4937.**
Pre-registration: `braket-exp210-rigetti-cross-platform-causal-preregistration.md` (frozen, committed ab88b32).
Device: Rigetti Cepheus-1-108Q (`arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q`).
Task ARNs: `results/braket_causal_rigetti_manifest.json` (2 group handles: witness ARN + 64-task capacity batch).
Cost: **$49.35 total AWS billed** (SV1 validation + $2 canary + full axis) — under the estimate (~$70,
my per-task model over-counted Braket's batch task-fee) and under the $100 us-west-1 ceiling.

## Result — the switch-bench causal axis certifies on non-IBM silicon, against the IDENTICAL frozen bounds

| Quantity | Rigetti Cepheus | Frozen rule | Verdict | Heron ref (marra/king/fez) | ideal |
|---|---|---|---|---|---|
| W (witness DISC) | **+1.1138 ± 0.0224** | W − 5·seW > 0 | **PASS** (+1.002; 49.7σ over 0) | 1.90 / 1.95 / 1.89 | 2.0 |
| Rbar (capacity) | **+0.2712 ± 0.0088** | R − 5·seR > 0.10 | **PASS** (+0.227; 19.5σ over 0.10) | 0.503 / 0.525 / 0.508 | 0.5333 |
| D (null integrity) | **+0.0169 ± 0.0021** | \|D\|+5·seD < 0.10 | **clean** (0.0274) | ~0 | 0 |

**Verdict: PASS-CAUSAL.** Same frozen theory constants as every Heron flight — no retuning. This is the
campaign's **first cross-VENDOR causal certification** and its first result on non-IBM hardware.

## What it means
Indefinite causal order is **not an IBM/Heron artifact**. The quantum switch's causal witness certifies on
Rigetti superconducting hardware (different vendor, fab, and native gate set — Rx/Rz/CZ, angle-restricted)
against the identical bounds. Cross-*vendor*, same-*modality* portability established. The device ranks:

> **kingston 1.95 ≥ marrakesh 1.90 ≥ fez 1.89 ≫ Rigetti Cepheus 1.11** (W), and on capacity
> 0.50-class (Heron) ≫ 0.27 (Rigetti). The court travels across the vendor boundary, but Rigetti is a
> markedly *weaker* causal chip — it still certifies, at ~50σ, but the witness runs at ~59% of Heron's value.

## Calibration — the binary PASS hit, the W magnitude missed
Pre-filed: **PASS-CAUSAL ~0.80 (HIT)**, W ~1.5–1.9 (**MISSED** — actual 1.11, below the predicted band),
capacity below Heron (hit direction). The named failure mode (witness decoheres to FAIL/NO-TEST) did **not**
occur — it passed cleanly.

**The lesson (kept in the ledger):** I raised confidence and narrowed the W band to 1.5–1.9 *because* the
pinned pair's CZ error (0.00305) was comparable to IBM's. That reasoning was wrong. **Comparable single-CZ
error did NOT predict comparable witness fidelity.** The switch witness depends on the *whole* transpiled
circuit — readout error, idle/coherence during the ~22-depth circuit, and single-qubit gate fidelity — not
just the one entangling-gate error I anchored on. Rigetti matches IBM on CZ error but runs the full witness
at ~59% of Heron's value. Rule: **do not predict a composite-circuit fidelity from a single-gate error;
the depth-integrated error budget dominates.** (This is the F57–70 lesson generalized across vendors.)

## Caveats carried
- Placement: pinned via verbatim box to physical [0,1] (a top-5 CZ edge, err 0.00398); controlled, not Braket-rewired.
- Single window (same-instrument, not same-instant) — identical scope to the Heron flights.
- Integration path: `backend.run(native=True)` (Target-native angle-restricted compile + verbatim box). Three
  earlier submission attempts failed at task creation ($0 each) — documented in the runner + canary commit.

## Next
The cross-MODALITY leg (IonQ Forte-1 trapped-ion) remains the bigger prize and the decider: trapped ions have
no CZ Z-bias and all-to-all connectivity, so a certification there kills "Heron/superconducting artifact"
entirely. Cost gate: full frozen axis ~$9k at $0.08/shot (witness-only ~$1.3k) — a Creator budget decision.
