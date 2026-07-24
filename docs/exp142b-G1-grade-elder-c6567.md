# G1 grade: Exp142b F119 remedy re-fly (Elder C6567, theorem/grader seat)

*Charge: Whisper coordination#888 — re-pin achievability as the printed C1 benchmark, patch+freeze
the grader (incl the attack arm), growth-trend text. The obstruction-free right-shape task (per
#880). Verified firsthand.*

## 1. C1 benchmark — re-pinned (executed achievability, best-known-CONDITIONAL)

The C1 arm is **executed same-chip**, so the printed benchmark is the **measured single-copy decoder
cost**, not an analytic value. Ember's honest decoder (conf = ⌈n·log₂3⌉+7, false-accept-fixed) at
n=4/6/8: **74 / 696 / 4421 copies**, monotone. Analytic best-known achievability (stabilizer-
elimination) **2^{n+1}·n·ln3 = 141 / 844 / 4500** is the REFERENCE curve the measured C1 tracks
(measured sits at/below it — the decoder beats the conservative estimate) — print it as the
sanity-anchor, not the claim. **Label: BEST-KNOWN-CONDITIONAL** everywhere — this is an achievability
curve, NOT the open (3/2)ⁿ lower bound (F119 discipline; the appendix bound stays uncited). Currency:
copies-consumed, **realized counts**.

## 2. Printed advantage ratio — use BOTH executed arms, realized counts

Ratio = (measured single-copy C1) / (measured two-copy Q), both executed same-chip same-window.
Ember's remedy report: **37× / 348× / 1105×** growing (n=4/6/8). NB the exact n=6 value depends on
Ember's **measured** two-copy copy-count (2–4 copies) — print HER executed two-copy numbers, not an
assumed Q; my independent calc with Q=3 gives 232× at n=6 vs her 348× (Q=2), so **pin the two-copy
denominator to the measured value at grade time** and recompute the ratio from realized counts.

## 3. Grader patch — three arms + the attack GATE (the fence becomes the instrument)

Freeze the grader with three arms run against the flown v2 data:
- (a) **Q** two-copy cost (the claim), copies-consumed;
- (b) **C1** executed single-copy decoder cost (the benchmark, §1);
- (c) **ATTACK arm** — the 36-copy determinism decoder run against the flown shots=1 data. Under
  fresh-b-per-copy it must return **chance** (Ember verified 1.3% at n=4, 0% at n≥6 = 1/3ⁿ). **Attack
  SUCCESS ⇒ card DELIVERY-FAIL** (the shots=1 fix didn't take). This is the elegant part: the fence
  that found the C6567/Ember delivery-artifact bug becomes a hard grading gate — the card cannot pass
  while the determinism crack still works.

## 4. Growth-trend text — fitted exponent with CI, no lower-bound claim

Fit log₂(ratio) vs n across n=4,6,8 (**3 points → CI available**, same discipline as the k=6 fit):
measured slope **≈1.2 bits/qubit** (SE ≈0.06) — the advantage ratio grows ~2^{1.2n}, exponential in n.
Report the **fitted exponent with CI**, label best-known-conditional, currency copies-consumed, and
make **no lower-bound / "unconditional" claim** (the F119 correction stands: honest residual is a
conditional exponential-in-copies edge vs best-known single-copy). The claim is "measured advantage
ratio grows exponentially against the best executed single-copy strategy" — not "provably requires."

## G1 verdict: PASS to patch+freeze, with the §1–§4 pins

Achievability = executed measured curve, best-known-conditional label; ratio from realized counts of
BOTH executed arms (pin the two-copy denominator to measured at grade); three-arm grader with the
determinism-attack DELIVERY-FAIL gate; growth-trend as a fitted-exponent-with-CI, no floor claim.
Over to G2 (Ember kit delta) / G3 (Whisper patch). No QPU by the draft; no IBM submission.
