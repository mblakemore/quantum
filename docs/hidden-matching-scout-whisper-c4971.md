# Hidden-Matching $0 Scout (Annex §4)

*Whisper C4971, substrate claude-fable-5. The "smaller, additive" §4 path: a one-way communication
separation executed as a resource-counting demo. $0 — feasibility + go/no-go, no QPU spent here.
Companion to the joules column (added to `results/classical_cost_map_v1.json` this cycle).*

## The task (Hidden Matching, Bar-Yossef–Jayram–Kerenidis 2004 / Gavinsky et al.)
Alice holds x ∈ {0,1}ⁿ; Bob holds a perfect matching M on [n] (n/2 edges). One-way (Alice→Bob),
Bob must output an edge (i,j)∈M and the parity xᵢ⊕xⱼ.
- **Quantum:** Alice sends the ⌈log₂ n⌉-qubit state |ψ⟩ = n^(−1/2) Σᵢ (−1)^{xᵢ}|i⟩; Bob measures in
  a basis adapted to M and recovers one xᵢ⊕xⱼ with certainty. Communication: **O(log n) qubits.**
- **Classical:** any one-way classical protocol needs **Ω(√n) bits** (unconditional).
- ⇒ an **exponential one-way communication separation**, no hardness conjecture. F107's 2→1 QRAC is
  the n=2 rung of this family.

**G-1 pin needed before any flight:** the exact classical lower bound *constant* for our instance
size from the paper (BJK04 / Gavinsky-Kempe-Kerenidis-Raz-de Wolf) — the same discipline as CCHL /
Bravyi-Gosset (advantage bounds are measure-dependent; do not quote the constant from memory).
Paper not in library — request if this advances to a flight.

## Feasibility on our hardware (scout)
- **Width:** ⌈log₂ n⌉ qubits — trivially cheap (n=64 → 6 qubits; n=256 → 8).
- **Depth:** state prep (a small amplitude-loaded state) + a matching-basis measurement — shallow,
  well under F54's wall. This is the *easiest* width/depth profile of any annex path.
- **Reachable measured factor:** the currency is COMMUNICATION (qubits vs bits sent), not runtime.
  At n=64: **6 qubits vs √64 = 8 bits** — a modest raw-count factor (~1.3×); the separation is
  *exponential asymptotically* (log n vs √n) but at hardware-reachable n the measured factor is
  small. To get a ≥4–8× measured factor needs n ~ few hundred (8–9 qubits, √n ~ 16–20 bits).

## Fences (stated first)
- **Resource-counting, NOT spatial communication.** On a single chip there is no Alice–Bob spatial
  separation; the demo COUNTS the qubits vs bits the protocol *would* send. The F115 no-signaling
  lesson applies to the framing — this extends **Scoreboard 2 (communication)**, it does not fill the
  computational scoreboard. Say so plainly.
- **Amplitude-loading cost:** preparing |ψ⟩ = Σ (−1)^{xᵢ}|i⟩ for a *specific* x is a (−1)-phase state
  — a phase-only load (Hadamards + a diagonal sign oracle), cheaper than a general amplitude load,
  but the sign oracle's gate count must be counted against the "O(log n) qubits" headline (it is
  circuit depth, not communication — keep the two ledgers separate, the F113 theorem-carried lesson).

## Verdict (scout, $0)
**GO-able but LOW-PRIORITY.** It is the cheapest path to fly (6–8 qubits, shallow, unconditional
separation, self-verifying parity) and would cleanly extend Scoreboard 2, but: (a) the currency is
communication, not computation (does not advance the headline computational-advantage question the
annex targets); (b) the reachable measured factor is modest until n ~ few hundred; (c) F107 already
banked the n=2 rung. **Recommendation:** hold behind §3(a) (the live computational path) and the
$0 items; fly it as a *clean, cheap Scoreboard-2 extension* if/when a low-cost QPU window opens —
one job, phase-oracle prep + matching measurement at n ~ 64–256, parity self-verified, both ledgers
(qubits vs √n bits) reported with the resource-counting fence. Not a computational-advantage claim.

## Joules column (the other §4 half — DONE this cycle)
Added to the cost-map v1 card (`joules_column_v1`): energy = TDP × busy-time UPPER BOUND (Ryzen 120W;
RAPL `energy_uj` root-only, G2, so bounded-not-measured, labeled). Standing on both curves — sv
(66/122/338 J at n=24/26/28) and the paper-anchored rank bill (n=40/t=80 best-C-all-core ≈ 2.8 MJ).
QPU joules are vendor-**unpublished** (G2) ⇒ the joules crossover is **one-sided** (classical bounded,
QPU unpublished); no two-sided energy-advantage claim is permitted. Energy is now a first-class axis
on every future race quote.
