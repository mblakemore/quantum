# The n-ladder — does the sealed-shadow advantage GROW with n? PRE-REGISTRATION (FROZEN pending Creator GO)

**Whisper · C5086 · board #175 · Status: DRAFT — corrected after Ember's pre-freeze catch (general#17706). FROZEN pending her sign-off + a Creator GO citing this file's + the runner's digest.**
**Frame:** LABELED ADVANTAGE-SCALING test on the campaign's flagship (F122). Not a new advantage claim — a
measurement of whether the two-copy protocol still DELIVERS at larger n, and thus whether F122's advantage scales.
Extends Ember's door-(b)/F122 machinery and ratio identity.

## The question, one sentence
F122 is one point (n=16). This flies the same protocol across a ladder of n and asks: does the two-copy protocol
keep delivering its contrast as the state widens, or does the delivered contrast collapse at the NISQ width wall?

## Ember's identity — general form, K(n) unfrozen (CORRECTED per general#17706)
Ember's ratio identity (doorb_ratio_identity.py, court-verified #8431), with n unfrozen:
**`ratio(n) = (2^n / K(n)) · ε_size⁴ / ε_del²`,  `K(n) = 4·ln(2·4^n/δ)`, δ=0.05.**
- ε_size = the contrast at the CALIBRATION gate (weather, blind to the sealed P). ε_del = the contrast the FLIGHT
  delivers. They are MEASURED INDEPENDENTLY per rung — NOT equal. (My first draft wrongly used the normalized form
  2^n·ε_del²/K, which is valid only at ε_size=ε_del; Ember caught it before freeze — the correction is in the fences.)
- **REPRODUCTION TEST (correct form, PASS):** ratio(16, ε_size=0.1616, ε_del=0.1839) = **12.77** — reproduces
  Ember's registered w12 branch exactly. K(16,0.05)=103.478 also reproduces her L. Both halves now checked.

## ⚠️ THE RATIO IS NOT THE FALSIFIABLE OBSERVABLE — it INVERTS on hardware failure (Ember general#17706)
ε_del sits in the DENOMINATOR. A NISQ collapse of the delivered contrast makes the single-copy FLOOR (2^n/ε_del²)
grow faster than the two-copy budget, so the ratio **GROWS**. At n=16, holding the registered ε_size=0.1616 and
starting from F122's delivered ε_del=0.1839 (which returns the reproduction value 12.77): a collapse to ε_del=0.09
takes the ratio **12.77 → 53.32 (4.2×)** while the truth r=ε_del/ε_size **DROPS 1.14 → 0.56**. The ratio and the
delivered contrast move in OPPOSITE directions — both numbers recomputed from the general form above, δ=0.05. A raw
ratio that goes UP when the flight degrades would CONFIRM the scaling advantage on exactly the failure that should
kill it. **The ratio is a hardware-failure amplifier, not a scaling witness.**

## The graded OBSERVABLE (Ember's own point: "report ε_del, the ratio was never the observable")
Per rung, measure DIRECTLY: **ε_size(n)** (calibration gate) and **ε_del(n)** (flight), and their ratio
**r(n) = ε_del(n) / ε_size(n)** — does the flight DELIVER the contrast the calibration promised, at width n?

## Frozen PREDICTION (before any bar)
- **P1 (the real claim):** the two-copy protocol DELIVERS at width — **r(n) = ε_del(n)/ε_size(n) ≈ 1** across the
  ladder. When it holds, the derived advantage grows ~2^n/K(n) as a CONSEQUENCE (0.15 at n=8, crosses 1 near n=12,
  21.7 at n=16, ~3884 at n=24) — but that curve is reported, not graded.
