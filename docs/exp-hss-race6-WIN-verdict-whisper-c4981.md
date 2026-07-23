# Exp-HSS Race 6 — 🏆 VERDICT: THE ADVANTAGE WINS — first fully-fenced, court-graded runtime advantage of the campaign

> **⊘ SUPERSEDED (C4996, 2026-07-23 — same day, own red-team, pre-submission).** The F121 runtime-advantage claim recorded below is RETIRED: the planted MM problem's algebra falls to a classical 41-query linear-structure solve (~0.25 ms vs the 1,818 s simulation floor), run on our own sealed instance and confirmed independently by all three court seats. **F120 (shot-axis decoder) stands as an instrument result — not an advantage. F119 under re-audit.** This record is kept as-was, dated — see [the red-team finding](exp-hss-race6-REDTEAM-whitebox-break-whisper-c4996.md). Read every "advantage/WIN" statement below through that lens.

*Whisper C4981, 2026-07-23, substrate claude-fable-5. Frozen card + 2 pre-submission amendments
(3-of-3 each): [exp-hss-race6-prereg-FROZEN-whisper-c4981.md](exp-hss-race6-prereg-FROZEN-whisper-c4981.md).
Job `d9gps850k0jc738h6blg`, **ibm_kingston**, 58 pubs, 360k shots, **104 s QPU** (pool ≈ 2,427 s).
Court: Ember sealed/revealed/adjudicated (#657/#670/#672), Elder graded (#674, quantum@52c689c),
Whisper flew/decoded blind. Wall: `results/exp_hss_race6_quantum_wall.json`.*

## The result

**The blind frozen decoder recovered the sealed 40-bit hidden shift of a t=80 (80-T-gate,
10-CCZ) Roetteler hidden-shift circuit EXACTLY — s ⊕ ŝ = 0 — at d2q=167 on a pre-gate-certified
clean kingston register, from 12,500 shots, for a re-measured quantum wall of 3.82 s (anti-
flattering attribution) against Elder's frozen edge-robust classical band: 476× faster than the
FASTEST plausible classical solver (edge-4500× floor, 1,818 s) and ~6,100× faster than the
operating estimate (23,460 s). The pre-registered WIN rule — exact recovery + wall ≤ 1/10 of the
band's lower edge at EVERY edge — is MET with a 48× margin at the harshest edge. All three court
seats concur. 🏆**

## Every fence held

| Fence / rule | Requirement | Outcome |
|---|---|---|
| Rule-1 clean routing | clean candidates exist | marrakesh: ABORTED honestly (0/100) → 3-of-3 die amendment; kingston: 100/100 |
| Depth cap 200 | d2q ≤ 200 | **167** ✓ (33 margin) |
| Register unification | twin/ladder share race register ≥30/40 | **37/40** ✓ |
| Clean-ladder PRE-GATE | both t=0 rungs EXACT before seal opens | **EXACT ×2** (55, 165), zero flips ✓ |
| Twin gate | exact at race depth | **EXACT at 167** ✓ |
| Decoder | frozen calibrated majority, no rescue, 2⁻⁴⁰ null | six-way blind consensus; race exact from 12.5k ✓ |
| WIN wall | ≤ 181.8 s (1/10 of harshest edge) | **3.82 s** — 47.5× under ✓ |
| Court | 3-of-3 sealed, ŝ-before-reveal | commitments verify; zero disputes ✓ |

Robustness (Elder #674): even the maximally conservative wall (full 200k budget = 57.8 s) clears
the bar 3×; the graded 3.82 s charges cal overhead onto race shots (stricter than #605 required).

## Fences, printed on the result (Elder C6563 anti-flattering discipline)

One HSS instance family (Maiorana–McFarland, n=40, t=80, planted-shift, self-verifying); one die
(ibm_kingston, this calibration window); classical arm = Elder's frozen edge-robust band gated on
the fastest all-core tool — the classical side got its best tool and still loses 476×; joules
one-sided (QPU power unpublished, G2); **supersedable-by-design**: a classical solver beating
1,818 s on this family retires the number — that is the Tracker mechanism working, and it is
printed here per the standing rule. This is a best-known-solver engineering race, NOT a
complexity theorem — Exp142/F119 remains the theorem-floored result in its distinct
sample-complexity currency; the two now bracket the campaign's advantage answer from both sides.

## How it was won (the arc, six flights, 789 s QPU)

The C4971 NO-GO said the window was closed. C4974 found the window was measured with the wrong
observable — **the shot axis is a code** — and each subsequent fold descended one layer:
observable (C4973) → placement/endianness (C4976) → granularity (C4977) → qubit tilts (C4978) →
register quality (C4980) → device topology (C4981 marrakesh abort) → **WIN (C4981 kingston)**.
Six pre-registered folds/aborts, every branch honored, zero grading disputes; the falsified
hypotheses (window-closed; decoder-side-alone) were as load-bearing as the confirmations. The
final instrument stack: temporal-redundancy decoding (shot-axis code) + whole-chip readout
calibration + calibrated per-bit majority + depth-matched twin + clean-ladder pre-gate + sealed
3-of-3 commit-reveal court + a frozen classical band that graded honestly from first co-verify
to WIN.

*The campaign's largest standing negative is converted. Contact: Mike Blakemore.*
