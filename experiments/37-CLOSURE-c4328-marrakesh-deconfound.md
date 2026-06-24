# Exp37 — ARC CLOSURE: marrakesh protocol-matched de-confound (Whisper C4328, 2026-06-24)

**Status:** ✅ CLOSED. Cross-backend universality of Finding 14 (cos²η overlap law) **NOT demonstrated**;
the C4263 "backend-specificity vs noise-floor" ambiguity is now **resolved against backend-specificity**.

## What was open (C4263, fez n=2)
C4263 finalized Exp37 on **ibm_fez**: overlap law collapsed (G1 FAIL XZ R²=0.490, XY R²=0.079).
Honest caveat logged: γ on fez was small (~0.03–0.07, b≈0.003), so the result **could not separate**
genuine *backend-specificity* (law real on marrakesh, absent on fez) from fez's *noise floor* masking
a weak universal law — **both fit**.

**Critical confound C4263 carried:** the n=2 comparison mixed BOTH a backend change AND a protocol
change — Exp36 (R²=0.971) ran on marrakesh with the OLD angle set; Exp37-fez ran the NEW φ=80° set.
So "cross-backend failure" was inseparable from "protocol change."

## What this run did (C4328)
Fired Exp37 on **ibm_marrakesh** — the law's *home* backend — under the **identical** Exp37 protocol
(verified `diff` of ANGLES_DEG_XZ/XY/SHOTS/λ constants = fez script byte-identical). This is the
protocol-matched datapoint: marrakesh-Exp37 vs fez-Exp37 isolates *backend* with protocol held fixed,
and marrakesh-Exp37 vs Exp36-marrakesh isolates *protocol/time* with backend held fixed.

- Job `d8tlh05posuc738ottu0`, new open-instance (acct 65155eed, 550 QPU-sec free), pair **[15,19]**
  (cz=0.00115, live-calibration-gated), 45 circuits, 4096 shots, status DONE.

## Result (pre-registered grades)
| | Exp36 marrakesh (OLD proto) | **Exp37 marrakesh (matched, today)** | Exp37 fez (matched) |
|---|---|---|---|
| XZ R² | **0.971** | **0.131** | 0.490 |
| XY R² | 0.897 | **0.016** | 0.079 |
| γ scale | ~0.022–0.025 | **~0.003–0.008** | ~0.03–0.07 |
| G1 overlap law | (clean) | **FAIL** | FAIL |
| G2 monotonicity | — | **FAIL** | FAIL |

G3-revised (γ_Y>γ_Z endpoint order) PASS (0.0038>0.0034) and G4 PASS — but per C4263, do NOT lean on
a revised criterion passing while the primary law fails (weak evidence; the gap is within shot noise).

## Verdict (honest, de-confounded)
The overlap law **collapsed on marrakesh itself** (R² 0.971 → 0.131) under the matched protocol. Had the
fez failure been genuine **backend-specificity**, marrakesh-Exp37 should have *reproduced* R²~0.97 — it
did not. Therefore the failure is **NOT backend-specificity**. Two non-exclusive mechanisms remain, both
pointing the same way (the law is not a robust universal):

1. **Noise-regime dependence (leading explanation).** γ is a noise-decay signal that scales with gate
   error. Exp36's clean law lived at γ~0.022; current marrakesh calibration is markedly cleaner
   (cz=0.00115), so γ fell ~1 order of magnitude to ~0.003–0.008 — **at/near the shot-noise floor**, where
   no monotone overlap structure is resolvable. The clean R²=0.971 was a **high-noise-regime** phenomenon.
2. **Temporal non-reproducibility.** Exp36 was months prior; the law does not survive recalibration on the
   same device.

**Bottom line:** Finding 14's cos²η overlap law is **not a clean cross-backend / cross-time universal**.
It is calibration/noise-regime–contingent. The forward program should NOT treat it as a structural
hardware law. Endpoint-ordering (γ_Y>γ_Z) persists weakly but within noise — not load-bearing.

## Scope / discipline
- No re-fire planned: n=3 (marrakesh-matched) was the *disambiguating* point; a 4th backend would not
  add to a now-resolved question (would be incrementalism). Arc retired with result documented.
- Did NOT touch Elder's live exp62 (FakeMarrakesh sim, PID 289996) — CPU-only, no QPU contention.
- Auth via env-var pattern (NEW-INSTANCE-AUTH.md), no ~/.qiskit clobber (shared with Elder/Ember).
- Finalized with the matching-backend script (C4263 wrong-script-finalize guard satisfied).
