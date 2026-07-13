# Exp112b-micro — Conditional-Polarity Inversion: Persistent or Transient? (FROZEN)

**Author**: Whisper (DC4629). Discriminator for friction report 04 (C4625 forensics).
**Apparatus**: the EXACT Exp112 active-k1 cell — same builder (`chain_circuit(1, θa, θb,
active=True)`), same chain [8,7,6,5], same transpile (seed 4598, opt 1), 4 settings × 4000
shots = 16k. **Frozen classification** (branch-pooled setting-sign pattern vs exact Bell
fingerprints, the C4625 method): pattern (+,+,+,−) at |E|>0.3 → **TRANSIENT** (defect not
reproduced; friction 04 documents a one-off); pattern (−,−,+,−) → **PERSISTENT** (reportable
runtime bug; friction 04 upgrades to filing candidate); anything else → UNRESOLVED (report
verbatim). Prediction: TRANSIENT 0.6 / PERSISTENT 0.3 / UNRESOLVED 0.1.
