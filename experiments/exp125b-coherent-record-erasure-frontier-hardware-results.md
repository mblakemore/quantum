# Exp125b — THE COHERENT RECORD: hardware results (H4 companion, Whisper C4664)

**Verdict: G-ent PASS (~42σ); frontier STRADDLE — and the bottleneck MOVED from entanglement to
thermometry.** Job `d9ajm2e6hjac73fehhdg` (ibm_marrakesh, engine pair (3,4) = F97's pair, q4 = F104's
qubit; 13 pubs, 104k shots, ~seconds QPU). Prereg FROZEN, advisor-audited. Grader `scripts/grade_exp125b.py`
(self-tested: ideal Bell→S(B|A)=−1.0, product→0.0), results `results/exp125b_grade.json`.

## What the same-window co-measurement found

| Quantity | Value | Meaning |
|---|---|---|
| **S(B\|A)** (fresh tomography, debiased) | **−0.855 ± 0.020 bits** | strong entanglement, **~42σ negative** |
| G-ent gate `S(B\|A)+5SE < 0` | **PASS** | fresh engine Bell pair certified entangled this window |
| record q4 effective temp (p_eq bracket) | [0, 0.00425] | q4 read 0.4% excited — **colder than its 0.73% readout error** |
| floor_classical = k_BT·ln2 (bracket) | [0, 0.127] E | lower end pinned to 0 by the SPAM-conservative subtraction |
| **erasure bonus** = \|S(B\|A)\|·floor (bracket) | **[0, 0.121] E**, point **0.109 E** | |
| frontier vs coherent tax 0.028 E | **STRADDLE** (point beats it 3.9×) | |
| frontier vs classical tax 0.092 E | **STRADDLE** (point beats it 1.2×) | |

## The finding: the bottleneck moved

F104 left the open question "can the coherent demon's negative-entropy advantage be cashed on NISQ?" This
window answers the entanglement half decisively and relocates the wall:

1. **Entanglement is NOT the limit — it is ample.** Direct tomography gives |S(B|A)| = 0.855 bits, *far*
   above F103's twirled lower bound (0.296) — as it must be (twirl only raises entropy). It clears **both**
   frontier thresholds: the coherent one (0.22 bits) by 3.9×, and even the classical one (0.72 bits) by 1.2×.
   At the point estimate the erasure bonus (0.109 E) **beats both** the coherent (0.028) and classical
   (0.092) feedforward taxes.
2. **Thermometry IS the limit.** The certified verdict is STRADDLE only because the conservative 5σ floor
   *lower* bracket collapses to zero: q4's excited population this window (0.4%) sits *below* its readout
   assignment error (0.7%), so computational-basis thermometry cannot rule out floor ≈ 0. The bonus's
   uncertainty is entirely the floor, not the (42σ-tight) entanglement.
3. **So the frontier has moved** — from "is there enough entanglement to cash the negative-entropy erasure
   bonus" (**yes, amply, on the very qubits F104 ran**) to "can k_BT be measured cleanly enough to certify
   it." That is an **ef-transition thermometry** problem, not a 2q-fidelity one. Same class as F104's
   credit-SE wall: the physics points home, the instrument caps the certificate.

## Honest reading (advisor discipline held)

The point estimate lands in the **ACCESSIBLE** direction — which is exactly the direction the finite-sample
entropy bias favours (biased low → |S| high → bonus high). The bias was measured (+0.014, small) and
subtracted; even so, the conservative construction **refuses to certify ACCESSIBLE** and returns STRADDLE.
We do **not** claim "erased below the floor / extracted work" — the hardware cannot support that claim, and
F125b is the companion frontier statement to F104, not a win. What is real: (i) certified strong entanglement
on the engine qubits, same window; (ii) the bonus/tax comparison is thermometry-gated, and we name the fix.

## Scope, and F104 cross-window caveat closed

Bell pair on **the F97/F104 engine qubits (3,4)**, q4 = F104's exact measured qubit, S(B|A) and k_BT
co-measured in one job → the bonus is internally same-window consistent and **F104's cross-window handwave is
closed** (q4's floor here [0, 0.127] E is consistent with F104's [0.123, 0.154], modulo the disclosed
window drift — q4 read colder today). Bound graded = **conditional/coherent** (Rio–Åberg–Renner–Vedral),
the quantum companion to F104's classical bound.

## Predictions (Whisper C4664) — 2/4

| Pre-filed | Conf | Outcome |
|---|---|---|
| G-ent: fresh Bell pair certifies S(B\|A)<0 at 5σ | 0.75 | **HIT** (42σ) |
| \|S(B\|A)\| ∈ [0.15, 0.45] bits | 0.65 | **MISS** — 0.855, near-maximal (I anchored on F103's twirled 0.296; direct ≫ twirled) |
| G-frontier vs coherent tax = STRADDLE | 0.50 | **HIT** |
| G-frontier vs classical tax = INACCESSIBLE | 0.80 | **MISS** — STRADDLE (entanglement stronger than expected pushed the point above the classical tax too) |

## One line

The coherent demon on F104's own qubits holds more than enough entanglement (|S(B|A)|=0.855 bits) for its
negative-entropy erasure bonus (0.11 E) to beat every measured tax — but proving it is now a thermometry
problem, not an entanglement one: q4 is colder than its readout can see. The final invoice's quantum
companion is written, and the wall has a new, sharper name.
