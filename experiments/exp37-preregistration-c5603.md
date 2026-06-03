# Exp37 Pre-Registration: Expected Results (C5603)
**Pre-registered**: June 3, 2026 | Job: d8fu393o3njc73f0rsqg (ibm_kingston)
**Status**: QUEUED — predictions locked before results available

## Pre-Registered Expectations

### G1 (R² ≥ 0.90 both meridians)
**Prediction**: PASS (both X-Z and X-Y meridians)
**Probability**: 0.65
**Rationale**: ibm_kingston pair 154-155 has CZ error 0.15% (very low). Simulation showed G1 FAIL but that was on FakeMarrakesh with poor noise correlations. Real quantum hardware at low error rates shows more structured noise-overlap relationship. Exp36 showed X-Z R²=0.971 (easily passing). X-Y had R²=0.897 (near threshold, now with extra φ=80° point to stabilize fit).

### G2 (Spearman ρ ≥ 0.90 both meridians)  
**Prediction**: PASS
**Probability**: 0.60
**Rationale**: If G1 passes, G2 likely follows. The Spearman rank correlation of noise vs overlap should be high when the noise-overlap relationship is structured.

### G3 (γ_Y_endpoint > γ_Z_endpoint)
**Prediction**: PASS
**Probability**: 0.85
**Rationale**: This is the primary result from the commutation-aligned compilation principle. Exp36 already showed γ_Y (0.0245) > γ_Z (0.0221) and G3 PASSES in simulation. With the confound-correction in Exp37, this should hold robustly.

### Overall (principle_confirmed = G1 AND G2 AND G3 AND G4)
**Prediction**: PASS (principle confirmed)
**Probability**: 0.55
**Rationale**: G3 is very likely (0.85). G1/G2 have good probability (0.65/0.60) given the low-error pair. The X-Y curve with extra φ=80° point should stabilize the R² above 0.90. Overall estimate: 0.55 probability of full confirmation.

## Validate At
When job status changes to DONE (currently QUEUED on ibm_kingston)

## Processing Protocol
1. Check job status: `python3 -c "from qiskit_ibm_runtime import QiskitRuntimeService; service = QiskitRuntimeService(); job=service.job('d8fu393o3njc73f0rsqg'); print(job.status())"`
2. If DONE: fetch results via experiment analysis script
3. Run gate analysis: compare R², ρ, endpoint ordering
4. Grade against pre-registrations above
5. Store as quantum experiment outcome

*C5603 pre-registration*
