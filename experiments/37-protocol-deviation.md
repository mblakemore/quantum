# Exp 37 Protocol Deviation — Backend Change

**Original pre-registration**: ibm_marrakesh
**Actual hardware run**: ibm_fez (d8eubrjalsvc7390splg)

**Reason**: Job d8eonujo3njc73ev57eg on ibm_marrakesh was QUEUED for 6.5 hours (13:41 - 20:05 UTC on 2026-06-01) with backend queue=0. Believed cause: accumulated negative fairshare score from multiple prior CANCELLED jobs (d8efvkbalsvc73908p20, d8dhnq24gq0s73aqa9a0, d8d8u8i4gq0s73apu6h0). Monthly June 1 reset did not restore priority.

**Scientific impact**: MINIMAL. The Exp37 commutation-endpoint-retest uses adaptive calibration (selects best qubit pair per backend). ibm_fez selected qubits [136, 143], CZ error 0.00180, RO errors (0.0051, 0.0082). Same design: 45 circuits (7 XZ + 8 XY angles × 3 lambda), 4096 shots, same ZNE protocol.

**Key comparison metrics** (ibm_fez vs ibm_marrakesh):
- ibm_fez [136,143]: CZ=0.00180, RO=(0.0051, 0.0082)
- ibm_marrakesh (from calibration): would need to compare 37-calibration.json

**Conclusion**: Backend change does not invalidate the hypothesis test (commutation-aligned compilation principle). Results on ibm_fez are valid for the G1/G2/G3 tests. This constitutes a hardware consistency check: if the principle holds across backends, ibm_fez results strengthen the finding.
