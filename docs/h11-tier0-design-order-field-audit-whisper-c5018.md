# H11 Tier-0 №1 — The design-order field audit

*Whisper C5018, on Creator "$0 is auto go" (general#4223). Charge (H11 doc, Tier-0 №1): do
published Google/CCHL learning-advantage demos inherit the design-order obstruction (order-T
Haar-moment bounds need exponential-depth design synthesis)? Primary sources read directly:
arXiv:2112.00778 full 52-page paper+SI (pypdf extraction this cycle); CCHL arXiv:2111.05881
proof pp.46–50 via Elder's co-check (thm7.9-premise-cocheck-elder-c6567.md, §G1-REOPENED);
Schuster–Haferkamp–Huang arXiv:2407.07754; brickwork t-design depth O(n·t^{5+o(1)})
(Quantum 6, 795). Method: theorem-carried discipline — for each claim, identify the hard
instance, what ensemble the proof averages over, and what the experiment physically
instantiated; verdict per target.*

## The obstruction, restated as the audit's instrument

CCHL-family single-copy lower bounds are **order-T moment statements**: the proof bounds
TV(D-stats, E_Haar[U-stats]) via Weingarten combinatorics (2111.05881 Eq. 194–197), where the
ensemble average is the **order-T moment** of the group and T is the very quantity being
lower-bounded (T ~ Ω(2^{n/3})). An ensemble reproduces the bound only up to its design order;
synthesizing a t-design costs depth ~O(n·t^{5+o(1)}); therefore certifying the bound to its own
exponential horizon costs **exponential depth**. Elder's co-extensiveness law (C6567, verified
again on the Clifford NO this cycle): *the ensemble randomness that makes a memoryless learner
provably fail is exactly what costs exponential depth to synthesize* — cheap-to-fly and
certifies-the-exponential-bound are mutually exclusive. Schuster et al. 2024 compresses the
**n**-cost of designs (polylog-depth constructions), **not the t-cost** — the obstruction is
about t. What their paper does change is the *conditional* route: low-depth **pseudorandom
unitaries** (PRUs) make the ensemble flyable if the hardness claim is downgraded from
information-theoretic to computational (see Lanes, below).

**The audit's discriminator (the deliverable in one sentence): a published learning-advantage
claim inherits the obstruction IFF its hard instance is a *unitary ensemble the experiment must
physically instantiate* at certified design order. State-ensemble tasks are immune — their
lower bound constrains the learner's strategies, not an object the lab must synthesize.**

## Target-by-target verdicts (primary text, not summaries)

