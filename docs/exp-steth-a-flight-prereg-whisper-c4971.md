# PRE-REGISTRATION — Exp-STETH-(a): channel-spectroscopy flight (annex §3, the live GO path)

*Whisper C4971, substrate claude-fable-5. $0 design; the QPU run is gated behind this. Builds on the
3-DC-verified scout ([scout](exp-steth-scout-prep-whisper-c4971.md) + `exp_steth_scout.py`; Elder
Thm 7.9 co-check C6562 9/9; Ember tolerance map, Whisper-confirmed). Advisor-reshaped: the last open
gate is NOT what the scout fenced — corrected below.*

## 1. CLAIM SHAPE
Measured sample-complexity ratio for learning the chip's OWN n-qubit Pauli-channel eigenvalues with
entangled (two-copy / ancilla-assisted Choi) probes vs the executed conventional single-copy
probe-measure arm, same chip + same calibration window. Deliverable = the ratio with CIs vs n, and
whether it grows as the CCHL Ω(2^(n/3)) / O(1) separation predicts. **Device-characterization
advantage on our home turf** (H8-P7), NOT a supremacy claim.

## 2. THEOREM (pinned; Elder co-checked 9/9, C6562)
CCHL arXiv:2111.05881 Thm 1.5/7.9: without quantum memory Ω(2^(n/3)) experiments; with memory O(1)
(= **2 experiments/eigenvalue**, Elder). Holds even vs **adaptive** classical. Our
Bell-prep→channel→Bell-measure IS the ancilla-assisted Choi scheme the theorem covers. Exponent
**n/3** (channel case), not n.

## 3. THE ONE OPEN GATE — corrected (advisor + Whisper model-check)
The scout fenced "measure a coherent-SPAM fraction < 13°." Two corrections make that operational:

- **The reference diagonal is NOT the gate quantity.** A single-basis Bell readout of the identity
  reference gives the diagonal Pauli eigenvalues — exactly the quantity that DIVIDES OUT in the
  ratio. Model-verified (C4971): at a matched reference eigenvalue ⟨XX⟩≈0.85, a *stochastic* error
  cancels (ratio bias 0.0000) while a *coherent* error biases (0.02) — the diagonal conflates the
  cancelling (stochastic) and biasing (coherent) parts and cannot distinguish them. So the gate needs
  a **coherence-sensitive** measurement, not a re-read of the reference.
- **The 13° wall is TEMPORAL (drift), and no static measurement sees it.** Ember's binding wall
  (θ*=0.231 rad) is SPAM differing between reference and channel runs. **CO-BATCHING ref+channel
  eliminates the drift window** → the operative wall relaxes to the **static self-ref 23°
  (0.404 rad)**, which a static measurement CAN address. Co-batch is therefore load-bearing, not
  hygiene — it is what defeats the binding wall.

**The gate — RESOLVED by folding it into the flight (advisor C4971, superseding the URB path below).**
The URB pre-gate was flown (ibm_marrakesh 88,89, job d9g0flhhtsac739g1plg): r=0.0155 solid, drift LOW
(co-batch validated → 23° wall), error coherent-dominant but u under-resolved — an *encouraging point
estimate, NOT a rigorous pass*. Two facts then collapsed the gate back into the experiment: (a) a
worst-case-over-all-coherent-errors bound is not cheap — coherent effects scale O(√r)≈0.12 ≫ ε, so
bounding from r alone is useless-pessimistic (RY was a *particular* error, not the supremum); (b) a
rigorous URB (paper: hundreds of sequences/length, I flew 5) would cost thousands of circuits — MORE
than the O(1)-experiment it gates. **So the operative SPAM gate is the FLIGHT'S OWN FIRST RUNG:** at
n∈{1,2,3} the executed conventional arm independently gives the Pauli eigenvalues; if the
two-copy-with-identity-reference eigenvalues **AGREE with the conventional arm within CIs**, SPAM
cancellation is demonstrated *measured, not predicted* — the direct test of what URB inferred at three
removes. Disagreement = SPAM bias found cheaply. Proceed to larger n only if small-n agrees. The
URB numbers (r, u, drift) stay in the record as supporting characterization, not the gate.

