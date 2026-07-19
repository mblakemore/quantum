# Exp203b — THE COLLISION LEDGER: NOT HELD (registered), the law standing, a retraction owed

**Whisper C4899, 2026-07-19. Job `d9ee989htsac739e5e20`, `ibm_fez`, 45 pubs, seed 0.
Prereg: predictions frozen in [C4898 §4](../docs/collision-corrected-ledger-whisper-c4898.md)
BEFORE flight authorization; operationalization committed pre-submit (`3bbfb23`).**

## Verdict

**REGISTERED VERDICT (G0∧P1∧P2∧P3∧P4): NOT HELD** — G0, P2, P3, P4 missed; **P1 HELD**.
Three separate findings inside the miss, each with receipts:

## 1. The XOR ledger law: replicated, now at 0.6% — and both fixed points demonstrated

P1 held in **both** arms: max |residual| **0.0064** across all ten (arm, dose) points
(203's post-hoc fit: 0.012; the naive AND-model: 0.163). Checkpoints: plain acc(π) =
0.4946, twirled 0.5039, both in [0.47, 0.53]. And an unplanned bonus with its own meaning:
the twirled arm — instrumentally broken (below) — sat at acc ≈ 0.50 at **every** dose,
which is exactly the XOR law's *other* fixed point: **p_n = ½ ⟹ acc = ½ for any e_r**
(a fabric coin XORed with anything is a coin). The broken arm obeyed the law it was
supposed to test. **The collision ledger's acceptance arithmetic is now 2-for-2 across
windows and compilations, at the sub-percent level.**

## 2. The plain arm FITS the static-Pauli collision model — C4898's "instrument" claim is RETRACTED

With the anti-folding compilation (2 CX at every dose, one layout — verified at compile:
2q = 5 uniform including θ=0), the plain arm's coherence residuals are
**+0.000 / −0.025 / −0.038 / −0.012 / −0.013** — inside the ±0.06 band the *twirled* arm
was supposed to need twirling to reach. **The +0.199 "non-Pauli deviation" of Exp203 is
GONE.** Diagnosis: in 203, the θ=0 anchor (cry folded → zero 2q gates → free layout)
was measured on *different physical qubits* than the interior doses — so c0 and m_odd
parameterized a model for the wrong hardware, and the growing "deviation" tracked
collision weight only because the model error scaled with dose. **C4898 §3's
interpretation — "a ledger-based detector of non-Pauli noise" — is hereby RETRACTED**
(addendum added to that doc): the deviation was the anchor-layout artifact in a second
costume, killed by the same structural fix that was aimed at its first. The F80 rule,
one flight late: what the whiteboard missed, the fixed compilation caught.

**The constructive result**: with honest same-layout anchors, the full collision ledger —
XOR acceptance + static-Pauli coherence bookkeeping — **describes the shield's books at
the 4% level with no exotic term.** The ledger is closed.

## 3. The twirl implementation is refuted as built — the echo lesson

The twirled arm is not a Pauli-twirled instrument; it is a destroyed one: acc(0) = 0.499,
c0 = **0.012** (G0 caught it: anchor floor 0.55). Autopsy, consistent with every number:
the per-slice {I,X} frames were inserted **inside the X⊗4-bracketed echo window**, so each
random frame toggled the precession sign mid-window and un-did the refocusing — each
instance accumulated an O(π) quasi-static Bell phase, making the X-parity a coin
(acc → ½, dose-independent ✓), killing pooled coherence (c0 → 0 ✓), and leaving erratic
per-dose post values of magnitude ~1/√8 (±0.1–0.3 ✓ — eight instances of cos φ that don't
cancel). The prereg's own scope line ("twirl scope is part of the diagnosis if P2 fails")
fired at maximum: **P2 was never tested — its instrument broke on contact with the echo.**
Friction-report lesson, filed: *twirling frames must be echo-compatible* — insert frames
in echo-symmetric pairs (or twirl the whole refocused window as one unit), never at
arbitrary positions inside a refocusing sequence.

## Scoreboard and consequences

**Budget predictions (graded straight)**: plain resid(π) ∈ [0.12, 0.28] → **−0.013, OUT**
(the retraction *is* this miss); twirled resid(π) ∈ [−0.06, 0.06] → untestable
(instrument dead, G0); P4 σ ~7 → 3.6 measured on an invalid comparison; acc(π) within
0.02 of 0.50 both arms → **IN** (0.495/0.504). 1/4 gradable.

**Consequences for the program**:
- The **XOR ledger law** graduates: sub-percent, two windows, two compilations, both fixed
  points seen. Fleet rule: shield acceptance under an engineered record dose is priced by
  XOR composition — and acc(π) = ½ is a free calibration checkpoint for any [[4,2,2]]
  postselection experiment.
- The **collision model with same-layout anchors** closes Exp203's G4 question: no
  non-Pauli term needed at the 4% level. Exp203's registered NOT HELD and this NOT HELD
  both stand; the physics question they bracket is answered.
- The **anti-folding doctrine** (manual ry–cx–barrier–cx) is validated end-to-end and
  should be standard for every dose-sweep with angle-parameterized 2q gates.
- An echo-compatible twirl replication is possible but LOW priority — the deviation it
  was built to certify no longer exists.

## Line

**We built an instrument to certify a mystery and the instrument's foundation fix
dissolved the mystery instead. The ledger closes at 4%; the law it rode in on holds at
0.6%; and the "new noise physics" goes back on the shelf, retracted by its own author.**
