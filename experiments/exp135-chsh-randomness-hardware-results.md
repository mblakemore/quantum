# Exp135 Hardware Results — CERTIFIED RANDOMNESS ON ONE CHIP: The Witness Holds, the Scope Corrected

**Author**: Whisper (DC15W), C4676 (2026-07-14) · **Substrate**: claude-opus-4-8
**Job**: `d9an47mg26ic73dev0s0`, `ibm_marrakesh`, pair (1,2), ~168k shots, one window
**Verdict**: **CHSH-WITNESS-CERTIFIED — all four frozen gates PASS; entropy reported in three correct tiers, NOT over-certified**

## Headline

| Gate | Frozen condition | Measured | Verdict |
|---|---|---|---|
| **W1_WITNESS** (primary) | S > 2 + 5·SE (device behaves quantumly) | **S = 2.7522 ± 0.0141** = **53σ over 2** | **WIN** |
| **W2_TSIRELSON** | S ≤ 2√2 + 5·SE (apparatus honesty) | 2.7522 < 2.8284 | **PASS** (97.3% of Tsirelson) |
| **W3_NULL** | no-entanglement arm S ≤ 2 | 0.0363 ± 0.0141 | **PASS** (dead at 0) |
| **G_SENT** | sentinels ≥ 0.95 | 0.9952 / 0.9875 | PASS |

Pre-filed band [2.65, 2.78] — HIT. The CHSH violation is certified at **53σ over the local-
hidden-variable bound**: the device behaves quantumly, and a no-entanglement classical mimic
(null arm, S ≈ 0) cannot reproduce it.

## The entropy accounting — three tiers, kept separate (the corrected scope)

| Tier | Quantity | Value | Status |
|---|---|---|---|
| 1. **Witness** (gated) | S | 2.7522 (53σ) | device is quantum; classical mimic excluded |
| 2. **Trusted-device** (usable *under device-trust*) | Born-rule H_min | **1 bit / measured qubit** | CHSH is the health-check that the device behaves quantumly; certification rests on the trust, not Bell |
| 3. **DI counterfactual** (reported, **NOT usable**) | DI H_min(S) | **0.5928 / use** | what the DI bound *would* give *if* loopholes were closed — no-signaling is unmet on one chip, so this is a what-if, never a certificate |

The load-bearing correction (advisor, pre-freeze): the DI bound converts CHSH→entropy **only
under no-signaling between the two measurement sites**, which two qubits sharing control lines,
calibration, and readout do **not** enforce — a deterministic device with shared control can
output S = 2√2 at zero entropy. So the 0.5928 is quarantined to tier 3, and there is **no
"certified bits > 0" gate**. This is stronger than the campaign's usual interpretive caveats
(F101 "not time travel", F107 "not Holevo"): there the measured effect was real and only its
*interpretation* was qualified; here the DI *quantity itself* evaporates without no-signaling.

## What this establishes

- A **quantum-behavior witness** at 53σ, and the campaign's **randomness-primitive entry done
  right**: a clean, reusable account of what an on-chip CHSH violation *does* certify (the
  device is quantum; a health-check enabling trusted-device randomness at 1 bit/qubit) and
  *does not* (a device-independent randomness certificate).
- The honest next step, flagged not claimed: a genuinely loophole-closed or **semi-DI**
  certificate needs a *different protocol with its own bound* — dimension-bounded
  prepare-and-measure, or a one-sided **steering** inequality (one-sided trust suits a single
  chip naturally) — not the DI CHSH bound relabeled.

## Bookkeeping

Noiseless S = 2.833 (≈Tsirelson), null 0.000. Lint 4/4. Audit: main arm 1 CX, null 0 CX, 10/10
pubs. Predictions: W1/W2/W3/G_SENT all HIT (S in band). Results: `results/exp135_hw_results.json`.
This is the cheap-honest-path toward the harder real primitive the Creator's guidance names —
the scope correction is the deliverable, the number is honest about what it is.
