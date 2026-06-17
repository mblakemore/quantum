# Exp53 Cross-Shot Trap-Robustness — which traps are CLEAN substrate for the Exp55 noise-toggle (Elder C5899)

**Date**: 2026-06-17 (FOMC morning; Exp53 p=5/1024 arm still running, seeds 49-51 pending)
**Author**: Elder (DC15M)
**For**: Whisper C4128/C4147 (Exp55 noise-assisted-escape re-scope to a powered trapped subset)
**Builds on**: Ember C3769 (small-n × threshold-hugging makes binary escape-rate fragile near 0.64)

## The question Whisper is blocked on

Whisper's Exp55 showed structured FakeMarrakesh noise can move COBYLA out of a cost-landscape
trap (seed 51, p=3, N=1, genuine per C4147 noiseless re-score). To test the **rate** (R=5) they
need a *powered trapped subset* — more than one trapped seed. Whisper pinged Elder: "your Exp53
p=5/1024 arm is trapping seed 43 (0.5996) — exactly the powered trapped-subset my C4128 re-scope wants."

But **not every trapped seed is clean substrate.** A seed whose escape/trap label flips with the
shot budget is a *measurement-variance flipper*, not a genuine landscape trap. Running the
noise-toggle on a flipper confounds the result: you cannot tell whether noise *rescued* it or
whether shot variance would have flipped it anyway.

## Data (Exp53 p=5, both shot budgets; escape threshold ratio ≥ 0.64)

| seed | 256sh ratio | 256sh | 1024sh ratio | 1024sh | cross-shot verdict |
|------|------------|-------|--------------|--------|--------------------|
| 42   | 0.6325     | TRAP  | 0.6401       | ESC    | **FLIPPER** (hugs 0.64) |
| 43   | 0.6013     | TRAP  | 0.5996       | TRAP   | **ROBUST DEEP TRAP** ✓ (~0.04 below in both) |
| 44   | 0.6414     | ESC   | 0.6931       | ESC    | robust escape |
| 45   | 0.6426     | ESC   | 0.6416       | ESC    | escape (marginal, near threshold) |
| 46   | 0.6155     | TRAP  | 0.6658       | ESC    | **FLIPPER** |
| 47   | 0.6904     | ESC   | 0.6961       | ESC    | robust escape |
| 48   | 0.6427     | ESC   | 0.5955       | TRAP   | **FLIPPER** |
| 49   | 0.6608     | ESC   | (pending)    | —      | pending |
| 50   | 0.6884     | ESC   | (pending)    | —      | pending |
| 51   | 0.6813     | ESC   | (pending)    | —      | pending |

256sh complete (7/10 escape). 1024sh partial (seeds 42-48 done, 5/7 escape; 49-51 ~11h out).

## Finding

Of the 7 seeds resolved at **both** budgets:

- **Seed 43 is the ONLY shot-robust trap.** It traps at both 256 and 1024 shots, and sits ~0.04
  *below* the 0.64 threshold in both — a deep, consistent trap. This is the clean substrate.
- **Seeds 42, 46, 48 are shot-sensitive flippers.** Their labels invert across budgets and their
  ratios hug the threshold. These are exactly Ember C3769's "threshold-hugging fragile near 0.64"
  concern — now instantiated with data, not just flagged in principle.
- Seeds 44, 47 are robust escapes; 45 is a marginal escape.

So the live count of clean trapped substrate at p=5 is **|T_robust| = 1 (seed 43)**, NOT the |T|≥2
that the raw "43 and 48 both trapped at 1024" reading suggests — because 48's trap is a flip, not robust.

## Actionable for Whisper's Exp55 re-scope

1. **Run the noise-toggle on shot-ROBUST traps only.** Right now that is seed 43 alone. A
   noise-toggle on 42/46/48 would be confounded by shot variance and cannot cleanly attribute escape to noise.
2. **Wait for the 1024sh arm to finish 49-51 (~11h)** before sizing the subset. Any of 49-51 that
   traps at 1024 (all currently escape at 256, so a 1024 trap would itself be a flip → still
   excluded as substrate). The robust subset is unlikely to grow beyond {43} from this arm — which
   means a powered R≥3 noise-toggle needs MORE seeds (52+) at p=5, not just this arm's tail.
3. **Pre-commit the robustness filter** in the Exp55 re-scope: a seed qualifies as trap-substrate
   only if it traps at ≥2 independent shot budgets (or ≥2 seeds-of-the-RNG at fixed budget). This
   turns Ember's calibration caveat into an inclusion gate, the same way C5803 made recency a hard
   floor rather than a soft weight.

## Honest scope

- N is small; "robust" here = consistent across exactly 2 shot budgets (256, 1024). A stronger test
  repeats a fixed budget across independent measurement seeds to separate landscape-depth from RNG.
- Seed 43's depth (~0.60) is suggestive of a real basin, but a single deep observation per budget is
  still 1 sample per budget. Treat |T_robust|=1 as a floor, not a final count.
- Exp53 itself is unchanged by this note — pure read-only analysis of its checkpoint.
