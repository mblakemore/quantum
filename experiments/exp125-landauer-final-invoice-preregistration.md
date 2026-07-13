# Exp125 — THE FINAL INVOICE: the Landauer floor of the demon's record (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4663. Horizons-3 **H4** ("the final invoice / thermo-arc closure").
**Status**: FROZEN at commit — rules below fixed before stage 1 flies. Advisor-audited design
(three forks resolved before writing; see "Design audit" §).
**Arc**: F86→F88→F94→**F95 (engine full cycle)**→F97 (information did work) → **H4 = the erasure leg**,
the ledger line the engine never wrote. Ledger-closing companion to **H2** (negative-information ledger).

---

## The one honest question

The ICO engine (F95) booked deposit, extraction, demon-action cost — but never the **erasure** of the
demon's record. Landauer: resetting a one-bit record to a known state costs work ≥ k_BT·ln2. On this chip
k_BT is set by the qubit's **effective temperature** (residual excited population p_eq). In the engine's
own energy units (ℏω = 1, the 0.5-population passive line), the **minimum** erasure cost of one classical
bit is

  **floor(p_eq) = ln2 / ln((1−p_eq)/p_eq)   [E units]**   (Boltzmann: k_BT = 1/ln((1−p_eq)/p_eq)).

**Grade: does the Landauer FLOOR exceed the extraction CREDIT the record enabled?**
i.e. is `floor(p_eq) > W_credit` at 5σ. Two-sided by construction — the answer depends on the *measured*
p_eq and can come out either way on a hot-qubit window.

## Design audit (why NOT the literal sketch — advisor, C4663)

1. **Kill the literal headline** ("erasure dissipation ≥ credit"). The *actual* reset we use (T1 relaxation)
   dumps ~ℏω·p ≈ 0.5 E — it over-pays the ~0.092 E credit ~5:1 unconditionally. A gate that cannot fail is
   not physics (C4657/C4662 self-catch discipline). We grade the **floor**, not the dissipation.
2. **The floor is at-risk and its load-bearing input is p_eq** — measured per qubit (stage 1), never assumed.
3. **Bound audit vs our own H2 (load-bearing).** Standard Landauer k_BT·H(record) is the bound *only if the
   record is classical* (H ≥ 0). F95/F97's demon record is a **heralded / MEASURED bit** → classical → this
   floor applies, and this is what we grade. **We pre-register that a COHERENT (unmeasured) record obeys the
   conditional bound k_BT·H(record|system), and H2 certified S(B|A) ≤ −0.0986 < 0 — so a coherent record
   could be erased *below* this floor, even at net-negative work (Rio–Åberg–Renner–Vedral).** That coherent
   extension is H4's ledger-closing companion to H2; it needs coherent-record tomography and is **NOT graded
   here** — pre-registered as the follow-up (Exp125b).

## Banked credit (frozen, no new shots)

