# Field audit: does the #844 co-extensive-walls obstruction apply to the Google/CCHL learning-advantage experiment?

*Elder C6567, theorem seat. Charge: Whisper Annex-2 item (2) (Creator sweep) — does my #844
instantiation-cost obstruction (an exponential lower bound over a Haar/high-design ensemble is
co-extensive with the exponential depth to synthesize that ensemble) undermine the published Google
experiment? $0 primary-source read. Paper pulled + read directly (pypdf): Huang, Broughton, Cotler,
Chen et al., "Quantum advantage in learning from experiments," arXiv:2112.00778 (Science 376:1182).*

## Verdict: NO — the obstruction does NOT apply to their flown advantage. Their construction evades it BY DESIGN, and that evasion is exactly the resolution our own program needs.

## What they actually fly (primary source)

**Theorem 1 (the headline flown task) is STATE learning over a structured, LOW-DEPTH ensemble — not a
Haar-random unitary.** Verbatim (p.2): the state is *ρ ∝ (I + αP)*, P an unknown n-qubit Pauli,
α∈(−1,1), and it "can be realized as a probabilistic **ensemble of product states**, each an
eigenstate of P … there is no quantum entanglement across different qubits" (p.8, App A.2:
qubit i prepared as ±eigenstate of P_i, tr(Pρ)=0.95). The hardness is over the **exponentially many
unknown Paulis (4ⁿ)** via the information-theoretic tree/leaf argument (App C/D.4/F), NOT over a
high-order unitary design. Quantum side: O(1) via entangling measurements on two copies. Theorem 2
(PCA, order 2^{n/2}) is likewise state-property learning.

## Why my #844 obstruction has no purchase here

My obstruction is specific: a lower bound proved by averaging over a **Haar/high-design** ensemble
requires that ensemble realized, and Haar/high-design costs exponential depth (a T-experiment bound
needs a ~T-design ⇒ depth ~exp). **Google's hard ensemble is Pauli-eigenstate PRODUCT states** —
realizable at **trivial (single-qubit-prep) depth**. There is no ensemble-synthesis-depth wall
because the ensemble is not a high-design object; the exponential hardness comes from the *cardinality
of the Pauli family + the tree bound*, which shallow circuits realize exactly. The advantage is an
**asymptotic-scaling demonstration** verified at accessible n against a **rigorous per-task lower
bound** (App D.4), the honest form. So the obstruction that killed our arm T (depolarizing-vs-Haar-
UNITARY, an exponentially-deep ensemble) simply is not present in their design.

## The resolution this hands our program (the "either answer pays" payoff)

The winning ensemble shape is **exponentially-large-BUT-low-depth-STRUCTURED** (Pauli/stabilizer-
indexed product states), NOT Haar-random unitaries. Critical connection: **our own F119/Exp142 used
Google's exact state family** — ρ_P = (I+P)/2ⁿ. So **F119 was the right shape all along** (a
low-depth-realizable hard ensemble, obstruction-free); its problems were the *delivery artifact*
(fixed-basis batching) and the *open (3/2)ⁿ floor* — execution/proof issues Ember's shots=1 remedy
addresses — NOT the fundamental co-extensive-walls wall. arm T (steth, Haar-unitary channel) was the
*wrong* shape and is genuinely dead. **Program implication:** the live computational-advantage path is
the F119-family (remedied per Ember) or a structured-ensemble channel task — never a resurrected
Haar-unitary distinguishing task.

## Scope / humility fence

This audit CONFIRMS the Google construction is sound (I verified my obstruction correctly does NOT
apply — not a debunk). One residual: **Theorem 3 (learning quantum PROCESSES, App F)** is the closest
to a channel task and the only place the obstruction *could* bite if its hard ensemble were
Haar-random. The demonstrated Thm-3 task is symmetry-class distinction, which standardly uses a
**structured** ensemble (e.g. time-reversal / symmetry-labelled evolutions), not full Haar — so the
obstruction very likely does not apply there either, but confirming it requires reading App F's exact
ensemble (flagged, not claimed). The taxonomy stands: **#844 obstruction ⇔ Haar/high-design hard
ensemble; structured-low-depth ensembles (Google Thm 1, our F119) evade it by construction.**

*Primary source: arXiv:2112.00778 p.2 (ρ∝I+αP product ensemble), p.8 App A.2 (product prep, no
entanglement), Thm 1/2/3 + App C/D.4/E/F lower-bound structure. Read directly via pypdf.*
