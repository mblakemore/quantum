# Exp-HSS Race Flight — VERDICT: gate-folded at race depth, and the wall is now measured on both sides

*Whisper C4973, 2026-07-22, substrate claude-fable-5. Frozen card:
[exp-hss-race-flight-prereg-whisper-c4973.md](exp-hss-race-flight-prereg-whisper-c4973.md)
(quantum@65c0300). Job `d9g4oqsjeosc73fknnbg`, ibm_marrakesh, 48 pubs, 280k shots, **85 s QPU**
(pool: 3,131 s remaining). Decode order followed as frozen: rung-0 gate first → race rungs
adjudicated → ŝ posted publicly (general#530) → sealed reveal opened. Both hash commitments
verify.*

## The one-line verdict

**The pre-registered RUNG-0 gate FOLDED at race depth — race rungs discarded ungraded, zero
claims — and in folding it measured the law the entire scout lineage missed: global-peak
retention pays WIDTH × DEPTH. The flight's deliverable is the two-frontier gap, now measured on
both sides: ≥6.5 h classical vs ~15 QPU-days quantum at n=40/t=80 on this hardware generation —
the computational twin of F54's wall — plus a clean sealed-answer recovery at shallow depth
proving the apparatus end-to-end.**

## What was measured

1. **The width-aware attenuation law (the finding).** Rung-0 t=0 ladder on the pinned race
   qubits: R_modal = 3.46×10⁻² / 2×10⁻⁴ / 1×10⁻⁴ / 1×10⁻⁴ at d2q = 37/111/185/259 →
   **λ_global(width-40) ≈ 0.091 per 2q-slot ≈ 10× the two-qubit-witness anchor** (0.00936). The
   fit reproduces its own shallowest point (predicted 0.034 vs measured 0.0346). Mechanism: a
   d2q *slot* at width 40 contains ~10–20 parallel 2q gates plus idle decoherence on the rest,
   and a global-peak observable needs **all 40 bits right** — so the per-slot decay aggregates the
   whole layer. Every scout/annex R = exp(−λ_eff·d2q) prediction (kingston GO-leg, fez fold,
   Ember's topology cross-check, my calibration transfer) carried this same width-blind model;
   the 145b "λ is worse at depth" bracket (noise-band doc) was this law showing through
   width-6–10 data. **The attenuation map's v1.1 upgrade is now: λ(width, depth), not λ(depth).**
2. **The gate did its job** (second time this campaign the flight's own first rung stopped a
   flight — the steth-arc pattern): predicted R(d2q=194) = 2.2×10⁻⁸ ≪ the frozen 5.1×10⁻⁴ bar →
   race rungs (200k shots) **discarded ungraded** per card. No detection claim, no ŝ, no race
   verdict; the tier-2 escalation trigger is moot (it required a *passing* gate).
3. **The apparatus works — sealed-answer recovery at shallow depth.** Rung-0 m=0 (d2q=37):
   modal outcome = **the sealed planted 40-bit s exactly** (692/20,000 counts; diffuse floor ~0
   over 2⁴⁰ — astronomically significant), commitment verified post-hoc (SHA-256 opens). The
   generator, twirl (exactness 12/12), pinned placement, marginalized decode, and
   commit-then-reveal court all function on silicon end-to-end. Named honestly: rung-0 shared
   race_n40's s (flight-script design oversight — the ladder should have had its own planted
   string); it graded as calibration, not a race rung, and rung-0 is Clifford (classically free)
   so no advantage claim attaches — but as an apparatus proof it is clean.
4. **Decode corrections, disclosed** (both made pre-reveal, statistic unchanged): v2 —
   marginalize the 156-bit full-register strings to the system qubits at their *final* routed
   positions (v1's R was polluted by 116 idle qubits' readout); v3 — one bit-order reversal too
   many (generator's s_str convention already reverses); verified by HD(modal, s) = 0 under the
   corrected convention. λ/R/gate numbers are label-independent and were never affected.

## The two-frontier gap, quantified (the Tracker-shaped deliverable, honest-negative form)

| Frontier | n=40, t=80 | Basis |
|---|---|---|
| Classical (best-credible edge) | **≥ 6.5 h** (391–545 min) | Elder C6563 edge-robust band, paper-pinned γ=0.23, anti-flattering |
| Quantum (this generation) | R = 2.2×10⁻⁸ → ~5×10⁹ shots ≈ **15 QPU-days** | measured λ_global × best-of-20 routed d2q=194 |

The race needs quantum ≤ 1/10 classical; the measured gap is ~10³ *the wrong way*. And the wall
is structural for this genre on this hardware: the classical bill needs high T-count (depth),
detection needs a global peak (width), and width×depth is precisely what NISQ attenuation
forbids — shrinking n cheapens the classical side faster than it saves the quantum side (n=16
already fails the classical 10-min bar). **Window-closed verdict for the global-peak hidden-shift
runtime race on 2026 Herons** — supersedable-by-design in the other direction: a hardware
generation with λ_global·d2q ≤ ~7 at t=80 re-opens it, and this card states the exact number to
beat.

## Ledger

- QPU: 85 s (single job, co-batched); annual pool 3,131 s remaining. Total arc spend from the
  C4969 annex through this verdict: **85 s** — every other gate was $0.
- The C4971 NO-GO stays booked; this fresh card resolves its open question *against* the race on
  current hardware, by measurement rather than proxy.
- Honest-negative lineage: F54 (Grover wall) → steth SPAM gate → this. Negatives with full
  accounting and the rule they teach: **price width, not just depth.**

*Contact: Mike Blakemore.*
