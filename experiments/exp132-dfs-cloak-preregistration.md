# Exp132 Pre-Registration — THE CLOAKING DEVICE: DFS vs Echo vs Bare (Horizons-3 H3)

**Author**: Whisper (DC15W), C4671 (2026-07-13) · **Substrate**: claude-opus-4-8
**Status**: FROZEN before hardware submission
**Directive**: Creator ("getting numbered, next one!") — Horizons-3 H3, the *protection* genre
(new): can a qubit be hidden from the environment's gaze? Two protections raced against a bare
idling qubit down the delay ladder.

## Scope, stated first

- **What this is**: a three-way coherence race that doubles as a **noise-structure probe**.
  (1) **Passive** protection — a logical qubit in the decoherence-free subspace {|01⟩,|10⟩},
  immune to *collective* dephasing (both qubits share the phase → global phase → coherence
  untouched). (2) **Active** protection — a Hahn spin-echo (π pulse at the midpoint), which
  refocuses *low-frequency / quasi-static* dephasing. (3) **Bare** idle — the baseline. All
  measured with the **phase-blind coherence estimator** (F100 law is standing for coherence
  claims): C_L = √(⟨X_L⟩²+⟨Y_L⟩²) for the logical qubit, C = √(⟨X⟩²+⟨Y⟩²) for bare/echo.
- **The confound-breaker**: fake backends model **memoryless, independent** noise — so they
  **cannot preview either benefit** (sim: DFS ratio 0.15, echo ratio 0.97 ≈ 1). Any
  hardware win is therefore evidence of REAL noise structure the vendor model omits — the
  DFS probes the **spatial (collective)** correlation, the echo probes the **temporal
  (low-frequency)** correlation. Ties to the noise-structure arc (F04 non-Markovian, F55–56
  structured CZ noise, F81 vendor-calibration-misses).
- **Both outcomes pre-registered** (F85/F130 discipline): each protection either helps or
  doesn't, and either is a finding about the noise. Fairness: each curve is normalized to its
  own t=0 (removes prep-error offset — the comparison is decay, not absolute |V|).
- **What this is NOT**: not a claim that DFS is the right code for this hardware (the sim
  predicts it isn't); not a general echo-beats-DFS theorem (substrate-specific). Prior art
  plain: DFS (Lidar et al.), Hahn echo (1950) are textbook; the contribution is the frozen
  three-way phase-blind race as a vendor-model-gap probe.

## Apparatus

Two adjacent calibration-gated qubits (min 2q + readout). Logical |+_L⟩=(|01⟩+|10⟩)/√2 via
X(q1) H(q0) CX(q0,q1). Delay ladder **[0, 30, 60, 120] µs** of idle (per qubit for the logical
pair). Arms: logical (4 correlators XX/YY/XY/YX per delay), bare (X/Y per delay), echo (X/Y per
delay, π at midpoint). 4·4 + 2·4 + 2·4 = 32 payload + 2 sentinels, 8000 shots (~272k),
shuffled (seed 4671), co-batched.

## Frozen gates (on normalized coherence at the max delay d\* = 120 µs — model-free)

| Gate | Statement | PASS condition |
|---|---|---|
| **W1_ACTIVE_BEATS_PASSIVE** (primary) | active refocusing retains more coherence than the DFS code | echo_norm(d\*) − DFS_norm(d\*) > 5·SE |
| **W2_ECHO_PROTECTS** (both outcomes) | is there refocusable (low-freq) noise the model misses? | ECHO_PROTECTS if echo_norm(d\*) − bare_norm(d\*) > 0.05 + 5·SE; else MEMORYLESS (bare/echo at 12000 shots for SE) |
| **W3_DFS** (both outcomes) | is the dephasing collective enough for passive protection? | CLOAK if DFS_norm(d\*) > bare_norm(d\*)+5·SE; else NO_PASSIVE_PROTECTION (report DFS/bare ratio vs the fake's independent-noise floor 0.15 as the collective-fraction figure) |
| **G_PHASEBLIND** | estimator validity | noiseless C = 1 at all delays (verified at design: PASS) |
| **G_SENT** | prep/readout integrity | both sentinels ≥ 0.95 |

**Figures of merit**: fitted T2 ratios T2_echo/T2_bare and T2_DFS/T2_bare; the per-delay
coherence curves; the DFS/bare ratio vs the fake independent-noise floor (collective fraction).
**Fake preview** (memoryless model): DFS_ratio 0.15, echo_ratio 0.97 — both "fail" by
construction, which is the point. Noiseless estimator check PASS.

**Pre-filed predictions**: W1 (echo beats DFS) HIT conf 0.95 (near-certain — DFS is doubly hit
by T1 leakage of the single-excitation code + differential dephasing); W2 = **ECHO_PROTECTS**
conf 0.80 (real IBM noise has refocusable low-frequency structure the fake omits — betting
real ≠ fake); W3 = **NO_PASSIVE_PROTECTION** conf 0.75 (IBM dephasing substantially
independent; but DFS/bare likely > fake floor 0.15, showing a nonzero collective fraction);
G_SENT conf 0.92.

**NO-TEST conditions**: sentinel failure → window NO-TEST; logical-arm 2q count ≠ 1 CX (prep)
per correlator, echo arm 2q = 0 (audited pre-submit) → abort; if the noiseless estimator check
had failed → no flight (it passed).

## Relation to the campaign

Adds the **protection** genre and a fresh **noise-structure** result: whichever protection
wins, it exposes a correlation (spatial via DFS, temporal via echo) the vendor's memoryless
independent-noise model omits — a direct successor to F81 (our sentinel out-predicts the
vendor calibration feed). The three-way phase-blind race is a reusable noise-anatomy probe.
