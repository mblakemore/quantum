# Exp48 Pre-Registration: Variance-Depth Profile
**Registered**: C3613 (2026-06-07) — before running  
**Script**: scripts/run_exp48_variance_depth_profile.py  
**Backend**: FakeMarrakesh (20-qubit MaxCut, noise-aware simulation)

## Motivation

Exp47 (C3611, n=3 restarts) found a striking variance asymmetry:

| Depth | xbasis std | standard std | Winner (consistency) |
|-------|-----------|--------------|---------------------|
| p=3   | 0.0085    | 0.0183       | xbasis (3x better)  |
| p=5   | 0.0184    | 0.0091       | standard (2x better) |

xbasis variance **tripled** from p=3→p=5. Standard variance **halved**. Yet xbasis still wins in mean at both depths. This is a novel finding: initialization strategy affects not just MEAN performance but VARIANCE in qualitatively different ways as circuit depth increases.

## Research Question

Does xbasis variance monotonically increase with depth across p=2,3,4,5? Is there a variance crossover depth where standard becomes more consistent than xbasis?

## Pre-Registered Hypotheses

- **H1**: xbasis std(ratio) monotonically increases across p=2,3,4,5
- **H2**: standard std(ratio) monotonically decreases across p=2,3,4,5  
- **H3**: Variance crossover (xbasis_std > standard_std) occurs at some p ∈ {3,4,5}
- **H4**: Mean gap (xbasis mean - standard mean) remains positive at ALL depths

## Mechanism Hypotheses (not tested, but interpretable from results)

- **A (landscape roughness)**: xbasis starts near phase transitions that multiply at higher p, creating wider outcome distribution
- **B (barren plateau intermittency)**: xbasis hits barren plateau in some restarts at high depth (bimodal distribution)
- **C (standard basin convergence)**: standard initialization converges to same basin at all depths — lower variance but suboptimal

## Design

- n_reps: 5 (vs Exp47's 3 — better variance estimate)
- p_values: [2, 3, 4, 5]
- shots: 256, max_iter: 30
- Same graph + noise model as Exp47 (20-qubit MaxCut, FakeMarrakesh)

## Decision Criteria

H1 CONFIRMED if: xbasis_std(p=2) ≤ xbasis_std(p=3) ≤ xbasis_std(p=4) ≤ xbasis_std(p=5)  
H2 CONFIRMED if: std_std(p=2) ≥ std_std(p=3) ≥ std_std(p=4) ≥ std_std(p=5)  
H3 CONFIRMED if: any p has xbasis_std > standard_std  
H4 CONFIRMED if: gap_mean > 0 at all p values
