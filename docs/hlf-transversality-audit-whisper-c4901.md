# The HLF Transversality Audit — what the [[4,2,2]] shields can compute transversally

**Whisper C4901, 2026-07-19. 0 QPU. H4 board rank 7 on the Creator's standing go.**
Gates Horizons-4 Invention 6 (the logical HLF computer). Every logical-action claim below is
**machine-verified** by [`scripts/hlf_transversality_audit_c4901.py`](../scripts/hlf_transversality_audit_c4901.py)
(Clifford conjugation + GF(2) decomposition into stabilizers × logicals; Part 3 enumerates
the generated symplectic group). Textbook priors credited: the [[4,2,2]] transversal gate
set is documented code theory (Gottesman lineage); the contribution here is the audited
table on *our* convention, the group-reachability verdict, and the flyable instance spec on
the certified stack.

## 1. The audited logical-action table (mod Pauli frame — software-correctable)

| Physical operation | Cost | Logical action | Note |
|---|---|---|---|
| **S⊗4** | 4×1q, **zero 2q** | **CZ̄(L1,L2)** | ⭐ in-block logical *entangling* gate from single-qubit physicals |
| CZ(01)CZ(23) / (02)(13) / (03)(12) | 2×2q | CZ̄(L1,L2) | three equivalent 2q routes to the same gate |
| H⊗4 | 4×1q | (H̄⊗H̄)·SWAP̄ | with the wiring SWAP below → pure H̄⊗H̄ |
| SWAP(q1,q2) | wiring only | SWAP̄(L1,L2) | 197's automorphism |
| tCNOT (straight) | 4×2q | CNOT̄(L1A→L1B)·CNOT̄(L2A→L2B) | certified 191/196/197 |
| tCZ (straight) | 4×2q | CZ̄(L1A,L2B)·CZ̄(L2A,L1B) | crossed pair |
| **tCZ (permuted q1↔q2)** | 4×2q | **CZ̄(L1A,L1B)·CZ̄(L2A,L2B)** | straight pair, zero extra gates |

Stabilizer group preserved in every case (audited); all sign/stabilizer factors absorbed by
the Pauli frame.

## 2. The obstruction, proved by enumeration

The in-block transversal set {S⊗4, H⊗4, SWAP} generates a logical group of order **12**
out of Sp(4,2)'s **720** (mod Paulis). Membership tests: **S̄ on one logical: NOT
reachable. S̄⊗S̄: NOT reachable. H̄ on one logical: NOT reachable.** No composition of
in-block transversal operations produces an individual logical phase gate — the
obstruction is group-theoretic, not cleverness-limited.

Consequence for HLF: the BGK circuit is H-layer · U_q · H-layer with
U_q = Π CZ(edges) · Π S(vertices where b_i = 1). The CZ machinery is fully available; the
**S-vertices are not** (transversally).

## 3. The verdict: two roads, one open now

**Road A — the b = 0 family: COMPILABLE TODAY, and a natural first instance exists.**
HLF instances with no linear term need only CZ edges. For n = 4 logical qubits (2 blocks;
v1,v2 → L1A,L2A; v3,v4 → L1B,L2B), the 2×2 grid's four edges decompose *exactly* into the
available operations:
- (v1,v2): in-block A → **S⊗4 on A** (zero 2q)
- (v3,v4): in-block B → **S⊗4 on B** (zero 2q)
- (v1,v3) + (v2,v4): the straight inter-block pair → **one permuted tCZ** (4 CZ)

Full U_q for the all-edges 2×2-grid instance: **two transversal-S layers + one permuted
tCZ = 4 physical 2q gates** (plus 2×2 CX for the two block preps; ~8–12 2q total before
routing — shallower than Exp196). H-layers via H⊗4 + wiring. **This is Invention 6's
first flight, now specified**: logical BGK solver vs bare solver co-batched, F113's
W1/W3-coverage gates at the logical level, shield-beats-bare on P(valid z) as the
deliverable. Pre-flight check reserved to the flight's selftest: verify the b=0 instance's
solution-coset structure is nontrivial (F113's W3 machinery, statevector tier).

**Road B — b ≠ 0 instances: need a logical-S gadget (non-transversal).** Named options,
costed for a later rung: (i) teleported-S̄ through a logical ancilla prepared in
S̄|+̄⟩ + logical CNOT + measurement + frame (stays within measurement-and-frame
discipline; ancilla prep is postselected non-FT like all house preps); (ii) a direct
short non-transversal in-block Clifford for S̄1 (exists by universality of the Clifford
group; breaks detection-pays purity mid-circuit — the audit recommends (i)).

## 4. The bonus headline

**An entangling logical gate for zero physical entangling gates**: CZ̄(L1,L2) = S⊗4 + Pauli
frame. On hardware where 2q gates dominate the error budget, the [[4,2,2]] block computes
its in-block entanglement *for free at the 2q ledger* — a concrete, flyable instance of
"the shield pays" one level deeper than postselection. The b=0 HLF flight will exercise
this gate twice, making it load-bearing in a computational context for the first time in
the campaign.

*Next per the standing go: H4 rank 6 (Invention 3, the shielded sensor) opens the next
cycle; the Road-A logical-HLF flight slots after it with this audit as its groundwork.*
