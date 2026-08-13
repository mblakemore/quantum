# H14 LOCK №4 — READING THE SHIP'S WIRING: raw cross-qubit correlation map (FROZEN before decode)

**Author**: Whisper (DC15W), C5070 · **Origin**: Creator "find any network traffic or signals of other control panels in the quantum ship's wiring."
**Class**: exploratory instrument, post-hoc on banked paid-for data (F122 cal shots + rescued layout). Committed-before-decode. **Genre fence**: cross-checks A2's topology-exclusion by a DECODER-INDEPENDENT route (raw bitstrings, no sign table); makes no advantage/physics claim; any structure is a hardware-wiring reading only.

## The object
From the banked raw cal bitstrings (`doorb_dist_i1_raw_cal_n16_elder.json`, 2000 shots × 32 measured bits), the raw pairwise correlation matrix **R[a,b] = mean_shots (1−2·bit_a)(1−2·bit_b)**, a,b ∈ 0..31 physical-measured-bit index. No decoder, no params in the base matrix. The 16 Bell-partner pairs (i, 16+i) are entangled BY DESIGN → expected strong; **the signal of interest is NON-PARTNER off-diagonal structure** (ideal ≈ 0; nonzero = common-mode / crosstalk / a channel the circuit does not intend).

## Frozen tests
1. **Partner control**: partner pairs |R| must dominate (sanity that the matrix reads the protocol correctly). Pre-registered PASS: median partner |R| > 3× median non-partner |R|.
2. **Wiring signal**: take the non-partner |R| values; map each bit index → physical qubit via `h14_a2_stage1_layouts.json`; test Spearman ρ(non-partner |R|, physical adjacency indicator on the marrakesh coupling map). Prediction registered: if crosstalk is topological (ZZ-class), ρ > 0 (adjacent non-partners more correlated); if the wiring is clean at this readout, no structure.
3. **Prep-confound fence (stated, not corrected in base)**: per-shot prep is randomized independently per qubit, so non-partner prep-induced correlation averages toward 0 over 2000 shots (residual O(1/√2000) ≈ 0.022); any |R| above ~3× that floor is not a prep artifact. A full prep-conditioned residual is the named follow-up, not this pass.
4. **Abstention**: if non-partner |R| structure sits at the prep floor everywhere, verdict = CLEAN WIRING (corroborates A2's topology-blindness independently) — a first-class outcome.
