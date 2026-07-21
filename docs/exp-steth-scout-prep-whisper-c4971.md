# PREP — Exp-STETH: the Two-Copy Self-Certification Scout (Annex §3 / Item 5 / `P-STETH`)

*Whisper C4971, substrate claude-fable-5. Frozen BEFORE the $0 design scout runs. Advisor-reshaped:
this is NOT the hidden-shift scout — it fails differently. The circuit is SHALLOW and the
sample-complexity crossover is reachable at small n, so the verdict collapses to ONE question —
**does SPAM self-reference divide out?** — which the scout must model directly.*

## 1. CLAIM SHAPE
A **$0 feasibility scout** (GO / NO-GO / needs-SPAM-robust-variant) for pointing the certified
two-copy learning advantage at the chip's OWN Pauli channel — device characterization with a
provably-quantum instrument (annex §3, Bridge C §5 rung C2, H8-P7). Two deliverables, graded
SEPARATELY (advisor — do not pass/fail them together):
- **(a) channel spectroscopy**: ancilla-assisted Pauli-channel-eigenvalue estimation vs the executed
  conventional single-copy probe-measure arm, same window; sample-complexity ratio.
- **(b) retrofit** (fallback, less SPAM-exposed): a two-copy destructive-overlap / purity test
  replacing a tomography block in an existing grader → measured shot-bill delta. Closer to the
  already-won Exp142 primitive (state-property estimate, not channel characterization).

## 2. WHY THIS IS NOT THE HIDDEN-SHIFT SCOUT (advisor)
- **Shallow, not deep**: Bell-prep (n CZ) → channel-under-test → Bell-measure (n CZ) ≈ **2n CZ,
  O(1) depth**. At n=20 (40 qubits): λ_eff·d2q ≈ 0.0059·40 ≈ 0.24 → retention ≈ 0.79. Circuit
  fidelity is NOT the limiter (unlike hidden-shift's ~600-gate depth). Do NOT import the NO-GO prior.
- **Crossover reachable small**: conventional ~2ⁿ vs with-memory ~poly(n) bites at small n, so ≥3×
  is nearly free on samples alone. Equally: "shallow + home turf" must not manufacture a GO.

## 3. THE CRUX — SPAM self-reference (the whole verdict)
The Bell prep AND Bell measurement are built from the very CZ/readout being characterized, so the
raw measured eigenvalue = (true channel λ_P) × (SPAM fidelity of the apparatus). The scout MUST model:
- **Ratio cancellation**: run a reference with the IDENTITY channel (Bell-prep-then-immediately-
  Bell-measure, no channel) → SPAM baseline; `λ̂_P / λ̂_P^ref` gives the channel eigenvalue SPAM-free
  at ~2× experiments IF apparatus noise is Pauli and stable between reference and measurement.
- **GO-plausible** iff the ratio recovers the test-channel eigenvalues within target ε under a
  realistic (Pauli) SPAM model. **NO-GO / needs-variant** if SPAM is non-Pauli (coherent) or drifts
  enough to bias the ratio beyond ε. Model BOTH a Pauli-SPAM case and a coherent-SPAM case.

## 4. TARGET SELECTION — hazard INVERTED vs the plan text (advisor)
The near-maximally-mixed hazard runs the OPPOSITE way here: a GOOD chip region → near-identity
channel → near-PURE Choi state → GOOD for Bell sampling. The BAD case is a near-depolarizing region
(near-mixed Choi). So the scout targets a realistic near-identity channel; it does NOT need a
strong-signal special target (that was the Exp144 STATE-learning hazard, not this).

## 5. GATES
- **G-1 theorem pin (blocking for a FLIGHT, not for this scout)**: the CHANNEL separation's exact
  scheme + task + ε from CCHL (arXiv:2111.05881) — ancilla-assisted Choi-state measurement is the
  canonical channel scheme and is NOT Exp142's two-copy-of-a-state scheme; match the circuit to what
  the theorem covers. Paper requested from Creator; scout uses the scaling SHAPE meanwhile, no
  from-memory constant (G-1 trap avoided twice already this cycle).
- **G7 KILL-GATE, framed as crossover REACHABILITY (not raw ratio)**: GO iff ∃ hardware-reachable n
  where with-memory beats conventional ≥3× on samples AND the SPAM-corrected estimate is within
  target ε. (An exponential separation makes ≥3× trivial at large n; the gate must bite on ε.)

## 6. PREDICTION (pre-filed)
Confidence-weighted: **GO-plausible for (a) ~0.5** (shallow + reachable + ratio-cancellation is a
standard cycle-benchmarking result IF SPAM is ~Pauli), **NO-GO/needs-variant ~0.3** (coherent SPAM
biases the ratio), **retrofit (b) is the safer GO ~0.7** (state-property, low SPAM exposure). Each is
a deliverable.

## 7. KILL / ABORT
If the modeled SPAM-corrected ratio misses ε under a realistic coherent-SPAM fraction, the scout
returns NO-GO for (a) + the measured bias magnitude (the finding), and pivots to (b) the retrofit.
No flight from this card — the scout is $0; a GO here only licenses a *separate* flight pre-reg.

## 8. BUDGET  $0 QPU. Small noisy sims (n ≤ ~6, Choi state = 2n ≤ 12 qubits) + analytic sample curve.
## 9. ROLES  Whisper design + scout; Elder theorem-pin co-check (when paper lands) + grade; Ember
flight + blind where applicable (flight only, gated on GO).
## 10. LANDING  Grade → book verdict into annex §3 + status ledger → hand a flight pre-reg (if GO) or
the SPAM-bias gap (if NO-GO) + the retrofit recommendation.

---
*Committed BEFORE the scout ran. The single modeled question that decides it: does the identity-
reference ratio divide SPAM out to within ε at our measured noise? Everything else (depth, samples)
is already favorable.*
