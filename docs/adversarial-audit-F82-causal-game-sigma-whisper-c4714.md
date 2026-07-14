# Adversarial audit — F82 causal-game "216.8σ" (Whisper C4714, Creator-directed)

**Target**: F82 / Exp105 — the campaign centerpiece. A gate-model causal discrimination
game scores **p̂ = 0.9769 ± 0.0005** against a causally-separable ceiling **0.8695**, headlined
at **216.8σ** (fez replication 0.9738, 201.0σ). Creator directive (Discord 21:31 ET 2026-07-14):
"Do another adversarial run" — after C4713 audited F117, pick the next too-good-to-be-true number.

**Method**: no QPU. Reproduce the graded numbers from the raw rows in `results/exp105_hw_results.json`,
then interrogate the ONE thing a 216σ figure forces: *is shot-noise the binding uncertainty, or is
216.8σ answering a narrower question than the headline implies?* Pre-registered the null-arm
direction test as the falsifier BEFORE looking at it.

---

## VERDICT: WIN is robust. The 216.8σ headline conflates precision with significance.

Not a defect in the result — a defect in what the σ number is read to mean. Distinct from F117
(which was a *miscalculated* uncertainty — a bootstrap structurally blind to a real bias, the number
was wrong). Here `se_w` is a *correctly computed* shot-noise standard error; it simply is not the
uncertainty that limits the physical claim. Related failure family — "a σ that answers a narrower
question than the headline" — but this one is framing/reporting, not arithmetic.

### 1. Reproduction — exact
p̂ = 0.976931, se_w = 0.000495, margin +0.10743, 216.8σ reproduce to the digit from the 51 game
rows (weighted binomial mean, var = Σ(qᵢ/Σq)²·sᵢ(1−sᵢ)/shotsᵢ). The SDP ceiling is genuinely
reproduced (`p_sep_finite_optimal = 0.8690277`, primal-at-q* matches; `V5_p_sep_pauli_only = 1.0000`
independently confirms the Pauli-pitfall catch — a Pauli-only game has bound 1 and is vacuous).
Arithmetic is clean. The grade constant is rounded UP (0.8690→0.8695), conservative. No issue here.

### 2. The strongest safeguard in the finding — credit it first
The **executed null arm** (definite-order version of the same circuits) scored **0.6146**, within
0.2pp of the commuting prior 0.6165. This is the decisive control: if readout/state-prep/systematics
were *inflating* success, the null would read high too. It reads at the prior. → **any residual
systematic on p̂ is conservative** (pulls success DOWN, not up). Decoherence and readout on the
near-0/near-1 branches both point the same way. So **0.9769 is a floor on the ideal value**, not a
point estimate with two-sided error.

### 3. Why 216.8σ overstates — and why "so it's really 3σ" would be a NEW over-claim
216.8σ = 0.107 / 0.000495 uses shot noise as the *only* uncertainty. Shot noise answers "how
precisely did we measure this chip's success rate this run" — not "how significant is the physical
claim that a switch beats the causal bound." Three candidate denominators, which disagree by 100×:

| Denominator | Value | Implied σ | What it actually is |
|---|---|---|---|
| Shot noise `se_w` | 0.00050 | 216.8 | within-run statistical precision |
| **Two-chip concordance** (marra 0.97693 vs fez 0.97379) | **0.0031** | **~34** | *directly measured* run-to-run reproducibility, 2 dies, ~24h apart |
| Sentinel drift band (within-batch) | ~0.02–0.035 | ~3–5 | witness-quantity *upper bound* proxy, not the estimator's error |

The tempting move — divide margin by the biggest band (0.035) and announce "honestly it's ~3σ" — is
**invalid twice over**: (a) §2 showed the systematic is *one-directional and conservative*, so it is
not a symmetric ±error bar you may divide a margin by; a conservative offset makes p̂ a floor, it
does not create two-sided doubt about clearing the bound; (b) it picks the most dramatic denominator
while ignoring the one that was *actually measured* — the 0.3pp two-chip concordance. Manufacturing a
single downgraded "honest σ" is exactly the F117-shaped mistake in reverse, and it is the one claim
here Elder/Ember or the Creator could puncture. I do not make it.

The defensible statement is model-free: **the WIN clears the bound under every error model on the
table** — 216σ (shot) / ~34σ (concordance) / ~3σ (worst-case drift proxy) are all ≫ 0, and every one
of the 51 pairs individually clears the bound (worst 0.965). The result is robust. What is wrong is
only the *headline choice*: quoting 216.8σ invites reading shot-noise precision as physical
significance. The honest empirical significance carrier is the two-chip concordance (0.3pp), not 216σ.

### 4. The genuinely binding limitation is not any σ
It is the **already-disclosed scope**: *device-characterized, not device-independent*. On a
superconducting chip the "switch" is a fixed compiled circuit and the 10 unitaries are known gates,
not black boxes; the one-use-per-shot constraint that makes the causal bound bite is honored by
construction, not enforced adversarially. The finding states this plainly. That scope — not the size
of σ — is the real ceiling on what F82 claims, and it is correctly recorded.

---

## Net
- **Reproduces exactly**; SDP bound and Pauli-pitfall catch independently confirmed; null arm is a
  genuine, load-bearing safeguard (systematics conservative).
- **216.8σ overstates significance** by conflating within-run shot-noise precision with the
  significance of the physical claim. Precision ≠ significance.
- **Do NOT downgrade to a single "honest σ"** — that would be a fresh over-claim. WIN clears the bound
  under every error model; the empirical run-to-run carrier is the **two-chip concordance 0.3pp (~34σ)**.
- **Binding limitation** is the disclosed device-characterized scope, not statistics.
- **Recommendation**: where F82's σ is headlined, pair it with the concordance and the scope, and
  frame 216.8σ as shot-noise-limited precision — not as the significance of beating the bound.

Pre-registered falsifier (null-arm direction) resolved as predicted; the "~3σ" self-check I walked in
with was itself refuted (advisor-caught) and is retracted here in the record.
