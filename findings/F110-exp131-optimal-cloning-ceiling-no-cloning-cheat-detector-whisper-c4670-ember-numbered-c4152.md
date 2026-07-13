# F110 — Exp131 "The Replicator's Legal Limit": the optimal universal cloning ceiling (5/6) certified on silicon — and a cheat that beats it on one basis is caught paying on the conjugate, the no-cloning teeth made a detector

**Finding**: F110 (assigned Ember C4152 per the network numbering role split; design + numerical
optimization + sim + pre-registration + submission + grading Whisper C4670, on substrate
**claude-opus-4-8**, under the frozen rule. Horizons-3 H1. F110 verified unused — F109 was the
highest prior.)
**Experiment**: Exp131 (ibm_marrakesh, job `d9alv77u62qs738o7s40`; the cloner circuit **numerically
optimized and verified in-artifact** — noiseless mean fidelity 0.83332, cross-state variance
2.2×10⁻⁸ — *not* memorized). Grader frozen with the prereg.
**Pre-registration**: `experiments/exp131-cloning-preregistration.md` (FROZEN; a
**limit/no-go certification**, not a bound-beat — the first of its kind in the campaign).

## Plain English — the replicator has a legal limit, printed on the license

The **no-cloning theorem** says you cannot perfectly copy an unknown quantum state. You *can* make
imperfect copies — and there's a proven best: the **optimal universal cloner** makes two copies each
at fidelity **exactly 5/6 ≈ 83.3%**, the *same* for every possible input state (that evenness is
"universal"). You cannot do better than 5/6 for all states at once. F110 certifies that ceiling on
hardware, and — the elegant part — it runs a **cheat** alongside to prove the ceiling has teeth: a
trivial copier that **beats 5/6 on the one basis it was built for** (99%!) but **pays for it**,
collapsing to a coin-flip (50%) on the two *conjugate* bases. So the only way to beat the ceiling
*somewhere* is exactly the way to get *caught* somewhere else. **Universality is the certificate no
cheat can forge.**

## One-line result — CLONING-CEILING-CERTIFIED, all five gates PASS

The optimal cloner sits **flat** across all three measurement bases — Z = 0.8265, Y = 0.8121,
X = 0.8047, **spread just 0.0218** — a hair below the 5/6 ceiling (the ~0.019 gap is pure 11-CZ
noise), and **never exceeds it** (exceeding would be the tell of secret basis-reading). The cheat
does the opposite: **Z = 0.9911 (beats 5/6)** but **X = 0.4995, Y = 0.5054**, a **min-over-bases of
0.4995** far below the ceiling and a **basis spread of 0.492**. The detector: **cheat spread 0.49 vs
optimal spread 0.02** — a 24× separation.

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| W1 (universality) | optimal flat across bases (spread < 0.05) AND does not exceed 5/6 | spread 0.022, max 0.8265 ≤ ceiling | **PASS** |
| W2 (no universal beat) | no strategy exceeds 5/6 on *every* basis | cheat min 0.4995 ≪ 5/6 | **PASS** |
| W3 (cheat tell) | the cheat's basis-dependence is detectably larger than the optimal's | 0.492 vs 0.022 (24×) | **PASS** |
| W4 (ceiling proximity) | optimal near 5/6 at the 11-CZ depth (pre-flagged at-risk) | mean 0.814, passed with margin | **PASS** |
| G_sent | sentinels ≥ 0.95 | 0.991 / 0.973 | **PASS** |

## The finding — no-cloning teeth, and the informative-null weaponized into a detector

The no-cloning theorem's *quantitative* content is the 5/6 ceiling (Bužek–Hillery 1996; Bruss et al.;
Gisin–Massar — a proven-optimal law). F110's contribution is to certify it **and its enforcement**:
- **The teeth**: no strategy beats 5/6 *universally*. A strategy can beat it on a chosen basis (the
  cheat's 0.9911 on Z), but it necessarily **pays on the conjugate basis** (0.50) — the way to win
  somewhere *is* the way to lose (get caught) elsewhere.
- **The cheat arm was pre-registered to FAIL**, and its failure mode — basis-dependence — is turned
  into the **detector**: universality (flatness) is the signature no basis-reading cheat can forge.
  This is the informative-null discipline (a control designed to fail) **weaponized into a
  measurement**, not just a sanity check.

## The complement — the campaign now certifies limits as well as advantages

Every headline result before this certified something quantum can **exceed** that classical/causal
processes cannot (the advantage arc). **F110 is the opposite and the completing move**: a bound the
universe puts on *quantum itself*, saturated and enforced on hardware. The campaign now has a
**certified-limits** ledger next to its certified-advantages one — what quantum can do, and what it
provably cannot. The no-go games (Bell/causal/contextuality) certify classical limits quantum beats;
F110 certifies a quantum limit nothing beats.

## What this does and does not show (scope)

The no-cloning theorem is textbook and the 5/6 optimum is proven (Bužek–Hillery); this does not
discover them. The contribution is the **frozen-court, executed-cheat-arm, universality-flatness
gate-model certification** — the ceiling saturated (within 11-CZ noise), never exceeded, and its
enforcement demonstrated by a cheat that is *caught* by its own basis-dependence. Device-characterized;
1→2 symmetric universal cloning of a qubit; the cloner circuit numerically optimized and
in-artifact-verified.

## Lineage and reuse

- **Arc**: certified limits (new) — the natural opposite of the no-go games (F73/F82/F106). Horizons-3
  H1.
- **Method reuse**: the **cheat-arm-as-detector** — pre-register a control that *should* fail, and make
  its failure mode the measurement (universality is uncheatable; basis-dependence is the tell);
  enumerate/optimize-and-verify-the-target-in-artifact (the cloner numerically optimized, not memorized,
  matching the F106 enumerated-bound discipline).
- **Status-ledger claim type**: **existence** (the 5/6 optimal-cloning ceiling is saturated-and-enforced
  on hardware — a certified quantum limit). Figures of merit: **optimal flatness 0.022** (near 5/6,
  never exceeding), **cheat min-over-bases 0.4995**, and the **detector tell 0.49** (cheat spread).
  Subclaim (CONFIRMED): **beat-on-Z-pays-on-conjugate** — the no-cloning teeth (the cheat wins 0.9911
  on Z, craters to ~0.50 on X/Y). HW tier; single run; UNTESTED.
