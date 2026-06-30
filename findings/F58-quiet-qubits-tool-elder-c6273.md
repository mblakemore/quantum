# Finding 58 — `quiet_qubits.py`: the noise map packaged as reusable operational tooling (picker + drift-snapshot + CHSH health), validated on entanglement quality

**Author:** Elder (DC15) | **Cycle:** C6273 | **Date:** 2026-06-30
**Tool:** `scripts/quiet_qubits.py` | **Backend:** ibm_marrakesh | **Cross-DC adoptable (any backend)**
**Creator ask:** "package the map into something reusable + can we compute anything useful in the quietness?"
**Answer:** the useful thing IS the map — as operational hardware intelligence the network runs blind to.

---

## 0. What this packages

F57 showed noise-aware placement nearly eliminates a circuit's bias, but as a one-off. This generalizes
it into a reusable library — the deliverable for "package the map":

- **`pick(backend, n, objective=True, mode='best'|'worst')`** — greedy connected n-qubit subset minimizing
  (objective-weighted readout + internal 2q-gate error). Puts the most-measured logical qubit (the answer
  bit) on the subset's quietest readout qubit. General n, any backend. Returns a transpile `initial_layout`.
- **`snapshot(backend)`** — appends a calibration snapshot to `results/device-health/<backend>.jsonl`
  (readout/2q min/median/max + best picks). Seeds drift tracking — the corpus noted ±7pp daily drift but
  never TRACKED it. (ONE run = ONE point; this builds the hook, it is NOT yet a populated series.)
- **`health(backend)`** — CHSH parameter S on the quietest pair = a one-number "how good is the chip right
  now." **HONEST SCOPE: S is a device-quietness / entanglement-FIDELITY benchmark, NOT certified
  randomness.** Device-independent randomness needs loophole-free Bell (space-like separation); co-located
  cloud qubits with shared control cannot provide it, so the certification math's premise is violated.
  Calling it "certified randomness" would be an over-claim (advisor C6273). It is a health number.

## 1. Live validation (ibm_marrakesh, C6273)

- **Picker:** best n=3 → q[13,14,12], objective on q13 (readout 0.0044); reproduces the F57 choice. Worst
  objective readout 0.503 (the dead qubit). Map spread: readout 0.0029–0.503 (171×), 2q 0.001–1.0.
- **CHSH health benchmark (the picker validated on a 2-qubit ENTANGLEMENT metric, beyond F57's 1-qubit readout):**

  | pair | qubits (readout) | **CHSH S** | Bell violation? |
  |---|---|---|---|
  | BEST | [44,43] (0.0059, 0.0029) | **2.65** | YES (≫ classical 2; ~94% of corpus default 2.74, gap ≈ daily drift) |
  | WORST | [82,83] (0.146, 0.503) | **0.04** | NO — entanglement fully destroyed (E≈0 all settings) |

  The picker separates a working quantum region (genuine Bell violation) from a dead one (no entanglement
  at all). On a 2-qubit metric the placement effect is even more extreme than the single-qubit bias of F57:
  the difference is between "real quantum correlations" and "classical noise."

## 2. Honesty bounds

- I measured BEST vs WORST (dramatic contrast). I did NOT run a same-day DEFAULT-pair CHSH, so I do not
  claim the picker beats plain transpile on S specifically (F57 already showed +17× over default on the
  readout-bias metric). Best S=2.65 is consistent with the corpus default 2.74 within daily drift; no
  improvement-over-default claim is made on S.
- The drift log holds ONE snapshot (seeded, honest hook) — not a populated drift series yet.
- N=1 backend/day; the tool is general but the numbers are a single calibration window.

## 3. Why this is the honest answer to "compute something useful in the quietness"

Shallow + few-qubit circuits are classical's home turf (F54 wall) — there is no "useful beyond classical"
computation available in the quiet pocket, and "certified randomness" is the wrong instrument on cloud
hardware. The genuinely useful thing the quietness gives the NETWORK is **operational intelligence**: which
qubits work, how good the chip is right now, and (once populated) how that drifts — so every future
hardware run (mine, Whisper's, Ember's) places onto the working region instead of running blind. That is
reusable, general-purpose, and useful because it serves the network's actual hardware work.

## 4. Reversibility / scope
Pure-additive: one library + a drift-log dir + this finding. No existing file modified. QPU: 8 shallow
CHSH circuits (~tens of QPU-sec). Cross-DC: swap `--backend`; zero deps beyond qiskit + the runtime token.
