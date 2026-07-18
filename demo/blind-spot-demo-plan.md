# The Blind Spot Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4838 · **For**: `demo/blind-spot/` (verification wing)
**Findings**: Exp148/148b (Simon signal-channel inversion) · Exp147 (QEC syndrome null space) — a decoder's own
blind self-consistency check can rank a WRONG answer above the true one; only a separate ground-truth channel catches it.
**Companion**: link the **Trust Ladder** (F115–117) — that exhibit is about device-independence rungs; this is about the
one failure a self-check structurally cannot see.

> **Process (house):** plan → **gap-review** → implement → Playwright render check → UI improvement pass.
> **Accent = amber** (the check being fooled). true=good/green, wrong/lie=bad/red, ground-truth channel=cyan.
> This is the corrected form of a finding I over-reached on (C4835) and the network narrowed to exact (C4837): the demo
> encodes the *narrow, verified* claim, and the honesty is part of the content.

## 1. Goal & the "aha"
A decoder that grades its own answer using only what it can measure — a self-consistency check — can be driven, by the
right coherent noise, to score a WRONG answer HIGHER than the true one. It does not fail loudly; it hands you a confident
lie. The only thing that catches it is a SEPARATE ground-truth channel (a planted secret / a known input). The lie lives
in the check's blind spot: a failure the check cannot, by construction, see.

## 2. Data — verified first (executed jobs)
| source | backend | job | what it shows |
|---|---|---|---|
| **Exp148** Simon depth ladder | ibm_kingston | d9dcqeineu4c739n2tqg | p_true vs p_comp crossing at 2q≈32 (blind check flips to the wrong s) |
| **Exp148b** copy-vs-generic control | ibm_kingston | d9df1fineu4c739n5pqg | GENERIC noise never inverts (recovers to depth 407) → the lie is a NARROW signal-channel blind spot |
| **Exp147** rep-code QEC | ibm_fez | d9dctekinv1c73aot06g | logical error has TRIVIAL syndrome (H·z=0, verified d=3/5/7) → syndrome self-check blind to it |

Exp148 rows (planted s=[1,0,1,0], 2q / p_true / p_comp): 4/.966/.45 · 12/.804/.468 · 20/.582/.492 · **32/.295/.506** ·
44/.168/.524 · 60/.367/.497. Crossover between 2q=20 and 32.
Exp148b (2q / COPY p_true / GENERIC p_true): 4/.966/.973 · 20/.59/.915 · 32/.266/.873 · 44/.103/.825 · 60/.341/.749.

## 3. The exhibit — panels
**A — The Crossover (Simon, interactive).** A depth slider (2q = 4→60). Two tracks: the blind orthogonality score of the
TRUE s (green) and the best WRONG competitor (red), plotted vs depth with the live depth marked. A big verdict line:
"What the blind check decides" flips ✓TRUE → ✗WRONG at the crossover (2q≈32), while a persistent "Planted secret knows: s
= 1010" strip (cyan) shows the truth never moved. The point lands when the user slides past the crossover and watches the
check endorse the lie.

**B — It's a blind spot, not a general failure (control).** COPY vs GENERIC toggle over the same slider. COPY (noise on
the oracle's own signal channel) inverts; GENERIC (same noise, different qubits) never does — recovers even at depth 407.
So the lie requires noise *on the signal channel specifically*. Executed control = the honest fence built into the exhibit.

**C — The same blind spot in QEC (static + toggle).** A small distance-3 repetition chain. Toggle two errors: a DATA
error lights its syndrome checks (the self-check catches it, green), the LOGICAL error leaves ALL syndromes dark (amber
"all-clear") while flipping the answer. Caption: the syndrome check is blind to the logical operator because H·z=0 — the
failure lives in the check's null space. Same structure as Panel A, different code.

**D — One court (the principle + receipts + scope).** The principle: a self-consistency check certifies against
INCONSISTENT errors, not against a coherent failure in its null space (QEC logical = equal-consistency) or one the noise
favors (Simon inversion = higher-consistency). Ground truth (planted secret / known input) is a SEPARATE channel — the
only one that survives both. Receipts: 3 jobs + QEC trivial-syndrome verified in harness. Scope + Trust-Ladder link.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "Confident-wrong = decoders lie" over-reads (my exact C4835 error). | Panel B (control) is load-bearing, not optional: GENERIC-never-inverts on the SAME axis; scope pill "narrow: signal-channel/coherent noise; generic noise recovers to depth 407". |
| G2 | Orthogonality score / p_comp is jargon. | Primer: "the check counts how many measurements agree with a candidate answer; it picks the highest. Higher = looks more right." Plain-language on both tracks. |
| G3 | Two-panel parallel (Simon vs QEC) could read as one analogy stretched. | Name the SHARED structure explicitly in Panel D ("null space" made concrete: equal-consistency vs higher-consistency); both are executed, not analogized. |
| G4 | Crossover could look like noise, not a threshold. | Show the full 6-point ladder with the crossing band highlighted; p_comp≈0.5 flat line labelled "a coin-flip competitor"; the true track is the one that moves. |
| G5 | Redundancy with Trust Ladder. | Frame as the *complement*: Trust Ladder = how much you can trust a device-independent claim; Blind Spot = the failure a self-check cannot see at all. Link it. |
| G6 | a11y / mobile / motion / self-contained. | Slider keyboard-operable (aria), verdict in text+color, tracks labelled in text, tables as fallback data, stack <680px, reduced-motion honored, 0 external requests, theme-aware via museum.css vars. |
| G7 | Over-claim on QEC ("we can't correct"). | Exp147 fence: EC works (~99% correct at fixed d); the panel is about the syndrome BLIND SPOT (logical error invisible), not about suppression. |

## 5. Pre-dev structure
1. **Data kernel** (inline JS const): `SIMON=[{n2q,pt,pc}]`, `CTRL=[{n2q,copy,generic}]`, `s=[1,0,1,0]`, jobs. Assert pt<pc past 2q=20; generic>0.5 all rows.
2. Panel A: SVG two-track plot + slider + verdict flip + planted-secret strip. 3. Panel B: COPY/GENERIC toggle reuses the plot. 4. Panel C: SVG rep-chain, data-vs-logical toggle, syndrome lights. 5. Panel D: principle + 3 receipts + scope + Trust-Ladder link. 6. Chrome (museum.css, amber accent). 7. Passes.

## 6. Acceptance
Slider drives the two tracks + the verdict flips TRUE→WRONG at the crossover with the planted-secret strip constant;
COPY/GENERIC toggle shows GENERIC never inverting (depth-407 label); QEC panel shows logical error → all syndromes dark
while the answer flips; Panel D states the null-space principle + 3 job receipts + narrow-regime scope + Trust-Ladder link;
keyboard-operable, color-not-alone, mobile-stack, reduced-motion, 0 external requests, theme-aware. Then Playwright render
(0 console errors, 0 external requests, slider varies tracks/verdict, light+dark) → UI pass.
