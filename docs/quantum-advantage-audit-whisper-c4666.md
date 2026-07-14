# Have We Found Quantum Advantage? — The Honest Audit

**Author**: Whisper (DC15W), C4666 (2026-07-13), answering the Creator's direct question.
**Companion action**: Exp126 (magic-square game, `d9akl8fu62qs738o68pg`) — flown the same cycle this audit was written and since **landed as F106**: contextuality certified at **196σ** over an enumerated classical ceiling (measured 0.96901 vs 8/9), completing the no-go triptych (Bell · causal order · contextuality).

## The one-line answer

**Yes — repeatedly, in the strict sense of beating exact classical theorem ceilings at 5σ–341σ, across games, communication, thermodynamics, and information. No — not yet in the popular sense of a computational speedup, and F54 quantifies exactly why. The creative frontier that could change the second answer at our depth is the shallow-circuit (BGK-class) separation — since flown as the F113 apparatus, but the advantage there is theorem-carried (asymptotic), not a run-carried speedup at the n=4 flown, so the second answer stands.**

"Quantum advantage" is not one claim; it is five different scoreboards. Here is where the campaign actually stands on each, receipts attached.

## Scoreboard 1 — Computational speedup (time-to-solution): **NOT FOUND, with receipts**

- F54: the Grover/QAE speedup that would beat classical Monte Carlo needs ~10⁴ two-qubit gates; the scrambling wall is ~10³ (F05). A 10× depth deficit that no constant-factor stack closes.
- Exp33: the QAOA utility ceiling co-locates with the same wall. F62: textbook error correction adds more noise than it removes on this substrate.
- Honest context: no one else has an uncontested NISQ speedup either, outside sampling tasks whose classical hardness is contested. Our contribution here is the **measured wall**, not a speedup.

## Scoreboard 2 — Provable-bound game & correlation advantages: **FOUND, the campaign's core genre**

Every entry beats an *exact theorem ceiling* for classical (or causally ordered) resources, pre-registered, on silicon:

| Advantage | Ceiling (theorem) | Measured | Clearance | Finding |
|---|---|---|---|---|
| Causal discrimination game | 0.8695 (SDP, all definite-order processes) | 0.9769 | **216.8σ** within-run; **0.3 pp two-chip concordance (~34σ) is the physical carrier** (replicated 0.9738 / 201σ cross-chip) ([audit C4714](adversarial-audit-F82-causal-game-sigma-whisper-c4714.md)) | F82 |
| Superdense coding | 0.5 exactly (unassisted classical) | 0.9688, 1.77 bits/qubit | **341σ** | F87 |
| Capacity activation | 0 exactly (each channel & every causal composition) | 0.0436 bits/use | **55.6σ** (N=3: 61.7σ) | F85/Exp106 |
| Bell/CHSH | 2 exactly | 2.74; repeater arm survives two swaps | ≥15σ | F01/F91/F93 |
| **Contextuality game (magic square)** | **8/9 exactly (enumerated in-code, 4096 strategies)** | **0.96901** | **196σ**; worst context r3c3 wins at 37.8σ, all 4 gates PASS | **F106/Exp126** |

These are *measurable quantum advantages* in the resource-theoretic sense: a referee with the transcript and the theorem must conclude no classical strategy produced the record.

## Scoreboard 3 — Thermodynamic advantages (tasks forbidden to ordered/classical machines): **FOUND**

- ICO refrigeration: splitting forbidden to every ordered process, 21.1σ (F86); native-fluid retest colder than the coldest reservoir at 5σ (F88); strictly exceeds coherent path-control at ~20σ with the theory ratio 2.00 landing in-band (F89).
- The engine — F95's full thermodynamic cycle with the books audited. Its enabling resource is F94: a **certified working resource** — a population inversion the individually-passive baths alone cannot reach (p₁|₋ = 0.5509, +10.6σ; both baths passive at 5σ), **routed** from control-coherence + demon-information through the switch (a router, not a battery), and **pre-ledger** — the pre-registered demon-ledger work column is not yet computed, so a certified resource, not a closed engine cycle ([audit C4717](findings/adversarial-audit-F94-ico-engine-whisper-c4717.md)). Certified negative local energy (F97).
- Scope kept honest: these are resource advantages per-interaction, not power-plant claims; and the H4 arc closed with the finding that the *coherent-erasure* advantage is real directionally but **below NISQ's 5σ certification floor three instrument-walls deep** (F104/F105/Exp125c) — the null is part of the audit.

## Scoreboard 4 — Information-theoretic certifications impossible classically: **FOUND**

- Negative conditional entropy S(B|A) = −0.855 at 42σ direct (F105 elevation), −0.0986 at 5σ from banked data alone (F103). Classically S(B|A) ≥ 0 — the sign itself is the advantage.
- Zero-capacity transmission (above) and the heralded-mirror recovery of definite-order-inaccessible information (F99, 56σ) sit in the same class.

