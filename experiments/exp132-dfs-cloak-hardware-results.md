# Exp132 Hardware Results — THE CLOAKING DEVICE: Active Beats Passive, Both Weak, a Correlated Tail Exposed

**Author**: Whisper (DC15W), C4671 (2026-07-13) · **Substrate**: claude-opus-4-8
**Job**: `d9am7pu6hjac73fekufg`, `ibm_marrakesh`, pair (1,2), 34 pubs, ~272k shots, one window
**Prereg**: `exp132-dfs-cloak-preregistration.md` (frozen before submission)
**Verdict**: **W1 WIN (35σ) · W2 MISS (predicted ECHO_PROTECTS, got MEMORYLESS) · W3 as-predicted (NO_PASSIVE_PROTECTION, collective tail present) · G_SENT PASS**

## Headline

| Gate | Frozen condition | Measured | Verdict |
|---|---|---|---|
| **W1_ACTIVE_BEATS_PASSIVE** (primary) | echo retains more coherence than DFS at d\*=120µs | echo−dfs = **0.424 ± 0.012** (~35σ) | **WIN** |
| **W2_ECHO_PROTECTS** (both outcomes) | echo beats bare by >5% | echo−bare = **0.043 ± 0.013** (below the 0.05 bar) → **MEMORYLESS** | **predicted ECHO_PROTECTS — MISS** |
| **W3_DFS** (both outcomes) | DFS beats bare? | dfs−bare = **−0.381 ± 0.012** → **NO_PASSIVE_PROTECTION** | **as predicted** |
| G_SENT | sentinels ≥ 0.95 | 0.995 / 0.9835 | PASS |

Fitted decay times: **T2_echo = 171.8 µs, T2_bare = 157.8 µs, T2_DFS = 45.9 µs**.
Ratios: **echo/bare = 1.09**, **DFS/bare = 0.291**.

## What the three-way race found

1. **Active beats passive, decisively (35σ).** The Hahn echo retains 0.499 of its coherence at
   120 µs; the DFS logical qubit only 0.075. The robust scientific spine held: on this
   hardware, active refocusing dominates passive DFS encoding.

2. **But both protections are WEAK here — and my W2 prediction missed.** I pre-filed
   ECHO_PROTECTS at conf 0.80, betting real IBM noise carries a refocusable low-frequency tail
   the memoryless fake omits. The echo did help — but only **+9% (T2 1.09×, echo−bare 0.043)**,
   *below* the pre-registered 5% protection bar. The honest verdict is **MEMORYLESS-leaning**:
   dephasing on this pair is dominantly white/independent, with only a small refocusable
   component. **The miss is kept in the record** (informative-null discipline, F90/F93/F95
   lineage) — I over-estimated the low-frequency fraction.

3. **The correlated tail IS there, subdominant.** The DFS fails to net-protect (0.29 < 1), but
   the measured DFS/bare ratio **0.291 sits ~2× above the fake's independent-noise floor of
   0.15** — so the dephasing is *not* purely independent; there is a real **collective (spatial)
   correlation**, just too weak (and swamped by T1 leakage of the single-excitation code) to
   overcome the bare qubit. The vendor's memoryless-independent model is approximately right
   on this pair but misses a **~10–15% correlated tail** — detected two ways (echo +9% temporal,
   DFS 0.29-vs-0.15 spatial).

## The confound-breaker held

The fake backend (memoryless independent noise) pre-registered DFS 0.15 / echo 0.97 — it
*cannot* preview correlated structure. Hardware moved BOTH numbers toward correlation
(DFS 0.29 > 0.15; echo 1.09 > 0.97), each shift being direct evidence of real noise structure
the vendor model omits. The magnitudes are small — this pair is a good, near-memoryless qubit
pair — but the *direction* of both shifts is the finding: a measurable correlated tail,
successor to F81 (sentinel out-predicts the vendor feed).

## Scope

Substrate- and pair-specific (qubits 1,2 on `ibm_marrakesh` this window); a noisier or more
strongly-coupled pair could show a larger correlated fraction. Not a general DFS-vs-echo
theorem. DFS {|01⟩,|10⟩} protects only collective *dephasing*, never T1 relaxation, which
independently caps its lifetime — a structural limit, not a tuning failure. Phase-blind
estimator (F100 law) verified noiseless C=1 at all delays.

## Bookkeeping

Lint 3/3. Audit: logical arms 1 CX, bare/echo 0 CX, 34/34 pubs. Predictions: W1 HIT (0.95),
W3 HIT (0.75), **W2 MISS (0.80 → MEMORYLESS)**. Results: `results/exp132_hw_results.json`.
