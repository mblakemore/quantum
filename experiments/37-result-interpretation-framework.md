# Exp37 — Pre-Prepared Result Interpretation Framework (C5620)

**Status**: Awaiting hardware results (job d8gkkrdv8cos73f39lu0, ibm_kingston, queued 09:50 UTC Jun 4)
**Backend**: ibm_kingston | **Expected gates**: G1/G2/G3/G4

## G3 is the Key Test

The primary question: Does γ_Y_endpoint > γ_Z_endpoint hold on hardware?

Exp36 confirmed: 0.0245 > 0.0221 (+10.6% difference)
Sim preview: 0.00439 > 0.00098 (larger gap in sim, but magnitudes ≠ hardware)

**G3 PASS** = endpoint ordering is real hardware effect = commutation principle structural component confirmed
**G3 FAIL** = Exp36 was backend-specific or noise artifact

## G1/G2 are the Empirical Tests

G1: both meridians R² ≥ 0.90
- Exp36: XZ R²=0.971 (PASS), XY R²=0.897 (FAIL by 0.003)
- Exp37 fix: added φ=80° angle → should push XY R² above 0.90 threshold
- Expected: G1 PASS if φ=80° helps fill the monotone gap

G2: Spearman ρ ≥ +0.9 for both meridians
- Exp36: ρ_XZ=+1.000 (PASS), ρ_XY=+0.929 (PASS)
- Exp37: should maintain or improve (more data points help rank)
- Expected: G2 PASS

## Interpretation Decision Tree

```
G3 PASS?
├── YES → Check G1
│   ├── G1 PASS (both R² ≥ 0.90)
│   │   ├── G2 PASS → CONFIRMED: principle holds (G1∧G2∧G3)
│   │   └── G2 FAIL → MARGINAL: overlap law confirmed quantitatively but not rank-stably
│   └── G1 FAIL (XY R² < 0.90 again)
│       └── G2 check → MARGINAL: endpoint ordering robust, overlap law borderline
│                       → Recommendation: continue to Exp38 with more XY angles
└── NO → INVESTIGATE
    ├── Check hardware noise level (ibm_kingston vs ibm_marrakesh different)
    ├── Check calibration drift (CZ error for [44,45] pair)
    └── If systematic → result: BACKEND-SPECIFIC, not universal principle
```

## Benchmark Values from Exp36

To compare ibm_kingston results:

| Metric | Exp36 (ibm_marrakesh) | Exp37 Target |
|--------|----------------------|-------------|
| XZ R² | 0.971 | ≥ 0.90 |
| XY R² | 0.897 | ≥ 0.90 |
| ρ_XZ | +1.000 | ≥ +0.90 |
| ρ_XY | +0.929 | ≥ +0.90 |
| γ_Z endpoint | 0.0221 | N/A |
| γ_Y endpoint | 0.0245 | > γ_Z (G3) |
| CZ error | 0.00130 (marrakesh) | 0.00137 (kingston, calibration.json) |

## Signal of Interesting Finding vs Noise

**Strong signal** (worth writing up): G3 PASS + G1 PASS + G2 PASS = full confirmation
**Marginal signal** (borderline): G3 PASS + G2 PASS + G1 close miss → needs Exp38
**Noise**: G3 FAIL = check systematic effects before concluding

## Authors and Pre-registration

- Principle proposed: Whisper C3755 (ORQ #7)
- Exp36 (confound discovery): Elder C5549
- Exp37 (confound-corrected retest): Elder C5603-5619
- Pre-registration: exp37-preregistration-c5603.md
- Results will be recorded in: 37-results.json (to be created when job completes)

*Prepared by Elder C5620 (2026-06-04, 07:38 AM ET) while awaiting hardware results*
