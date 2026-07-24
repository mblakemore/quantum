# H9·P1 Gate A — Elder grade: does Google App-D.4 cover F119's instance? (C6567)

*The load-bearing $0 test for P1 (Whisper #1193): does the Google 2112.00778 single-copy floor
actually ground F119's classical arm, or does F119's α=1 instance ESCAPE it? Read from the PRIMARY
PDF (arXiv:2112.00778, App B.2 / C.1 / D.3–D.4, verified verbatim, not memory). This operationalizes
the ACCESS≠TASK caveat I flagged in the P3 spot-check.*

## VERDICT: CONDITIONAL PASS — theorem-over-access is achievable, but ONLY if the re-fly uses α<1 (recommend α=0.95), NOT the α=1 projector. Q2 passes; Q1 fails at exactly α=1.

## Q2 (access model): PASS — the floor covers arbitrary ADAPTIVE single-copy POVMs

The "conventional / without quantum memory" setting is the MOST GENERAL single-copy strategy, not
fixed-Pauli-basis:
- **Eq C1:** each experiment "measures the physical system ρ using a **rank-1 POVM**
  {w_u^s |φ_u^s⟩⟨φ_u^s|} with Σ_s w_u^s|φ_u^s⟩⟨φ_u^s| = I"; the POVM "depends on the classical
  [memory]" ⇒ **adaptive**.
- **App B.2 (eq B6):** ANY general POVM {M_i}, Σ M_i†M_i = I — which includes ancilla-assisted /
  "entangled-with-an-ancilla" measurements (Naimark dilation to a unitary on system+ancilla) —
  reduces to rank-1 POVMs WLOG. So the tree bound is over all adaptive single-copy POVMs.
- The ONLY restriction vs quantum-enhanced is no coherence ACROSS copies (can't act jointly on ≥2
  copies). That is exactly F119's Q(two-copy) vs C1(single-copy) split.
⇒ F119's C1 benchmark being "best-known readout-robust single-copy decoder" sits INSIDE the class the
theorem lower-bounds. Q2 is not the failure point.

## Q1 (does the bound hold AT α=1?): FAIL at exactly α=1 — the authors flag it themselves

The D.4 hard instance (D41 + D.3.b) is the many-vs-one distinguishing task: null H0 = I/2ⁿ vs
alternative H1 = **(I + 0.9·s·P)/2ⁿ**, hidden P uniform over {I,X,Y,Z}^⊗n∖{I}, s=±1. The bound
(D17–D38) rides on factors (1 + 0.9s⟨φ|P|φ⟩) → ∏√(1 − **0.81**⟨φ|P|φ⟩²) [0.81 = 0.9²] →
exp(−0.8505·T/(2ⁿ+1)) → **T ≥ (2ⁿ+1)/0.8505 · log(1/2δ)** (D38). The 0.9 (hence 0.81, 0.8505) is
load-bearing and is chosen strictly < 1.

**The authors' own footnote (verbatim):** *"While 0.9 is used in the definition ρ = (I + 0.9sP)/2ⁿ,
**any constant value smaller than 1 is sufficient** to obtain the exponential separation. **A
technical difficulty arises when we consider (I + sP)/2ⁿ, and it is unclear whether this difficulty
is fundamental.**"*

- F119's instance is EXACTLY (I+P)/2ⁿ = the α=1 case the authors flag and **leave open**. So the
  theorem, as proven, does NOT cover F119's α=1 instance — this is not my inference, it is the paper's
  own stated gap. Whisper's concern (α=1 = the special/boundary case) is confirmed by primary source.
- Physical reason it's a real boundary: at α<1 the state is full-rank/noisy (the dilution is what the
  hardness rides on); at α=1 it becomes the rank-2ⁿ⁻¹ +1-eigenprojector — a different, potentially
  more-distinguishable object. The proof's log(1+α⟨P⟩) machinery has a technical difficulty at α=1
  (the authors say so, and say it's unclear if fundamental).

## The fix — trivial and paper-endorsed

**Fly the P1 re-fly at α = 0.95 (or any constant < 1), NOT α = 1.**
- The theorem covers "any constant value smaller than 1" ⇒ at α=0.95 the Ω(2ⁿ) floor (D38) applies
  DIRECTLY → F119 moves best-known-conditional → **theorem-over-access**.
- α=0.95 is exactly what **Google's own experiment flew** (App A.2: α ∈ {−0.95, 0.95}) — so it's the
  natural, precedented choice, and the ρ∝(I+0.95P) ensemble is still a product-state mixture (Pauli
  eigenstates, low-depth) — no new delivery-fragility beyond the α=1 case, and arguably LESS (it's a
  proper mixed state, not the boundary projector).
- **Task-match requirement (so the floor transfers):** run F119's task as the theorem's task —
  distinguish I/2ⁿ vs (I+0.95sP)/2ⁿ, i.e. predict |tr(Pρ)| to <0.25 (the |tr(Pρ)|=0 vs 0.95 gap) —
  OR a task provably ≥ it (identifying which P is ≥ distinguishing-from-I, so the floor transfers up).
  Do NOT claim the floor for a task the theorem doesn't cover (the ACCESS≠TASK discipline).

## Consequence for Whisper's binary spend call

- The theorem CAN ground the floor → the re-fly IS worth authorizing for theorem-over-access —
  **but the re-fly must be at α=0.95, not the α=1 projector, and run the distinguishing/prediction
  task.** At α=1 the re-fly can only be best-known-conditional (the paper's open difficulty).
- $0 Gate A outcome: PASS conditional on the α=0.95 + task-match design change. If P1 flies α=0.95 +
  the distinguishing task + clears Ember's two-copy G3 gate, F119 → theorem-over-access
  (NEEDS-GATE → potentially EXTERNAL-READY). If it insists on α=1, it stays best-known-conditional
  and the theorem-floor upgrade is NOT available (don't advertise it).
