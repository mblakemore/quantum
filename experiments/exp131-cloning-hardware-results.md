# Exp131 Hardware Results — THE REPLICATOR'S LEGAL LIMIT: Cloning Ceiling Certified

**Author**: Whisper (DC15W), C4670 (2026-07-13) · **Substrate**: claude-opus-4-8
**Job**: `d9alv77u62qs738o7s40`, `ibm_marrakesh`, line [2,1,3], 14 pubs, 112k shots, one window
**Prereg**: `exp131-cloning-preregistration.md` (frozen before submission)
**Verdict**: **CLONING-CEILING-CERTIFIED — all five frozen gates PASS**

## Headline

| Gate | Frozen condition | Measured | Verdict |
|---|---|---|---|
| **W1_UNIVERSAL** | optimal cloner flat across bases, doesn't exceed 5/6 | spread **0.0218** (<0.05), max 0.8265 ≤ 5/6+5·SE | **PASS** |
| **W2_NO_UNIVERSAL_BEAT** | cheat can't beat 5/6 on all bases | cheat min = **0.4995** ≪ 5/6 | **PASS** |
| **W3_CHEAT_TELL** | basis-reading signature separates cheat from optimal | cheat spread **0.4917** vs optimal **0.0218** | **PASS** |
| **W4_CEILING_PROXIMITY** | optimal is a real ~5/6 cloner, not noise-garbage | mean **0.8144** > 0.7733 | **PASS** |
| G_SENT | sentinels ≥ 0.95 | 0.991 / 0.973 | PASS |

## The two cloners, side by side

| Input basis | Optimal cloner | Cheat (CX copy) |
|---|---|---|
| Z (|0⟩,|1⟩) | 0.8265 | **0.9911** |
| X (|+⟩,|−⟩) | 0.8047 | 0.4995 |
| Y (|+i⟩,|−i⟩) | 0.8121 | 0.5054 |
| **spread** | **0.0218** (flat) | **0.4917** (basis-locked) |
| **mean** | **0.8144** (5/6 = 0.8333, −0.019 noise) | 0.6653 |

The optimal universal cloner sits **flat within 0.022 across all three bases**, a hair below the
5/6 ceiling (the 0.019 gap is the 11-CZ noise budget — it never *exceeds* the ceiling, which
would signal basis-reading). The cheat does the opposite: it **beats 5/6 on the Z basis it was
built for (0.9911)** but pays for it, cratering to ≈0.50 on the two conjugate bases. Its
minimum over bases (0.4995) is far below the ceiling — **no strategy beats 5/6 universally**,
which is the no-cloning theorem's quantitative teeth. The cheat's basis-dependence (0.49) vs
the optimal's (0.02) is the detector: **the way to beat the ceiling somewhere is exactly the
way to get caught.**

## What this certifies (scope)

- The exact **quantitative ceiling** the no-cloning theorem licenses (5/6 per copy, universal),
  and its enforcement — beating it on one basis is provably paid back on the conjugate.
- NOT an advantage (a limit is *hit*, nothing is beaten); NOT a no-cloning "proof" (that's a
  theorem). The cloner circuit's ancilla-prep angles were **numerically optimized and verified
  in-artifact** (noiseless mean 0.83332, cross-state variance 2.2×10⁻⁸), not taken from memory.
  UQCM is textbook (Bužek-Hillery 1996); the contribution is the frozen-court,
  executed-cheat-arm, universality-flatness certification.
- Adds **no-cloning** to the certified-limits ledger. The campaign now certifies both what
  quantum resources can exceed (the advantage arc — games/comms/metrology) and what they
  cannot (this). The cheat-arm-pre-registered-to-fail is the informative-null discipline
  weaponized into a detector.

## Bookkeeping

Noiseless design check PASS. Lint 5/5. Audit: optimal arm 11 CZ (5 logical + heavy-hex routing
of the unavoidable prep-triangle edge), cheat arm exactly 1 CZ, 14/14 pubs. All four pre-filed
predictions HIT (W4 flagged at-risk at 11 CZ — passed with 0.041 margin). Results:
`results/exp131_hw_results.json`.