- **P2 (ruler check):** the n=16 rung's (ε_size, ε_del) reproduces F122's on this protocol. **If the free-ibm_fez
  path is chosen, this n=16 rung is a CROSS-DEVICE ruler** (free-ibm_fez n=16 vs F122's paid-marrakesh) — REQUIRED by
  Ember (general#17723): without it a free-device ladder and the paid F122 result are not on the same scale, and every
  rung compares against a number from another machine. On the paid-marrakesh path this rung is same-device to F122.

## Frozen FALSIFIERS (any → honest negative)
- **r(n) = ε_del(n)/ε_size(n) drops below ~0.8 at large n** → the flight fails to deliver the calibration contrast on
  the wider state → the NISQ WIDTH WALL → the advantage is illusory at that n (the raw ratio would INFLATE here — that
  inflation is the tell, not a win). This is the F85/F108 metrology scaling-inversion pattern in the LEARNING domain.
- **The raw ratio is NOT graded as the witness** — it is reported alongside, precisely because it inverts. Any read
  that treats the ratio growing as confirmation is rejected by construction (this fence exists because I made that
  exact error in the first draft).
- n=16 rung's ε_del disagrees with F122 by >3σ → not on F122's ruler → comparison void.
- Any rung's decoder selftest (G-DECODE/F-BIAS/F-IND/F-MIX) fails → REFUSE that rung.

## The lesson this prereg carries (from the first-draft error)
A reproduction test that fixes ONE component (K) while the rest of the form varies will PASS on a different formula —
my K-half was perfect, which is exactly what let the ε_del inversion hide. A reproduction test proves a function is
the same function only if it exercises the WHOLE form, not one true sub-term. The correct-form test (→12.77) does.

## The flight (Ember's n-parametrized machinery, unchanged)
`tools/doorb_flight_ember_c4262.py --n <n> --fly`. Selftests PASS at n=8,20 ($0). Prep is a PRODUCT eigenstate of the
sealed P — CONSTANT depth at all n (verified: transpiled depth 9 at n=20 AND n=24); only WIDTH (2n) and readout scale,
which is exactly what the r(n) falsifier probes.

## Ladder, budget, device (frozen)
- **n-values:** {8, 12, 16, 20}; **24 conditional** — feasibility PASSED $0 (48 qubits, depth 9, fits ibm_fez).
- **Per-rung:** over-flown to a common 50,000 copies/rung (25,000 Bell shots) so ε_del is measured cleanly at every n.
- **Device/account — UNRESOLVED, a Creator + Ember decision (caught pre-freeze by reading the flight):** the draft
  claimed "free ibm_fez" — WRONG. Ember's doorb_flight, used unchanged, flies on the PAID account (PAID_CRN) and
  PINS ibm_marrakesh (EXPECTED_BACKEND, paid). So as-written this is a PAID multi-rung spend needing explicit Creator
  paid-authorization ("GO when ready" does NOT cover a paid submission I had not flagged). ALTERNATIVE: adapt the
  flight's account to the free open-instance (ibm_fez) — $0, but it MODIFIES Ember's flight and puts the n=16 rung on
  a different device than F122's marrakesh (the ladder stays device-internal; the P2 ruler check to F122 becomes
  cross-device). The device/account is FROZEN only once the Creator rules paid-auth vs free-adapt.
- **Seal — needs Ember's mechanism for the NEW n's:** each rung needs a pre-committed sealed P (G-SEAL reads
  ~/.ember-doorb-secrets.json + experiments/doorb_commitments/doorb_commitment_n{n}.json). Only n=16 exists; n∈{8,12,
  20,24} have NO commitment. Committing sealed P's for the new rungs is Ember's secrets machinery — coordinated, not
  soloed. Incremental-atomic batch pattern (F122-dist across weight; this across n).

## Gates (before freeze)
attack_preflight --claim · preflight_account_check on the runner · (feasibility DONE).

## What a GO authorizes (single-use, seal-bound)
One batch submission of the frozen runner (digest at freeze) to ibm_fez, once, BACKGROUND. Each rung's job_id recorded.

## Coordination (cross-seat — the check already worked once)
Extends Ember's flagship identity + machinery. She caught the normalized-vs-general inversion before freeze
(general#17706); this draft is the correction. @ember sign-off on this corrected form is the gate before freezing.
