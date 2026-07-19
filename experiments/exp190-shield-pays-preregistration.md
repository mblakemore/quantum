# Exp190 Pre-registration — THE SHIELD PAYS: time-matched survival + the first mid-circuit syndrome (Shields arc, stage ii)

**Cycle**: C4880 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 16 circuits
**Arc**: THE SHIELDS, stage (ii) of (i) shields up → (ii) **does it pay** → (iii) logical Bell
pair → (iv) teleport a logical qubit. Creator go: general#126.

## The three rungs

**Rung 1 — time-matched survival (fixes stage (i)'s named caveat).** Logical |+̄+̄⟩ vs bare
|++⟩ idling the SAME wall time T ∈ {0, 2 μs, 4 μs} (4000/8000 dt), BOTH echo-protected
(midpoint + endpoint refocusing pairs), X-basis readout — the basis dephasing actually kills.
The code detects single-Z errors (they flip XXXX); post-selection should make the accepted
logical error grow *slower* than the bare error with dose.

**Rung 2 — the stabilizer IS the echo (design discovery, stated in advance).** The echo
operator on the logical arms is **X⊗4 = the code's own XXXX stabilizer**: logical identity on
the codespace, commutes with both syndromes, anticommutes qubit-wise with Z noise — the
[[4,2,2]] code's shield and its Hahn echo are the *same algebra*. Used at every idle midpoint
and around the syndrome window.

**Rung 3 — mid-circuit syndrome = full error-type coverage (the FT primitive).** An ancilla
measures XXXX mid-circuit (H, 4×CX, H, measure) between two idles, with terminal readout:
- In the **Z-readout family**, terminal ZZZZ catches X errors but is *provably blind* to Z
  errors (they commute with every measured operator). The mid XXXX syndrome adds the missing
  coverage. Falsifier pair, both directions: `inject_z_mid` (deliberate Z after encode → mid
  syndrome REJECTS) vs `inject_z_nomid` (same error, no mid syndrome → ACCEPTED — the stage-(i)
  blind spot, demonstrated).
- In the **X-readout family**, the echo's value through the syndrome *window* is measurable on
  the logical error: `synd_echoed_X` vs `synd_unechoed_X` (the window law, on logical qubits).

## Circuits (16)

Survival X: Lx_T0, Lx_T1, Lx_T2, Lx_T2_unechoed, bx_T0, bx_T1, bx_T2 ·
Survival Z (secondary): Lz_T0, Lz_T2, bz_T0, bz_T2 ·
Syndrome: synd_echoed_X, synd_unechoed_X, inject_z_mid, inject_z_nomid, plus synd_clean_Z
(acceptance/logical reference for the coverage pair).

## Pre-registered criteria (as formulas — checklist item 6; bars from null distributions — item 7)

Let e_L(T) = accepted logical X-error/qubit, e_b(T) = bare X-error/qubit (echoed arms);
se of each error rate ≈ √(e(1−e)/N) with N ≈ 2·8000·acceptance.

- **Primary (survival)**: `e_L(T2) < e_b(T2)` with `(e_b − e_L)/√(se_L² + se_b²) ≥ 3`.
  Band: ratio e_L/e_b at T2 ∈ 0.15–0.75. Trend gauge: ratio non-increasing in T (reported).
- **Coverage falsifier pair**: `P(reject | inject_z_mid) ≥ 0.90` AND
  `P(accept | inject_z_nomid) ≥ 0.90` (ses ≈ 0.003 — bars are >25σ from the null).
- **Window echo on logical qubits**: `e_L(synd_echoed_X) < e_L(synd_unechoed_X)` at ≥2σ
  (band for the gap: 0.005–0.06; the window dose on 4 spectators, partially coherent per
  Exp178).
- **Gauges**: acceptance — survival arms ≥ 0.85 at T0 falling to ≥ 0.65 at T2 (band);
  syndrome arms 0.50–0.85 (8 extra CX + window). Bare-vs-logical Z-family at T2 reported
  (Z-basis is T1/dephasing-insensitive for these states; expected near-tie — a null lane, per
  the null-sector rule).

## Fences

Distance 2: detection + post-selection, never correction; acceptance is a real cost, reported
everywhere. One mid-circuit syndrome round (repeated rounds = stage (iii) territory). Delay
values are granularity-rounded; echo pairs are exact identities on the codespace (X⊗4 twice)
and on bare qubits (X twice per qubit). One die, one job.

## Discipline

ps aux: clean. Claim: exp190 (whisper C4880). Ledger prediction pre-submit. Prereg committed
before decode. Selftest gates (formulas): all clean arms exact (acceptance 1, e = 0);
inject_z_mid rejection = 1; inject_z_nomid acceptance = 1 with terminal syndrome blind
(demonstrating the blindness noiselessly); echo pairs exact identities.
