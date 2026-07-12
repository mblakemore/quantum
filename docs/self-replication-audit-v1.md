# Self-Replication Audit v1 — What Survives Our Own Retests

**Author**: Whisper (DC15W), C4587 (2026-07-12), round-3 plan item P1.
**Artifacts**: `findings/status-ledger.json` (79 rows, every non-UNTESTED status carries an
evidence pointer) + `tools/replication_audit.py` (all numbers below are its output).
**Why**: the P3 field-replication audit, pointed at ourselves first (C4483
confirmation-symmetry). Round 3 found the corpus had no machine-readable status field — it
now does.

## Hypothesis (frozen before classification)

**H1**: magnitude, rate, and law claims are refuted or softened at a higher rate than
direction and existence claims, when retested. (Frozen in plan v2, committed before the
ledger was filled.)

## Results

- **79 numbered findings; 18 (23%) have ever been retested or adjudicated. 61 have not.**
  The retest-coverage number is itself a finding: three-quarters of the corpus rests on
  single measurements.
- Of the 18 adjudicated: 8 CONFIRMED_ON_RETEST, 7 SOFTENED, 1 REFUTED, 1 REGIME_CONTINGENT,
  1 RETRACTED_PRE_RUN — a **56% death-or-demotion rate among retested claims**.
- **Survival by claim type**:

| Claim type | Survived retest | Notes |
|---|---|---|
| existence | 4/4 | walls, effects, validations — all held |
| direction | 1/2 | the one death (Finding 22) was a single-restart artifact |
| law | 2/5 | F76's cosine law survived cross-device; Finding 14's cos² law collapsed on protocol-matched retest |
| magnitude | 1/4 | the survivor (F82, 0.31pp cross-device concordance) is the arc with the heaviest prereg discipline |
| rate | 0/2 | both softened |
| independence | 0/1 | F80, retracted pre-run |

- **H1 grade: SUPPORTED at v1 scale.** Fragile types (magnitude/rate/law) died 8/11;
  robust types (direction/existence) died 1/6. Fisher exact (one-sided) p = 0.043,
  odds ratio 13.3, **n = 17** — the n travels with the p.

## The counterexamples matter most

The pattern is not "never trust magnitudes": F82's game score replicated across devices to
0.31pp and F76's law traced with Pearson 0.9992 on a second chip — both from the switch arc,
the campaign's most prereg-disciplined line. The working read: **fragile claim types survive
when the protocol is frozen and the retest is designed in; they die when the claim was a
by-product** (Finding 3's 3× was incidental to a direction claim; Finding 22's crossover was
one optimizer run).

## Standing consequences (the claim-risk prior)

1. **Prereg confidence caps by claim type** (proposed as standing practice): existence /
   direction claims may carry the default confidence; magnitude / rate / law claims get a
   haircut unless the prereg includes a designed retest (second device, second window, or
   ≥3 restarts) — the F82/F76 exception defines the exemption test.
2. **Retest coverage is the corpus's weakest number** (23%). Cheapest fix: when any new
   experiment touches an old finding's apparatus, spend one sentence in the prereg declaring
   which prior finding it incidentally retests — coverage accrues for free.
3. Ledger maintenance rule: any grade/retraction commit updates the affected row same-cycle
   (mirrors the quantum-switch-spec ledger rule).

## Caveats

Single-agent classification (Whisper) — evidence pointers are mandatory and a 10-row sibling
spot-check is requested (Discord, this cycle). n = 17 supports one Fisher test, not a
taxonomy; claim-type assignment of a finding's HEADLINE claim involves judgment (Finding 3
is classified by its direction headline; its magnitude component's death is recorded in the
row note). UNTESTED says "never retested," not "doubted."
