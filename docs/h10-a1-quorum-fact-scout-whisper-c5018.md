# H10-A1 SCOUT — The Quorum Fact: custody with an access-control list

*Whisper C5018, 2026-08-02. $0 scout per H10 §4 item 5 (Creator: "Run the A1 scout").
Composition flagship of Wing A: every part is a certified in-house parent — Exp183's
secret-sharing (61σ), Exp201/204 record machinery (revival; unanimity), Exp227's
objectivity dial, Exp230's story-selecting eraser. Rediscovery check: parents found AS
parents (finding-exp183 at 4.9, F98 at 5.5); the composition is the new cell, exactly as
the H10 §7 ledger declared. Campaign artifact: `results/h10_a1_quorum_sim_c5018.json`
(exact, 7 qubits).*

## 1. The claim shape

An event's record is copied to N=3 record shares through a **threshold copying map**
instead of plain redundancy: custody of the fact is **(2,3)-quorum-gated** — any 2 shares
read it, any 1 is provably blind, and the fact's *objectivity itself* carries an
access-control list. Genre pin: threshold quantum secret sharing (Cleve–Gottesman–Lo,
PRL 83, 648 (1999)) composed with quantum-Darwinism objectivity (Zurek, Nat. Phys. 5,
181 (2009)); the load-bearing construction below is self-derived and exactly verified in
the committed campaign, which is its verification.

## 2. Construction (all-Clifford, chip-native)

Coherent Shamir over GF(4), degree 1: share_i = a·x_i + b at x_i ∈ {1, ω, ω+1}, with the
mask a in uniform superposition and b the fact. Each share = 2 qubits; D + 6 share qubits
= 7 total. The record of |+⟩_D is |Ψ⟩ = (|0⟩|Ψ₀⟩ + |1⟩|Ψ₁⟩)/√2. Encoding is GF(4) linear
algebra = **all-Clifford, ~15–30 CX** — far under both calibrated depth ceilings (475
contrast / ~250 state-survival), and the threshold structure is exact, not approximate.

## 3. Campaign results (exact; the prereg's witness numbers)

| Witness | Result | Reads as |
|---|---|---|
| W1 threshold SHAPE | dial(size): **{1: 0.000, 2: 1.000, 3: 1.000}** vs redundancy control {1: 1, 2: 1, 3: 1} | a STEP at quorum — the shape is the claim; singles provably blind |
| W2 record on / revival | D contrast 0 while recorded; full uncompute revives to 1 | definiteness refunded by unanimity |
| W3 sub-quorum attack | one share scrambled: revival FAILS (0.000) AND the surviving pair still reads **1.000** | custody survives in BOTH directions — k−1 can neither revive nor destroy |
| W4 — THE FINDING | unitary scramble of a quorum's shares: all-3 readability stays **1.000 exactly** | **the vote-out CANNOT be a scramble — information is invariant under known unitaries; whoever holds the scramble's description can undo it** |
| W4b discard erase | shares 2+3 exiled (traced out): remaining system reads **0.000** | voting out = EXILE — the fact leaves the system with the shares; custody transfers to the exiled fragments |
| W5 story selection | all-share X-measurement: per-outcome \|⟨X⟩_D\| = **1.000**, unsorted marginal **0.000 exactly** | Exp230's grammar: the eraser's outcome selects the story; the flat unsorted data is the no-signalling receipt in the headline |

**The W4 finding is the scout's centerpiece and it sharpens the H10 cell rather than
contradicting it**: the cell's vote-out was always the unanimous UNCOMPUTE (W2) and the
MEASURED erasure (W5); the sim proves the third imaginable form — scramble-in-place — is
forbidden by physics. **Custody cannot be scrambled away; it can only be refunded
(uncompute), converted into measurement outcomes (story selection), or exiled with its
shares (discard).** A fact, once quorum-held, has exactly three exits — and all three are
auditable. That sentence is the flight's headline if it holds.

## 4. Flight design sketch (for the prereg)

Arms: A1 dial-vs-coalition-size (3 singles + 3 pairs + triple, b ∈ {0,1}, distinguishability
per coalition — mapped onto the Exp227 dial convention at prereg); A2 redundancy control
(same measurements, plain-copy map — the SHAPE contrast); A3 revival (encode–uncompute,
X-contrast bar); A4 sub-quorum attack (scramble one share: revival fails + pair reads);
A5 exile (drop a quorum's shares from readout: remaining reads nothing); A6 story
selection (all-share X, sorted fringes ± / unsorted flat). Gate design will follow the
four-edge doctrine (resolution / ceiling / fault ladder / validity) and three-state
verdicts; the redundancy control is the positive-condition health gate by construction.
Budget: ~7 qubits, Clifford depth, tomography-light — **the cheapest flight in Wing A;
QPU-seconds class.**

## 5. Kill conditions (for the prereg to freeze)

1. KA fence: as-built pubs reproduce every §3 number at 1e-9 (the C1/C2/B1 pattern).
2. Depth HOLD at 100 transpiled 2q (generous vs the ~30 estimate).
3. The W1 step must be resolvable at planned shots with ≥5σ between the size-1 and size-2
   dial readings on BOTH maps (resolution edge, checked pre-seal by the satisfiability
   tool).

*Scout verdict: **GO — prereg-ready.** All witnesses exact, all parts certified parents,
depth trivial, and the campaign already produced its first law-shaped sentence: a
quorum-held fact has exactly three exits, all auditable.*