`W_credit = 0.0920 ± 0.0098 E` — the F95 gross charge→extract population drop (9.4σ from zero; SE from the
finding's 9.4σ/4.3σ clearances). Cross-check: F97 W1b = 0.099 E at 9σ (information's thermodynamic work).
Primary = F95 drop (the engine's own extraction). Using the *gross* drop (not net 0.034) is the
demon-friendly choice: the largest credit is the hardest for the floor to beat → conservative for a PASS.

## Stage 1 — measure the effective temperature p_eq (this cycle, ~cheap)

**Sites (frozen):** (a) the F97 engine pair member q=4 (same qubits that earned the credit); (b) the
frozen min-readout-error qubit (argmin readout error, tiebreak index) — report BOTH; grade on (a), (b) as
robustness. Effective temperature is **window-specific**: the engine ran in a prior window, so this floor is
"a demon on today's chip" for the same qubits (disclosed, not identical-window).

**Pubs (per site):** `prep0` (empty circuit + measure) and `prep1` (X + measure), 20000 shots each.
m0 = raw P(1|prep0); b̂ = raw P(0|prep1) (readout 1→0 handle, reported cross-check).

**⚠ PRE-GRADE CORRECTION (data-blind, C4663, before any counts read — job DONE but unopened; commit
stamps the blindness).** The originally-frozen estimator `p_eq = (m0−P(1|0))/(P(1|1)−P(1|0))` is
**DEGENERATE**: `prep0` *is* the m0 measurement, so its "P(1|0)" is not independently measurable, and
`prep0`+`prep1` alone cannot separate thermal excitation `p_eq` from readout 0→1 rate `a` without an
external asymmetric-readout handle (the campaign self-audit rule firing at grading-design, as Fannes did at
C4662). Corrected to a **conservative bracket** using the backend-reported assignment error `a_max` as a
disclosed upper bound on the 0→1 false-excitation rate:

  `p_eq_lower = max(0, m0 − a_max)` → `floor_lower = ln2/ln((1−p_eq_lower)/p_eq_lower)`  (conservative for PASS)
  `p_eq_upper = m0`                → `floor_upper = ln2/ln((1−m0)/m0)`                    (generous, for FAIL)

`a_max` = `backend.target["measure"][(q,)].error` (q=4: 0.00732; q=98: 0.00220, from the frozen scan).
SE(p_eq)=sqrt(m0(1−m0)/N); a_max held as a fixed backend constant (its uncertainty absorbed by using the
point value as a hard subtraction). This makes the bias direction **correct**: the lower bracket under-states
the floor, so a PASS on floor_lower is robust-despite-readout; the upper bracket over-states it, so a FAIL on
floor_upper is robust-despite-thermal. A straddle = thermometry insufficient at 5σ.

**Stage-1 sanity gate:** m0 finite ∈ (0, 0.20), a_max < m0 (else p_eq_lower pinned at 0 → PASS impossible,
reported as such). Else ABORT.

## Grade (frozen)

- **floor SE by propagation:** `SE(floor) ≈ ln2 / (L²·p(1−p)) · SE(p_eq)`, L = ln((1−p)/p), evaluated at
  each bracket endpoint. `SE_comb = sqrt(SE(floor)² + SE(W_credit)²)`, SE(W_credit)=0.0098.
- **G1 (HEADLINE, two-sided, on the bracket):**
  **PASS ("the demon pays its bill")** iff `floor_lower − W_credit − 5·SE_comb(lower) > 0` — even a
  thermodynamically perfect demon erasing at the Landauer minimum cannot profit; the thermo-arc books close
  at the floor, and it holds even after generously blaming readout for the excitation.
  **FAIL ("the floor doesn't close it")** iff `W_credit − floor_upper − 5·SE_comb(upper) > 0` — even the most
  demon-favourable thermometry puts the Landauer minimum below the earnings; closure would rest on the actual
  super-Landauer irreversibility of physical reset OR the H2 coherent-record loophole (Exp125b).
  **STRADDLE → REFUTED magnitude subclaim** (F93/F95 "huge-vs-zero but misses-its-5σ" pattern): the floor
  bracket brackets the credit, so computational-basis thermometry is insufficient to certify direction at 5σ.
  Recorded as a loss, not softened — and itself the honest finding (the books cannot be closed at the floor
  with this instrument; that is information).

## Power calc at freeze (advisor point 4 — the W1-miss lesson, c4130_001)

Near p_eq ≈ 0.015: dfloor/dp_eq ≈ 2.68 E/unit → `SE(floor) ≈ 2.68·SE(p_eq)`. At 20000 shots,
SE(p_eq) ≈ sqrt(p_eq(1−p_eq)/N + readout-cal variance) ≈ 0.003–0.004 → SE(floor) ≈ 0.008–0.011 →
`SE_comb ≈ 0.013–0.015` → `5·SE_comb ≈ 0.065–0.075`. Expected gap `floor(0.015)−W_credit ≈ 0.166−0.092 =
0.074`. **The gap is at the edge of 5σ resolvability** — a REFUTED-straddle is a live outcome and is
pre-accepted as a finding. Readout-cal variance dominates → 20000 shots on `prep0` is the budget that keeps
SE(p_eq) small; not raised further because a bigger N cannot shrink the *systematic* SPAM residual.

## Predictions (Whisper C4663)

| Pre-filed | Conf | |
|---|---|---|
| Stage-1 estimator sane (p_eq ∈ (0,0.2), M well-conditioned) | 0.95 | |
| p_eq (engine qubit) ∈ [0.008, 0.035] | 0.70 | representative Heron-r2 effective temp |
| **G1 headline = PASS** (floor > credit at 5σ) | **0.55** | gap ~0.074 at edge of 5σ; straddle is live |
| Site (a) and (b) agree in verdict | 0.75 | |

Cost: one job, ~2–4s QPU (two 20k-shot calib pubs × 2 sites). QPU verified 🟢 (9868/10800 s, C4663).
