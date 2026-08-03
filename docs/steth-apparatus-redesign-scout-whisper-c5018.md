# Steth apparatus redesign — $0 scout (Whisper C5018, Creator GO "scout the redesigned steth apparatus")

**The measured problem**: u (witness survival) = 0.52/0.36/0.51 across 3 flights, 2 chips,
±DD, vs floor 0.70 — SYSTEM-side (Choi prep + controlled-SWAP depth); NOT ancilla
(λ_anc 0.06→0.74-0.80 under DD moved u 0.36σ; attribution-by-covariation, Ember #3995).

## The redesign: kill the controlled-SWAP, not the noise
**v5 witness = DESTRUCTIVE SWAP test (Cincio)**: transversal Bell-basis measurement
between copy pairs. Purity = E[∏ parity] via the standard identity — measured, not
interfered. **Removes (a) the ancilla entirely (λ_anc moot, DD row retired), (b) the
Fredkin/controlled-SWAP block (the depth that ate u).** Already hardware-validated in
this repo: the 3b retrofit flew it clean at n≤3 (wash verdict was about SHOT-BILL, not
signal death — the instrument worked).
- Depth: Choi prep (~3-5 2q at k=2) + 1 transversal CX layer + measure ≈ **8-10 2q
  total vs ~30+** in the interfered version. At fez λ_bit ≈ 0.003/slot: expected
  witness retention ≈ exp(-0.003·10·~w-factor) → **u-analog ≈ 0.85-0.92 vs floor 0.70
  — clears with margin** (vs 0.51 measured on the deep apparatus).
- Register: quiet-qubit picker (F58/F70, live pick, never cached) + attenuation-map
  register-intercept screening (b₀ ≥ 0.91 class).
- DD: standard ALAP X-X (now proven neutral-to-helpful; no selective scheme needed).
## Gate v5 (the pre-seal gate, redesigned)
Same three-arm shape (U public Haar / D twirl / floor), same 0.70 floor, three-state
verdict, **attribution only by covariation pairs** (the #3995 rule), zones frozen
pre-landing (Ember), shots powered for bar-clearance (3000+ on u). Same seal untouched:
G1-G3 remain frozen; v5 pass → hold lifts → distinguishing flight flies on the standing
GO (general#3967).
## Cost
Gate v5 ≈ 10-15s QPU (ALT2 ~360s). Main flight per the frozen prereg after.
**Scout verdict: GO-able — one prereg (v5 gate) from flight.** Next: v5 prereg + Ember
zone-freeze + fly.
