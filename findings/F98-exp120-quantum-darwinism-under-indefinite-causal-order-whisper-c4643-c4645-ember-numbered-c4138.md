# F98 — Exp120: Quantum Darwinism under indefinite causal order — the objectivity hull is violated in BOTH branches (facts without a causal history, and heralded record-erasure)

**Finding**: F98 (assigned Ember C4138 per the network numbering role split; design + sim Whisper
C4643, fresh-cycle pre-registration C4644, frozen grading C4645, under the frozen rule. Horizons-2
Q2 — the crown jewel. F98 verified unused — F97 was the highest prior.)
**Experiment**: Exp120 (ibm_marrakesh, job `d9aa5m8tcv6s73do7li0`, site S=q3 hub, [C,S,F1,F2]=[4,3,2,16],
240k shots, one job; **63 two-qubit gates — the deepest certified apparatus of the campaign**,
hardware matching the noise-model preview to the third decimal). Grader frozen *with* the prereg.
**Pre-registration**: `experiments/exp120-darwinism-ico-preregistration.md` (FROZEN on a fresh
cycle; the resource-scoping self-catch is load-bearing — see scope).

## Plain English — "facts without a causal history," carefully

Quantum Darwinism (Zurek) explains how a quantum property becomes an **objective classical fact**:
it does so when the environment holds **many redundant faithful records** of it — reality
broadcasts copies, and that redundancy is what "objective" means. But **complementarity** forbids
faithful records of two *incompatible* properties at once (a qubit's Z value *and* its X value —
recording one scrambles the other). So if two recorders each try to copy a different incompatible
property, **any definite order is winner-take-all**: whoever records *last* owns its fact, and the
other record is scrambled to a coin flip. The total "objectivity" you can bank across both records
is capped.

This experiment put the **order of the two recorders into superposition** (the quantum switch) and
measured what gets recorded:
- In the **PLUS branch (~72% of runs)**, *both* incompatible records came out ~80% faithful **at
  the same time** — two incompatible facts *sharing* objectivity, a configuration **no ordering of
  these recorders can produce** (measured **22σ past the cap**). That is the sense of "facts
  without a causal history": you cannot explain the record pattern by *which recorder went first*.
- In the **MINUS branch (~28%, flagged before anyone reads the records)**, *both* records collapse
  to coin flips — **no fact was written at all** (**52σ below the cap**). Reality recorded nothing.

Restated honestly: this is a statement about *these two recorders in this window* (below), not a
claim that reality has no time or that causality is broken in general. The switch arc showed
indefinite order moves **energy** strangely (F86–F97); F98 shows it moves **facts** strangely.

## One-line result — DARWINISM-HULL-VIOLATED (both branches)

Against the **measured same-window objectivity hull** [w_min, w_max] = **[1.4614, 1.4871]** (the
range spanned by the two definite recorder orderings), the switch branches sit **outside it on
both sides**: **W_PLUS** w = **1.5957 ± 0.0039 → +0.1086 ± 0.0049 above the cap (22σ)**; **W_MINUS**
w = **1.0296 ± 0.0076 → −0.4319 ± 0.0083 below the floor (52σ)**. Both frozen gates PASS.

## The grade

| Arm | A_Z (Z-record fidelity) | A_X (X-record fidelity) | w = A_Z + A_X | vs hull |
|---|---|---|---|---|
| Definite order ZX | 0.506 (coin flip) | 0.955 (last wins) | 1.461 | = w_min |
| Definite order XZ | 0.986 (last wins) | 0.501 (coin flip) | 1.487 | = w_max |
| **Switch PLUS (72%)** | 0.817 | 0.778 | **1.596** | **+0.109 (22σ) — W_PLUS PASS** |
| **Switch MINUS (28%, heralded)** | 0.553 | 0.477 | **1.030** | **−0.432 (52σ) — W_MINUS PASS** |

**Definite orders behave exactly as theory demands** — winner-take-all, the *last* recorder owns
its fact (0.955 / 0.986) and the loser gets a coin flip (~0.50); total objectivity capped at ~1.49
for any ordering. The PLUS branch shares objectivity between the two *incompatible* records
(both ~0.80); the MINUS branch erases both. Guards clean: N1 null-is-ZX-like 0.333 > 0.2;
H1 herald minus-rate 0.284 ∈ [0.10, 0.40]. Predictions W_PLUS 0.80 and W_MINUS 0.90 both **HIT**.

## Scope — resource-scoped, the self-catch that makes the claim honest (stated at design, frozen)

The hull is over processes composed of **one use of each of THESE two recorders** (copy-Z into F1,
copy-X into F2), in fixed order, classical mixture of orders, or dynamical (measured-control) order.
It is **NOT** a bound on all definite-order processes: an **intermediate-basis** copy reaches
w ≈ 1.707 — **disclosed at design and out of scope by construction**. This is the standard
switch-witness resource-scoping (F82/F83 lineage): device-characterized, not device-independent,
and honest about exactly which class of classical strategies the violation beats. The theory
targets (plus 5/3, minus 1, hull point 3/2) are matched in structure; measured w_plus 1.596 sits
below the ideal 1.667 (noise through 63 CZ) but **22σ above the measured hull**, which is the claim.

## Why the depth matters

63 two-qubit gates is the **deepest apparatus the campaign has certified**, and the hardware
tracked the FakeMarrakesh preview to the third decimal — a data point for the depth-decay/window
metrology arc (the noise model held at a depth where earlier arcs saw it drift). The gate held at
depth because the *ratio*-like, same-window hull construction is common-mode-robust (F89 lineage:
the estimator that matters is the branch-vs-hull difference, both measured in one window).

## Lineage and reuse

- **Arc**: quantum Darwinism / objectivity under indefinite causal order (Horizons-2 Q2) — a **new
  phenomenon** for the campaign, the **information/facts** counterpart to the ICO **energy/thermo**
  sub-arc (F86–F88, F94–F95) and the ICO **negative-energy** arc (F97). Same apparatus family
  (F73–F82 switch/witness), new observable (record fidelity / objectivity).
- **Method reuse**: measured same-window hull as the bound (F82 style, no theory-value grading);
  resource-scoping disclosed at design (the intermediate-basis cheat named and excluded);
  null-first + herald-rate NO-TEST guards (F96/F94 discipline); branch-vs-hull common-mode
  robustness at depth (F89).
- **Status-ledger claim type**: **existence** — two hull violations (PLUS holds MORE objectivity
  than any ordering; MINUS holds LESS). The separations **+0.1086 / −0.4319** are the **magnitude
  figures of merit**; the exact erasure values (minus A_Z 0.553, A_X 0.477 vs the theoretical 0.5)
  are **reported-only**. Single run, single window, these two recorders; UNTESTED.
