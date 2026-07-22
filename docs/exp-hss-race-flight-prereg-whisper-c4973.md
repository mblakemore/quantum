# Exp-HSS Race Flight — FROZEN PRE-REGISTRATION (the one deliberate spend)

*Whisper C4973, 2026-07-22, substrate claude-fable-5. Creator directive: "freeze and fly." This
card is FROZEN BEFORE circuit generation and submission; the git commit of this file IS the
freeze. Phase-A inputs, all closed: threshold calibration 2-of-2 (kc exact, one-sided), ball
decoder verified + structured null (Ember, quantum@b57d417), t=80 edge-robust classical gate
(Elder C6563), quantum wall ≥71× tier-1, kingston noise band closed-by-design → RUNG-0 self-gate
(`exp-hss-kingston-noise-band-whisper-c4972.md`). The C4971 NO-GO stays booked; this is the fresh
pre-registration it left open.*

## Device — chosen pre-flight, operational grounds, stated before any data

**ibm_marrakesh.** Reasons, in order: (1) live queues at freeze time: kingston 298 pending,
marrakesh 0, fez 1 — "fly tonight" is only real on marrakesh; (2) the twirl + pinned-placement
machinery was validated on marrakesh this week (steth arc, quantum@9eea11a → d1a82be); (3) λ
anchor 0.00936 is mid-band, and the RUNG-0 self-gate makes device viability an in-job empirical
question rather than a pre-flight assumption — which is exactly why it exists. A kingston re-fly
remains a named option only if marrakesh's rung-0 folds AND kingston's queue clears; it would be
its own card.

## Sealed answers (commit-then-fly)

Planted shifts generated from seed 20260722 + secret salts; SHA-256 commitments frozen here; the
reveal file stays **uncommitted** until decode. Decode procedure MUST report ŝ (ball argmax)
publicly **before** opening the reveal.

- `race_n40`: `48503776c6aa7a1dec29a868df1be0527951168dbc74154c1606098e9b56b36e`
- `race_n32`: `cf0a5acff7e8e09dc7102e56fb229069031a387e6bbcaa60fa4cec7d6c38673a`

(Commitment = SHA256(s_str || salt). Solo-court note, stated plainly: flyer and decoder are the
same DC this flight; the seal is the pre-flight git-committed hash + the ŝ-before-reveal
procedure, with Ember/Elder invited to co-verify the reveal against this card. Weaker than
Exp142's 3-of-3 court; named, not hidden.)

## The job (one submission, co-batched, ~280k shots ≈ 70–150 s QPU of 3,216 s remaining)

| Block | Circuits | Shots | Purpose |
|---|---|---|---|
| **RUNG 0** — t=0 Clifford ladder, n=40 | base t=0 MM-bent hidden-shift, transpiled once, then folded G(G†G)^m at m=0,1,2,3 → d2q ≈ b, 3b, 5b, 7b (b ≈ base, brackets the race depth); K=4 twirls × 5k shots each | 4×20k | measure λ_marrakesh(d2q) in-family, in-job |
| **RACE n=40** — t=80 (10 CCZ) | frozen generator, sealed s, K=16 CZ-twirls × 6,250 shots | 100k | the race rung |
| **RACE n=32** — t=80 (10 CCZ) | same, sealed s | 100k | secondary rung |

- **Twirl**: every transpiled CZ dressed with random two-qubit Paulis, compensation = CZ-conjugated
  Pauli (Clifford algebra; global phase discarded). **Exactness gate before submission**: the full
  pipeline (fold + twirl) at n=16 must return the planted s with probability 1 noiseless, per twirl
  sampled — any failure aborts the flight.
- **Placement**: best-of-20 transpiler seeds, minimum d2q, layout pinned across all blocks
  (deterministic pre-registered rule; no post-hoc choice).
- **Tier-2 (1M-shot escalation)**: NOT in this job. It exists as a pre-registered follow-up ONLY if
  rung-0 passes the gate but race-rung ball counts land between the structured null and comfort —
  its trigger is written here so it cannot be a post-hoc rescue.

## The frozen decision rules

1. **RUNG-0 GATE (adjudicated first, before race rungs are even decoded)**: fit λ(d2q) from the
   ladder's measured R (Poisson-weighted fit on ln R; censored rungs handled as censored). Race
   rungs are graded **only if** the fit predicts R(race d2q) ≥ **3× the structured-null ball floor
   = 5.1×10⁻⁴** (floor 1.7×10⁻⁴ per Ember's verified structured null). If the gate fails: race
   rungs are **discarded ungraded**, and the flight's deliverable is the depth-resolved marrakesh
   attenuation curve (the map's v1.1 backlog item) + an honest window-closed-on-this-die verdict.
2. **Detection statistic (frozen)**: radius-1 **ball argmax** over the pooled race-rung counts
   (per Ember's verified implementation), with the structured null (readout-correlation +
   coherent residual — background ball-max class, NOT uniform multinomial). Detection claim
   requires ball(ŝ) ≥ the structured-null bar at one-sided 7σ FWER; raw-modal and per-bit are
   recorded as diagnostics only.
3. **Grading**: report ŝ per rung → open sealed reveal → ŝ == s exactly, or the rung is a MISS
   (no partial credit; HD is reported for the record).
4. **The race verdict (the Tracker-shaped deliverable)**: quantum cost = measured QPU-seconds
   (billed) for the race rung's shots + queue-honest wall quoted separately. Classical counterpart
   = **Elder's frozen edge-robust band at t=80** (n=40: 391–545 min best-credible-edge to
   proxy-edge; n=32: ≥70 min fast-edge) — paper-pinned γ=0.23, anti-flattering direction of error
   (Elder C6563; his verified extstab anchor row remains the labeled sized follow-up). WIN =
   detection + ŝ==s + quantum wall ≤ 1/10 of the classical band's lower edge. Every other outcome
   is booked as measured, no spin, per standing rule.
5. **Supersedable-by-design**: printed on the result. A future classical solver beating the band
   retires the number — that is the Tracker mechanism working, not a failure.

## Fences

Currency = time-to-verified-solution of a planted, self-verifying instance family
(best-known-simulator engineering race, NOT a complexity theorem — Exp142/F119 remains the
theorem-floored result, distinct currency). Joules: classical side TDP-bound from cost-map v1.0;
QPU side one-sided (vendor-unpublished, G2). n=16 calibration transfer to n=40 is argued (diffuse
term only dilutes) not simulated — the structured-null bar is carried at 3× for exactly this
reason. Rung-0 is calibration, not a Clifford "race" (Gottesman–Knill classically free). QPU pool
after this job: ~3,070–3,150 s remaining, no further HSS spend without a fresh card.

*Frozen at commit time. Flight script: `experiments/exp_hss_race_flight.py`. Contact: Mike
Blakemore.*
