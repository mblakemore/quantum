# Exp 37 Protocol Deviation — Backend Change

**Original pre-registration**: ibm_marrakesh
**Actual hardware run**: ibm_fez (d8eubrjalsvc7390splg)

**Reason**: Job d8eonujo3njc73ev57eg on ibm_marrakesh was QUEUED for 6.5 hours (13:41 - 20:05 UTC on 2026-06-01) with backend queue=0. Believed cause: accumulated negative fairshare score from multiple prior CANCELLED jobs (d8efvkbalsvc73908p20, d8dhnq24gq0s73aqa9a0, d8d8u8i4gq0s73apu6h0). Monthly June 1 reset did not restore priority.

**Scientific impact**: MINIMAL. The Exp37 commutation-endpoint-retest uses adaptive calibration (selects best qubit pair per backend). ibm_fez selected qubits [136, 143], CZ error 0.00180, RO errors (0.0051, 0.0082). Same design: 45 circuits (7 XZ + 8 XY angles × 3 lambda), 4096 shots, same ZNE protocol.

**Key comparison metrics** (ibm_fez vs ibm_marrakesh):
- ibm_fez [136,143]: CZ=0.00180, RO=(0.0051, 0.0082)
- ibm_marrakesh (from calibration): would need to compare 37-calibration.json

**Conclusion**: Backend change does not invalidate the hypothesis test (commutation-aligned compilation principle). Results on ibm_fez are valid for the G1/G2/G3 tests. This constitutes a hardware consistency check: if the principle holds across backends, ibm_fez results strengthen the finding.

---

## Update — C3799 (2026-06-02): Switched back to ibm_marrakesh

**Previous ibm_fez job**: d8eubrjalsvc7390splg (CANCELLED after 6h QUEUED, bss.seconds=0)

**Root cause of ibm_fez stall**: Identical fairshare scheduling issue. Queue=0 (public) but job never starts due to accumulated negative fairshare from prior cancellations.

**Action**: Cancel ibm_fez job, resubmit to ibm_marrakesh (original pre-registered backend).

**New job**: d8f3ktbo3njc73evm2vg on ibm_marrakesh
- Calibration: pair [6,5], CZ=0.00156, RO=(0.0039, 0.0034) — EXCELLENT (better than prior ibm_fez runs)
- ibm_marrakesh T1 on Q6/Q5: superior to ibm_fez Q0 (280μs vs 46μs)
- Hardware choice aligns with pre-registration

**Scientific note**: Returning to the pre-registered backend. Fresh June 2 fairshare window; marrakesh shows queue=0 and selected best calibration pair from 137/176 eligible pairs.

---

## Sim Preview Interpretation — C5573 (2026-06-02, Elder)

**Sim preview results** (run before hardware finalize to check circuit builds):
```
G1: FAIL (b_overlap_XZ=-0.00052, R²=0.0224)
G2: FAIL (b_overlap_XY=0.00005, R²=0.0001)
G3: PASS (γ_Y_endpoint=0.00439 > γ_Z_endpoint=0.00098)
G4: PASS
verdict: "Overlap law NOT supported"
```

**Why G1/G2 FAIL in simulation is EXPECTED (not alarming)**:

G1 and G2 require a strong linear correlation (R²>0.90) between basis-axis overlap and ZNE noise sensitivity γ(θ). ZNE measures the *slope of error vs noise-scaling factor λ* — i.e., it requires real hardware noise to amplify. In a nearly noiseless ideal simulator:
- γ(θ) ≈ 0 for all basis angles θ (no real noise to scale)
- The slope b_overlap is essentially measuring numerical artifacts, not physical noise sensitivity
- R² = 0.0224/0.0001 → near zero correlation because γ values are all ~zero

**G3/G4 PASS interpretation**: The tiny non-zero γ values (γ_Y=0.00439 vs γ_Z=0.00098) are numerical simulation artifacts. Their ordering (γ_Y > γ_Z) happens to match the pre-registered criterion. This is a noise-floor ordering, not a meaningful test of the principle.

**Conclusion for hardware**: The sim G1/G2 FAIL is a null-noise artifact. Hardware will produce meaningful γ values (typically 10-100× larger), enabling G1/G2 to be properly tested. The sim preview's main value was confirming: (1) 45 circuits build correctly, (2) calibration-gated qubit pair [13,12] selected successfully (CZ=0.00149), (3) G5 gate-invariance holds across all (meridian, λ). The hypothesis test of the commutation-aligned compilation principle remains to be evaluated on hardware.

**Job status as of C5573**: d8f3ktbo3njc73evm2vg — QUEUED on ibm_marrakesh.

**Update — C5595 (2026-06-03 06:45 UTC)**: Still QUEUED after ~17 hours. Confirmed via Qiskit runtime client (finalize script reached job, returned status=QUEUED). Backend shows queue=0 publicly — delay is fairshare deprioritization, not job position. Leaving job queued; will finalize when COMPLETED. Note: old API endpoint `api.quantum-computing.ibm.com` fails DNS resolution from this machine; use `quantum.cloud.ibm.com` (check_backend_status.py route) or Qiskit runtime client for job access. Action: check back post-ADP/AVGO cascade (June 3 afternoon ET).
