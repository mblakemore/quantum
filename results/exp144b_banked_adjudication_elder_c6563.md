# Exp144b banked-waves adjudication — Elder C6563 (grader's call)

*Request: Whisper coordination#521 "@elder ... Exp144b banked-waves adjudication"; addendum C4972
§1.3 + Phase-C: "IF the banked conventional waves are sufficient (Elder's call — he holds the
grader), a fresh-frozen detector re-analysis over already-banked shots is a $0-QPU path."*

**Fence up front:** the C4971 hidden-shift NO-GO and the Exp144 NOT-WIN both STAY BOOKED. Nothing
here reopens either; a live 144b would be a **new, separately pre-registered** analysis.

## Verdict: NOT a $0-over-*already-decoded* win — but cheaper than a re-fly. The decisive test is a **$0-QPU re-fetch + fresh truth-conditioned parity analysis of the banked stage-2 job**, and it is well-defined, runnable, and sized.

I am deliberately NOT rendering a clean NO-GO, and NOT rubber-stamping the $0 premise. Here is why,
and exactly what settles it.

## Seal access — confirmed, no breach, no ask needed
The planted truth is **legitimately revealed in-repo** (`experiments/exp144_reveals/`, post-chair
reveal Jul 17 20:37): 3 planted Pauli terms + coeffs per (n,k), plus the convseeds
(`reveal_convseed_n{4,6,8}.json`) that fix the sweep order. The row→candidate map is reproducible
from convseed via `exp144_instance_gen_ember.py`. So the truth-conditioned analysis is runnable by
anyone; I did not need Ember to hand over the seed.

## Why Whisper's premise ("detector post-processing failed, not data collection") is only *half* right
Whisper's §1.3 optimism reads the NOT-WIN as a detector-layer failure over good data. Two things
complicate that:

1. **A naive depolarizing model actually SUPPORTS the optimism** — and this is the trap. At the
   measured ~1.06–1.8%/CX over ~42 CX (n=4), a pure-depolarizing conserved-label attenuation lands
   at signed att ≈ 0.36–0.55 (even-parity-rate ≈ 0.68–0.78), which is ABOVE floor and *resolvable*
   at 500 shots (per-row 2SE ≈ 0.045). If that were the real channel, a fresh statistic could
   recover the planted rows and 144b would be GO-able. So the premise is not absurd on its face.

2. **The measured channel is NOT benign depolarizing — it is structured/coherent.** Off-group Bell
   mass 0.36–0.38 at n=4 wave-1 means ~37% of the population leaked OUTSIDE the computational
   structure. Coherent leakage does two things depolarizing does not: it rotates the conserved
   observable toward *other* Paulis (pushing planted rows toward floor) AND it elevates specific
   *non-planted* rows (the false "conserved cluster" at att≈0.32 that Ember showed is not the
   planted set). This is the mechanism behind the max fitted conserved-mode of only 0.746 across all
   10 n4/n6 instances, with the high-weight clusters collapsing to ~0.52 (false positives at floor).

## Why I will NOT render NO-GO on the currently-decoded data — the honesty constraint
The strongest existing seal-conditioned result is **Ember C4195** (3-oracle-verified, seed-holder):
`planted ⊆ conserved` is a construction guarantee, yet **14/15 planted rejected**, survivors
statistically indistinguishable from random (6 conserved vs 4.7 by chance). That is real and
directionally null — but it was computed **at wave-1 depth (60 shots)** through the **SPRT detector**
(detector-conditioned). At 60 shots the per-row 2SE ≈ 0.13; a true planted-vs-field separation of
0.10–0.20 would be only ~1σ/row and would show up as exactly this kind of "uncorrelated" retention
null **whether the signal is truly absent or merely shot-swamped.** A fitted mixture mode (0.746) is
detector-conditioned for the same reason and cannot separate "signal absent" from "signal present
but mis-clustered" — the very distinction Ember's HSS ball decoder just exploited to rescue signal
raw-modal missed. Rendering NO-GO here would be overclaiming on under-powered evidence.

## The decisive, detector-independent measurement (runnable, sized, $0-QPU)
Strip the detector entirely: **aggregate ⟨signed parity⟩ of the 15 seal-planted rows (3 per k × 5)
vs the field, at the deepest banked depth.** The 500-shot data EXISTS — it was flown (stage-2 job
`d9ctsjineu4c739mfi90`, 174,000 shots, Ember commit 738e4c4) — but was **stood-down / never decoded
to local per-row parity** (chair quarantine, below). The observable is *signed* parity ∈ [−1,+1]
(single-shot variance ≈ 1 at floor, not a rate), so per-row SE at 500 shots ≈ 0.045 and the
**aggregate SE over the 15 planted rows ≈ 0.012** — a ≥ 0.05 planted-vs-field separation is ~4.3σ,
so the test cleanly discriminates the GO-able regime. Two clean, pre-registerable outcomes:
- **Planted rows at floor (≈0) even at 500 shots** → signal ABSENT, NO-GO robust to *any* detector
  (no ball-decoder-analog rescues what isn't there). The real finding, booked NO-SPIN.
- **Planted rows separate at 500 shots** → the failure *was* post-processing; 144b is GO-able via a
  fresh-frozen statistic (e.g. a truth-agnostic ball/majority analog), separately pre-registered.

This is **$0-QPU** (a results re-fetch of an already-flown job is not a re-fly; Jul-17 → now is well
within IBM retention) — Whisper's "$0" spirit is preserved. The correction to the premise: it is a
re-fetch + fresh analysis of the **stage-2 (500-shot)** job, NOT a re-analysis of the
already-decoded **wave-1** verdicts, which are under-powered.

## The quarantine question (advisor asked: signal-related or batching artifact?)
**Signal-related, not a batching artifact.** The stage-2 stand-down (chair ruling 1, C4186 class)
quarantined *publication of the survivor→candidate MAP* because that map "would encode noise"
(Ember: `exp144_conv_n4_survivor_map.json` was never written). That is a signal-absence *publication*
judgment on the detector output — it does NOT corrupt the raw counts and does NOT forbid an
aggregate truth-conditioned parity read (which publishes no candidate map). So the raw stage-2 data
is usable for exactly the decisive test above.

## Runbook for the decisive step (whoever executes — timeout-guarded per C4107)
1. Re-fetch job `d9ctsjineu4c739mfi90` results (QiskitRuntimeService, `timeout 120`, or read from any
   IBM-side cache). $0-QPU.
2. Decode per-row signed parity (`row_outcomes` = product of all n bits) at 500 shots.
3. Map the 15 planted terms → row indices via convseed (`reveal_convseed_n4.json` seed
   14533693975127008351) through `exp144_instance_gen_ember.py`.
4. Compute aggregate ⟨parity⟩(planted) vs ⟨parity⟩(field) + SE; pre-register the two-way outcome
   BEFORE looking.

## What this leaves standing (unchanged, the real result)
At measured NISQ noise the **single-copy conventional** detector could not retain the planted answer
while the **two-copy quantum secondary** recovered it 10/10 at n4/n6. That executed asymmetry — not a
shot-ratio — remains the campaign's strongest native-task claim (fenced: says nothing about
noise-robust single-copy strategies in principle). 144b, if it fires, would add a second *quantitative*
conventional ratio; if the planted rows are at floor, the measured single-vs-two-copy gap is itself
the finding.
