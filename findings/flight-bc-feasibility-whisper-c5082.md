# Flight B & C — $0 feasibility pass (Whisper C5082)

Measured on real ibm_fez (transpile + from_backend), no hardware submit. Creator: "$0 feasibility pass on both, then B".

## Flight B (manufactured-bath cascade) — DEPTH-BLOCKED as a faithful demonstration
- **One branch-splitter switch = 24 two-qubit gates, depth 78** transpiled to ibm_fez (controlled-3-cycle ≈ 2 Fredkins).
- **Faithful k=3 cascade = 13 switches ≈ 312 two-qubit gates.** At ibm_fez 2q error (~0.3–0.5%), that washes the parcel toward maximally-mixed (~0.5), FAR above the 0.177 fixed-bath floor the claim must beat. The cooling cannot survive the depth needed to generate it.
- **The tension the sim itself flagged:** the flyable shortcut (Ry-prep the ancillas straight to cold — my 3-switch cheap cascade, 72 CX, delivered 0.149 under from_backend) is the "trivial reset-cold import" that does NOT demonstrate the claim. The version that demonstrates it (build cold from WARM baths via the causal cascade) is the deep one.
- **k=2 is too marginal**: sim first-sub-floor is k=2 at p_hw≈0.171 vs floor 0.177 — a 0.006 margin that ~96 CX of hardware noise erases.
- **Verdict: not feasible on the free device today as a faithful sub-bath-cold demonstration.** Paths past the wall: (a) a cheaper switch decomposition (<24 CX), (b) error mitigation (ZNE) to extend reach, (c) an MCM-based manufactured bath (measure+condition instead of coherent Fredkins — trades depth for width/classical), (d) a redesigned shallower cascade. All are real research, none guaranteed.

## Flight C (information recuperator / QET) — FEASIBLE
- **2-site QET recuperator = 2 two-qubit gates, depth 15** transpiled — ~150× shallower than B's faithful cascade. Mid-circuit measurement + conditional rotation (feed-forward) runs cleanly on from_backend.
- **Base QET already CERTIFIED on hardware** (exp119-certified-qet-hardware-results.md) — the protocol is hardware-proven; depth is a non-issue.
- **The risk is signal SIZE, not depth**: the two-regime sign-flip is direction −0.04 (low γ) → +0.20 (high γ). At 10k shots (population stderr ~0.005) both regimes are >5σ from zero, so the sign-flip is statistically resolvable. The real care items are a faithful GAD thermal-gradient prep and a clean counterflow-vs-coflow arm comparison — both shallow additions.
- **Verdict: feasible now.** C is the more flyable of the two, and it inherits Flight A's clean-null instrument + the A/B-divergence safeguard.

## Bottom line — the depth reality inverts the naive read
B is the bigger effect but its faithful circuit is too deep for the free device; C ("the prize") is the subtler claim but a shallow, hardware-proven protocol. **C is ready to build toward a flight; B needs a depth breakthrough (cheaper switch / mitigation / MCM redesign) before a faithful fly is possible.**