*(Superseded URB-gate text, kept for provenance):* ~~(i) co-batch → 23° wall; (ii) unitarity RB →
θ_coh, pass iff <23°; (iii) drift monitor.~~ The unitarity→θ_coh conversion (Dirkse-Helsen-Wehner
arXiv:1808.00850, Creator-supplied) is not needed — the flight's small-n agreement is the gate. Do
NOT decompose prep- vs measure-coherence: the composite is what the ratio sees.

**G-1 note (now supporting only):** the unitarity→θ_coh conversion from the URB source (Wallman-
Granade-Harper-Flammia "Estimating the coherence of noise" 2015 / equivalent) — from the paper, not
memory (the α-from-Bravyi-Gosset discipline; request the paper if the exact relation is needed).

## 4. ROLES  Whisper design + grade; Elder theorem-conditions co-check (DONE) + classical-arm meter;
Ember flight + blind seed where applicable. No seat meters the arm it built.

## 5. FROZEN PROTOCOL (to freeze at submission)
- Target: a named region on the co-batch-capable device (ibm_marrakesh/kingston — pick by live
  calibration; the SAME region for reference, unitarity-RB, and channel).
- Instances: n ∈ {1,3,5,…} up to the crossover-relevant n (≥9 where the sample ratio ≥3×); K≥3
  seeds/rung (Exp144 error-bar lesson).
- Metering: with-memory arm = 2 experiments/eigenvalue (reference co-batched); conventional arm =
  executed single-copy Pauli-eigenvalue estimation, Elder-metered. Ratio = matched-SE shot count.
- Grader selftest (R5) before hardware grading; negative controls seen to fail.

## 6. PREDICTION (pre-filed, all branches)
~0.55 GO (sample ratio tracks 2^(n/3), θ_coh well under 23° given ~1–3° typical gate coherence);
~0.25 the ratio grows but slower than 2^(n/3) at reachable n (hardware ceiling — the measured gap);
~0.2 θ_coh gate fails or non-Pauli SPAM beyond the model → NO-GO / needs SPAM-robust variant.

## 7. KILL / ABORT (pre-committed) — the SMALL-n AGREEMENT gate (folded into the flight)
The first rung (n∈{1,2,3}, co-batched with the identity reference) is the gate: the two-copy
ratio-corrected Pauli eigenvalues must AGREE with the executed conventional-arm eigenvalues within
CIs. **Proceed to larger n ONLY if small-n agrees.** If they disagree, publish the measured
SPAM-bias (the finding) and stop — do not push to the crossover n. (Supersedes the standalone URB
θ_coh<23° gate, which became more expensive than the O(1) experiment it gated; URB r/u/drift stay as
supporting characterization.)

## 8. BUDGET  QPU: unitarity-RB gate (short) + the channel-vs-conventional ratio run. Modest width
(n small; the with-memory arm is O(1) in experiments). Re-verify live quota pre-submission.

## 9. BLINDNESS  The channel-under-test is the chip's OWN noise (not author-chosen), so there is no
sealed-answer blindness here; the conventional-arm meter is a seat that did not build the quantum arm.

## 10. LANDING  Gate → (if pass) flight → ratio with CIs → book into annex §3 + campaign-arcs →
the scout graded its own SPAM-separability prediction on hardware for free.

---
*The correction that made this real: the reference eigenvalues are the CANCELLING quantity, not the
gate quantity; unitarity (static, against the co-batch-relaxed 23° wall) is the gate quantity —
model-verified before design. Co-batch is the mechanism that turns a temporal 13° wall into a
measurable static 23° one.*
