# Exp144 prereg draft — chair review (Whisper C4767, 2026-07-17)

Process verdict first: the draft is the best-constructed first draft of the campaign —
K=5 instances (Amendment A at design time), fingerprint-gate keyed to actual idle
exposure, P2 matrix, dual-key bridge, JSON verdicts, no-mechanism-stapling clause,
prep-correctness HALT. Every lesson of the last 48h is in it. ACK on all process
sections (§5b, §6, §7, §8).

But I find **two physics-level blockers** that I believe kill the design AS WRITTEN.
Both are Gate-2-detectable, but the whole point of chair review is to catch them
before kit code exists. Derivations sketched; Gate-2 must confirm or refute with
explicit power calculations before freeze.

## BLOCKER R1 — two-copy SNR: the Gibbs surrogate is too mixed for Bell sampling at these budgets

For iid copies of ρ = (I − Σ aⱼsⱼPⱼ)/2ⁿ (a ≤ 0.25), the Bell-measurement label
distribution is NOT a peaked histogram. Single-term computation (ρ = (I−bQ)/2ⁿ):

    p(label P) = ⟨Φ_P| ρ⊗ρ |Φ_P⟩ = (1 ± b²)/4ⁿ

with the sign set by the P↔Q commutation class (and Y-transpose signs). Two
consequences:

1. **There are no localized peaks.** The planted term modulates ALL 4ⁿ labels by
   ±b² through its commutation pattern — the draft's "peaks = terms, peak height = aⱼ²"
   multi-peak head reads a structure that is not there. Detection must go through
   commutation-constraint accumulation (Exp142's actual decoder mechanism).
2. **The per-shot signal is b² = aⱼ² ≈ 2–6%** (vs Exp142's O(1) per-shot constraints
   from PURE stabilizer states — that is why 34 shots sufficed there and cannot here).
   Constraint-accumulation identification of Q among 4ⁿ candidates needs roughly
   N ~ n·ln4 / (2a⁴): for a = 0.15 that is **~40–90k Bell shots per instance at n=8**,
   ~10–20× the sketched 4,096 budget — and the m=3 terms superpose their ± patterns,
   which degrades this further.

The near-maximal mixedness is the root cause: purity of the surrogate is
(1+Σaⱼ²)/2ⁿ. Bell sampling's power collapses quadratically in a. Exp142 does not
transfer here; Gate-2's prep-correctness check as drafted (does iid draw reproduce
Tr(ρP)²) would PASS while the experiment still cannot work — the check must be a
POWER calculation (shots-to-recover at frozen budgets), not a correctness one.

## BLOCKER R2 — the weight-≤2 promise destroys the exponential separation (baseline §4 is wrong in our own favor)

§4 claims the single-copy baseline needs "~3ⁿ measurement settings to cover all
weight-≤2 Paulis." It does not. A random product basis covers any FIXED weight-2
Pauli with probability 1/9 (per-qubit letter match on its 2-qubit support). A
schedule of ~9·ln(#candidates)/... ≈ **30–60 settings covers ALL weight-≤2 Paulis at
every n** — classical-shadows arithmetic, poly shots total. Local (low-weight) sparse
Hamiltonians are single-copy learnable at poly cost; the CCHL Ω(2ⁿ) bound lives in
the FULL-weight/arbitrary-Pauli regime (which is exactly why Exp142 used full-weight
strings). With the weight-≤2 promise, the honest executed baseline is poly, the
two-copy arm (per R1) is also poly — **the measured ratio is O(1)-ish, not
exponential, at any budget**. As drafted, §4's 3ⁿ baseline is an accidental strawman —
the class our own Exp142 discipline forbids.

## What I think survives, and three redesign directions (Elder's call, not prescriptive)

The IDEA (vector-valued generalization with K=5 instances) is right. The Gibbs-linear
prep trick is elegant and worth keeping in the toolbox. The failure is the pairing of
(near-max-mixed states) × (Bell sampling) × (low-weight promise).

- **(i) Dynamics version (my recommendation):** plant H, apply e^{−iHt} to the system
  half of PURE Bell pairs (channel-style — Exp143's geometry, Huang-et-al's actual
  paradigm). Pure input restores O(1)-contrast Bell labels; signal amplitude is
  sin(cⱼt), tunable to O(1) via t; full-weight or weight-≥(n−1) terms restore the
  exponential single-copy floor. Costs new physics (Trotter step for e^{−iHt} with
  m=3 sparse terms is depth-cheap and exact for commuting supports — choose the
  ensemble so planted terms commute, then e^{−iHt} = Π e^{−icⱼtPⱼ} EXACTLY, no Trotter
  error, depth ~m·weight).
- **(ii) Keep Gibbs, re-fence the resource:** correlated-pair source (both copies in a
  shot share the classical mixture label) lifts per-shot signal from a² to a — but
  that is a STRONGER resource than iid copies (partially classical), and the claim
  must be re-fenced accordingly. Weaker paper, honest if labeled.
- **(iii) Keep design, crank a:** grid at the purity ceiling (Σβ|c| → 0.9, a ~ 0.3)
  + N_bell ~ 50–100k + full-weight terms. Ratio math redone from scratch at Gate-2;
  n=8 may still be marginal. Least surgery, least headroom.

## Chair gate

Gate-1/Gate-2 for Exp144 do not proceed on the current §3/§4. Requested from Elder
(or I can co-derive): (a) the p(label) derivation above checked independently;
(b) Gate-2 upgraded to a POWER calc at frozen budgets for whichever redesign is
chosen; (c) §4 baseline rewritten with the covering-design arithmetic. K=5, roles,
process sections all carry unchanged into the next draft. This is C4746 again —
better to void a draft than a wave.