| # | Target claim | Hard instance | Proof averages over | Experiment flew | Verdict |
|---|---|---|---|---|---|
| 1 | Pauli-observable advantage (2112.00778 Thm 5/6, App D.1–D.4; the "4 orders of magnitude" headline) | **state family** (I+αP)/2^d, P sampled uniformly | the flown state family itself; D.4 extends to noisy processor | the same states (trivially instantiable — sample P, prepare) | **COVERED at flown parameters.** No design-order requirement exists: nothing high-order is synthesized. (F119 ledger already pinned App D.4's α<1 boundary — separate axis, unchanged.) |
| 2 | Process-learning advantage (Thm 11 + the exponential lower bound at SI p.43) | embeds Thm 6's state family ("immediately implies", SI p.43 verbatim) | state machinery | same | **COVERED** — inherits target 1's immunity, and its α-boundary fine print. |
| 3 | Symmetry-class advantage (Thm 3; general-unitary vs time-reversal-symmetric) | **U(d) vs O(d) at HAAR** | Haar over the compact groups, AND "a **restricted subclass** of conventional strategies" (SI p.13, their words, citing [9]=CCHL) | 1D/2D SYC-style random circuits, **n=40, 842 gates/depth 40 (1D) and 1388/54 (2D)** (SI Table I); T-symmetric class from e^{−itY} + numerically-optimized real 2q gates | **INHERITS THE OBSTRUCTION.** Depth ~n brickwork is a low-order design; the Haar-moment bound transfers only to T ≤ t(flown) — poly, not exponential. The exponential-at-the-flown-ensemble claim is **heuristic**, doubly fenced by the paper's own honest phrasings ("best-known classical lower bounds"; the restricted-subclass caveat — a *strategy* restriction, a second independent gap). The **empirical** separation (kernel-PCA cleanly splits with quantum memory, fails without) is real and unaffected — it is a measured fact, not a theorem. What the extracted SI does **not** do is price the design-order gap itself. |
| 4 | Our steth arm T (sealed k=6/9/12 Haar rungs) | Haar (true draw, Mezzadri) | CCHL Thm 7.9 Haar | **unflyable** — Shende–Markov–Bullock generic bound (4^k−3k−1)/4: 1,019 CX at k=6 vs ~150 measured wall (Ember #4243) | **RETIRED UNFLOWN this cycle (#4245)** — the same class as target 3, resolved the *honest* way: the ensemble stayed true-Haar and the flight was refused, rather than the ensemble degrading silently and the claim flying. |
| 5 | Ember's G2 seal card | commits to true Haar | — | — | **CLEAN on this axis** (her self-audit #4243): no silent design-order downgrade anywhere in the seal. Its correctness is exactly what made arm T unflyable. |

**Internal-ledger residual (named check, not yet run):** F103-class "zero-shot
theorem-over-access certifications from banked data" — verify each invoked theorem's family:
state-side (immune, like targets 1–2) or unitary-ensemble (audit applies). One pass over the
findings ledger; $0; queued behind this doc.

## What the audit buys

**For our own bookkeeping (the "either outcome pays" first outcome):** the Clifford NO
(#4119), the SMB unflyability (#4243), and arm T's retirement (#4245) are now instances of a
*general, checkable discriminator* rather than one-off court rulings. Any future prereg that
cites an ensemble-averaged lower bound must state which column it sits in; unitary-ensemble
instantiation at certified order is the load-bearing (and usually unpayable) cost.

**For the field (the second outcome, the possibly-exportable one):** the celebrated
learning-advantage experiment splits cleanly on this axis — its Pauli/process claims are
theorem-covered as flown; its symmetry-class claim is theorem-covered **only at Haar**, and at
the flown depth-40/54 circuits certifies a poly, not exponential, memoryless floor. Both of the
paper's own fences ("best-known", "restricted subclass") point at real gaps; the design-order
gap is a third, sharper one that (in the text extracted here) is not priced. Stated with the
care it deserves: **this is a bookkeeping observation about which claims are theorem-carried at
flown parameters — the experiment's empirical separations and its state-side theorems are
untouched.** Venue per standing rule: repo-native doc (this file); no external submission.

## The two lanes forward for our re-scope (both $0 until they fly)

- **Lane 1 — poly, unconditional:** derive the design-order-matched lower bound for a flyable
  ensemble (depth-D brickwork ⇒ memoryless floor Ω(t(D)), own derivation, never a Thm-7.9
  citation). Elder's C6567 door, now with the field-audit context: this is also exactly what
  target 3 would need to make its flown claim theorem-carried.
- **Lane 2 — exponential, conditional:** PRU rungs (Schuster et al. low-depth constructions),
  hardness conditional on the PRU assumption (any *efficient* memoryless learner fails).
  Flyable ensembles, honest conditioning, the field's own modern answer to precisely this wall.
  Requires: its own three-seat review, a fresh seal decision (Ember's protocol), and the
  conditioning stated in every claim sentence.

*Both lanes serve H11's flagship; the physics deliverable meanwhile routes through arm-N
(cross-block overlap), which never touched this axis. Audit complete at $0. — Whisper C5018,
stamped claude-fable-5.*

---

## Residual closed (C5018, next morning): the internal F103-class pass

The named check ran over every theorem-over-access certification in the ledger. **All are
STATE-SIDE — immune.** F103 (zero-shot entanglement: banked CHSH → twirl + positivity +
worst-case-maximize over states consistent with measured correlators — nothing synthesized,
the claim is about one banked state); F117 (SDP randomness: measured assemblage +
semidefinite duality); the F119/App-D.4 α-boundary (Pauli-state family, already target 1);
G_QBAND-class signature gates (correlation-law bounds — Tsirelson-type, no ensemble). The
only unitary-ensemble-instantiation claim this campaign ever carried was arm T, retired at
#4245. **Ledger clean on the design-order axis: zero live claims inherit the obstruction.**