## Scoreboard 5 — Metrology: **AT THE BOUND, not yet a scaling win**

F81 saturated the quantum Cramér–Rao bound on a real financial distribution (err 0.0003); the 344× amplitude-estimation gain (F51/F78) is vs naive readout, not vs an optimal classical estimator — labeled as such. The scaling advantage (Heisenberg vs standard quantum limit) is untested by us — see frontier item (c).

---

## The creative frontier — ranked routes to a NEW measurable advantage

**(a) THE COMPUTATIONAL ONE — BGK shallow-circuit separation (flown as F113, Exp127-class).**
Bravyi–Gosset–König (Science 2018): constant-depth quantum circuits solve the 2D Hidden Linear Function relation problem with certainty, while ANY constant-depth bounded-fan-in classical circuit is provably capped — an **unconditional computational separation** (QNC⁰ ⊋ NC⁰), no hardness conjectures. It is the only *computational* advantage theorem that lives at exactly the depth we own, and its core resource is the same magic-square nonlocality Exp126 certified (F106, the HLF gadget embeds magic-square games in a grid). Standing rule applies before freeze (C4523 pattern, validated again at Exp105): **pull the exact classical success bound for our instance size from the paper — advantage bounds are measure-dependent** — and grade against the noisy-shallow-circuits follow-up (Bravyi et al. 2020) for the fault-line. **Flown as F113** (constant-depth 2D-HLF solver on silicon, P(valid) 0.9017, full solution-coset, O(1) depth). The scope earned is precise: the separation is **asymptotic** (as n grows), so at the fixed n=4 flown a constant-depth classical circuit can also solve the instance — the **advantage is theorem-carried, the on-chip result is the apparatus**; the 437.8σ is fidelity over the uniform-random floor 0.25, not a beaten classical bound; and the magic-square/contextuality link is theory-associated (BGK-2018 solver flew, BGKT-2020 gadget did not) ([audit C4715](findings/adversarial-audit-F113-computational-bridge-whisper-c4715.md)). The honest bridge from "correlation advantage" to a *computational-genre* apparatus on silicon — not a raw n=4 speedup.

**(b) The cheapest possible advantage — 2→1 quantum random access code.** One qubit encodes two bits so either can be recovered on demand: quantum 0.8536 vs classical 0.75 exactly. Single-qubit circuits, F82-court grading, near-zero budget. **Flown as F107** (Exp128, qubit 75, **zero two-qubit gates** — the campaign's first zero-2q-gate advantage flight): certified inside the two-sided band, **110.5σ above the classical law** and 5.2σ below the quantum optimum — adds the *communication-resource* column.

**(c) The practical one — GHZ metrology vs the standard quantum limit.** N-qubit entangled probes beat the 1/√N separable-probe limit toward 1/N. Frozen gate: measured phase variance below the *enumerable* separable bound at fixed N and equal shot budget. Reuses the delay-ladder, placement stack, and phase-blind estimator (F100 law). **Flown as F108** (2.848× Fisher info vs executed SQL, 168σ, N=3; persists to N=5, F109) — a certified N=3 *local* Fisher-information advantage. Not yet the *deployment* advantage: the k=3 super-resolution is also a 3-fold phase ambiguity (Higgins-2007 cascade for absolute phase), and under time-optimized interrogation with dephasing the *scaling* advantage is Huelga–Plenio-limited ([audit C4716](findings/adversarial-audit-F108-metrology-whisper-c4716.md)).

**(d) Certified randomness from banked CHSH 2.74** — semi-device-independent entropy expansion, assumptions stated; zero new flights for the first leg (F103 precedent: negative-ink certifications from banked data). **Flown as F117** (Exp137): rigorous *one-sided* device-independent randomness — **0.65 private random bits/use at 5σ** from measured assemblage data (no Werner model), the one rung a single chip genuinely holds.

**(e) The zero-qubit advantage — the QPU weather service** (bridges doc, C4522): our sentinel-vector + quiet-qubit picker out-predicts the vendor's published calibration data. A real, monetizable scheduling advantage for anyone using these machines — no quantum speedup required.

## Bottom line for the Creator

The campaign has already found **measurable quantum advantage** — the defensible kind, where the ceiling is a theorem and the clearance is hundreds of σ — and Exp126 has since **added contextuality, the third great no-go, to that ledger (F106, 196σ)**. What we have *not* found (and have honestly measured the wall preventing) is a computational speedup. The creative route that could add the word "computational" to our advantage ledger without leaving our depth budget is **(a)**: the shallow-circuit separation, built from the same magic-square resource — since flown as the F113 apparatus, though the separation stays theorem-carried at n=4, not a run-carried speedup. **Update since this audit was written**: all four flight-ready frontier routes have flown — QRAC (b → F107), BGK (a → F113), GHZ-SQL (c → F108), certified randomness (d → F117) — plus the companion contextuality game (F106). The open frontier is now the zero-qubit QPU weather service (e) and the true BGK computational *separation at scale*.
