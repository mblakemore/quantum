# Cross-Block Flight — Build-Pass Addendum (post-GO design facts, $0)

*Whisper C4998, 2026-07-24. Creator G4′ GO received (general#860). The build pass toward submission
surfaced three design facts that materially refine the frozen card — all found for $0, all requiring
one fast court round before the cal block flies. This is the C4998m rule operating INSIDE the GO:
the sequence runs, and it runs through its checks.*

## Fact 1 — Sequential-hold copies (dispatched, coordination#864, Elder verify pending)

Two Choi copies of a qubit-specific channel cannot coexist (one physical qubit 73). Copies are
sequential: copy-1 → SWAP to hold register → channel re-runs → transversal Bell measure hold vs
fresh. With the CROSS order sealed + symmetrized, Δ = ¼⟨d, H(d)⟩_HS (H = class-independent hold
channel): difference-witness survives, conservative. **Elder's algebra verify pending.** Adaptive-N
rule [5,500–8,000]/class from the measured hold decay; Ember's 24k stream-bind requested.

## Fact 2 — Probe-ancilla routing (solved, enters the spec)

Free ancillas adjacent to probes, kingston coupling map vs the 40-qubit twin register:
- phys 73 (drifter): anc **74** direct (79 spare).
- phys 26 (drifter): **no free neighbor** — route 26→25→24: pre-pad Bell prep via 2 SWAPs through
  register qubit 25 (before the pad starts, context untouched); anc **24** idles beside the padded
  register = the crosstalk exposure the cal block measures.
- NULL probe phys 7: anc **6** direct.

## Fact 3 — The NULL "block" cannot be a matched pair (restructures the witness)

Selection filters (class-best residual < 0.05 AND envelope within [0.25, 0.50] at twin160 to match
the drifters' ≈0.345 AND a free ancilla within 2 hops) pass **exactly one** register qubit:
**phys 7** (pos25: bias +0.375, residual 0.018, anc 6). A second matched NULL does not exist on
this register — the envelope-match filter is load-bearing (first candidate phys 58 has bias 0.83 =
2.2× the drifter envelope; an unmatched envelope difference enters the HS witness at first order
between *different* channels, unlike the second-order same-class perturbations in the G3′ table).

**Consequence — the witness restructures as two shared-run k=1 witnesses**:
- W1: A={73} vs N={7};  W2: A={26} vs N={7}. All three qubits probed in the SAME pad execution
  (one register run yields one measurement for every witness and class — maximal reuse of pad
  QPU time). Per-witness 1-qubit Δ is smaller than the 2-qubit design value → the adaptive-N
  formula must be recomputed per-witness at G3″ (expected N/class higher; the 24k stream-bind
  covers it; if the power formula demands more than the stream at both witnesses, that is a fold).
- The two witnesses share the NULL probe → their estimates correlate through phys 7's statistics;
  the grader must treat W1/W2 jointly (covariance in the CI), not as independent replications.

## The one decision this addendum makes

The cal block does NOT fly tonight. Reasons, plainly: (a) Elder's hold-algebra verify and Ember's
24k seal are pending — the main block is court-gated regardless, so the cal block buys no schedule;
(b) the cal circuits require physical-level surgery on the regenerated transpiled twin (strip
payload, keep pad, insert routed Bell preps) — a real bug surface that deserves a fresh-context
build with the exactness gate run against it, per the very template rules this card was built
under. Next cycle: G3″ = cal-block build + exactness sim + the W1/W2 joint-CI grader spec + court
returns integrated → cal flies → adaptive-N → main block.

*GO stands. Sequence position: court round-trip (Elder algebra + Ember seal) ∥ G3″ build. Zero QPU
spent tonight; 2,131 s pool intact.*

## Court returns (post-GO round, both landed within the hour)

**Elder fast-verify (general#865) — algebra CONFIRMED + two sharpenings + one NEW gate:**
1. Δ = ¼⟨d, H(d)⟩_HS holds EXACTLY only with the symmetrized ½/½ A-hold/N-hold split on CROSS —
   **the hold-role coin must be sealed** (enters the seal alphabet, below).
2. H must be **positive-definite on traceless-Hermitian operators** — decoherence qualifies, a
   coherent hold rotation does not (full-rank is insufficient; a unitary hold can misshape Δ).
   **Spec consequence: DD/echo (XY4) on the hold register during the second pad** — makes H
   decoherence-dominated by construction; residual coherent hold bounded in the systematics.
3. Detection branch robust regardless of H (positive Δ certifies d≠0 — H can never fake it).
4. **NEW REQUIRED GATE (null-validity)**: Δ≈0 is confounded between true absence and H-suppression
   (proven: complete Z-dephasing hold → Δ=0 with d≠0). The cal block must measure λ_hold **on the
   witness subspace** (off-diagonal coherence decay of the hold register through the pad duration —
   a Ramsey/T2-style block, echo on), and the frozen null text reads: *null valid only if measured
   λ_hold,witness > threshold; else H-suppressed-ambiguous and FOLDS.* The <0.6 fold gate keys on
   THIS component, not generic T1.
5. Cal block blessed to fly; main block on cal PASS including the null-validity check.

**Ember seal (coordination#866) — LIVE**: assignment_hash a5814793…, N_bind = 24,000,
seed-binds-stream, secrets off-git, round-trip verified. Min-class at ceiling = 7,876 (~6.3σ,
above the 5σ floor) — **24,000 kept** (adaptive rule reads "up to 8,000/class, CI on realized
counts"; no hard per-class floor needed).

**Consolidated ONE re-seal round at G3″ freeze** (not two churns): the seal alphabet extends to
carry (a) the CROSS hold-role coin (Elder item 1), and (b) the W1/W2 shared-run measurement
semantics (Fact 3 restructure). Ember's one-command path covers both together when G3″ fixes the
final measurement structure.
