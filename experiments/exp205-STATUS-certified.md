# Exp205 — THE BLIND ANTENNA: CERTIFIED (all 4 gates)

**Whisper C4902, 2026-07-20. Job `d9ehf2aneu4c739of7qg`, `ibm_fez`, 51 circuits, 8000
shots, seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`496bd14`).**
Horizons-4 Invention 3 (rank 6), flown on the Creator's standing go.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3∧G4): HELD.** The shield's blind spot is a working sensor.

The composition thesis, measured: Exp199 proved the [[4,2,2]] blind spot sits at global
coherent Z-rotations; a global Z-rotation is what a phase sensor reads; therefore the blind
spot is the antenna. Every derived signature landed on hardware.

## The four results

**G1 — the fringes are clean.** Fixed-frequency visibilities V_bare = 0.991, V_ghz4 =
0.887, V_log = 0.942; phase offsets all |δ| ≤ 0.03 rad; residuals ≤ 0.047. The shielded
sensor's fringe is as visible as the bare qubit's.

**G2 — super-resolution structure, un-fakeable.** Joint-orthogonal frequency ID returns the
dominant harmonic with overwhelming margin: bare **k=1** (ratio 122), ghz4 **k=4** (ratio
25), logical **k=2** (ratio 34). The Bell⊗Bell code state genuinely reads the field at 2φ —
2× super-resolution over a single qubit, from a 2-CX probe. Frequency is set by physics, not
visibility.

**G3 — the aperture is 199's curve.** The acceptance rides (1+cos²2φ)/2 to max residual
0.037 (in-arm parametric, no fit), and the signed non-monotonicity is exact: acc0 = 0.943 →
**acc(π/4) = 0.499** (narrowest, at the steepest operating point) → acc(π/2) = 0.927
(199's constructive addback). **Exp199's blind-spot acceptance curve is re-certified in-sweep
as the sensor's lens** — the same physics, read as an instrument instead of a vulnerability.

**G4 — the sharpened fringe (the invention gate).** Postselection strips the flat component:
X̄₁_post tracks 2c/(1+c²) with V_p = 0.920, residual 0.074. The payoff at φ=π/4: **post slope
−3.197 vs bare −0.716 — a 4.47× sharpening at 32.4σ** (gate: ≥2× at 5σ). Fisher information
per accepted shot **10.27 vs 4× the bare best (3.93), at 18.2σ** (gate: ≥4× at 3σ). A 2-CX
error-detected probe delivers metrological sensitivity that would otherwise need a
GHZ-class entangled state — *and it flags its own errors*.

## G5 (reported): the honest throughput comparison

| Probe | Fisher/shot | acceptance | Fisher/**raw** shot |
|---|---|---|---|
| bare (SQL) | 0.98 | 1.00 | 0.98 |
| GHZ-4 (bare super-resolution) | 12.58 | 1.00 | 12.58 |
| **logical (shielded, post-selected)** | 10.27 /accepted | 0.499 | **5.13** |

The filed conf-0.6 prediction **HELD**: on this window the bare 4-GHZ wins raw-shot Fisher
(12.58 > 5.13) — its visibility survived (0.887). So the shielded sensor is *not* a
free-lunch beat of an ideal GHZ at the throughput level. What it delivers is different and
real: **per-accepted-shot sensitivity equal to a bare 4-GHZ from half the entangling depth,
with error detection built in** — the regime that matters when the GHZ visibility does *not*
survive (deeper probes, worse windows). The honest scope: this window was kind to the GHZ;
the shield's advantage is robustness-per-depth, demonstrated in the sharpening, not a
throughput win here.

## Budget scoreboard (graded straight)

V_bare 0.991 ∈ [0.90,0.99] **IN** (top); V_log 0.942 ∈ [0.70,0.92] — **0.02 over** (better
than priced); V_ghz4 0.887 ∈ [0.45,0.85] — **0.037 over** (GHZ survived better than priced,
which is why G5's comparison went to it); slope ratio 4.47 ∈ [2.5,4.5] **IN** (top);
F_post/accepted 10.27 ∈ [6,15] **IN**. 3/5 in band, 2 grazes both in the good direction
(everything cleaner than priced).

## What enters the record

1. **The shield's blind spot, converted to an instrument.** 199 measured a vulnerability
   (coherent errors pass inspection); 205 measured the *same physics* as a sensor's antenna
   and aperture. A finding becomes a feature — the first time a measured error-detection
   blind spot has been used as the signal path.
2. **Metrology inside the shield works, and postselection sharpens it.** Fisher information
   is preserved and concentrated by error detection — the metrological analog of 196's
   "the shield preserves CHSH." Invention 3 delivered.
3. **The honest boundary**: on a good window a bare GHZ still wins raw throughput; the
   shielded sensor's edge is sensitivity-per-entangling-depth plus self-diagnosis, not an
   unconditional Fisher win. F109's lesson (scaling verdicts are task- and window-dependent)
   applies to sensing too.
4. First flight on the `claude-opus-4-8` substrate in this campaign (stamped per C4054).

## Line

**We found the shield's blind spot by shining a coherent error through it (199). We just
pointed the same blind spot at the sky and read a field with it — the flaw and the antenna
are the same aperture.**
