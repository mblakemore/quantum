# F113 — Exp127-HW "The Shallow-Circuit Solver Runs on Silicon": a CONSTANT-DEPTH quantum circuit solves the 2D Hidden Linear Function problem on real hardware at 90.2% (438σ over the random floor), covering the whole solution coset near-uniformly — the campaign's FIRST computational-genre on-silicon result, tied to the one depth-separation theorem (Bravyi–Gosset–König) that needs no hardness conjecture, honesty-fenced

**Finding**: F113 (assigned Ember C4156 per the network numbering role split; design + sim +
pre-registration + submission + grading Whisper C4673/C4674, on substrate **claude-opus-4-8**, under
the frozen rule. **This is the finding whose number was DEFERRED TO SILICON at C4154** — the C4155
numbering determination ruled the sim-tier groundwork (Exp127 sim) was docs/bridge tier and that the
F-number would be *earned the moment the frozen instance flew on hardware*. It flew, all gates passed;
the number is earned. F113 verified unused — F112 was the highest prior.)
**Experiment**: Exp127-HW (ibm_marrakesh, job `d9amnlvu62qs738o8nt0`, chain [0,1,2,3]; the frozen n=4
2D-HLF instance from the C4673 sim, on real silicon; 10 routed CZ, depth 23). Grader frozen with the
prereg; the valid-z solution set recomputed in-artifact = the circuit's Gauss-sum support.
**Pre-registration / groundwork**: `experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md` (the
sim-tier apparatus + O(1) depth ledger + NISQ-viability that this hardware flight cashes in).

## Plain English — a shallow quantum circuit solves a problem shallow classical circuits provably can't

There is exactly **one** proven quantum-advantage result that needs *no* unproven hardness assumption
and lives at the shallow depths today's chips can actually run: **Bravyi–Gosset–König (Science 2018)**.
It concerns the **2D Hidden Linear Function** problem, and it proves that a **constant-depth** quantum
circuit (depth that does *not* grow as the problem gets bigger) solves it *with certainty*, while **any
classical circuit built from bounded-fan-in gates needs depth growing like log n** — a genuine
separation in *computational* power measured by circuit depth, proven, not conjectured. Every other
advantage the campaign won is a *game* or a *channel* or a *sensor*; this is the **computation**
scoreboard — the one it had **not** won (F54 measured the *wall*: the deep circuits a Grover-style
speedup needs are past this hardware's coherence). F113 runs the shallow BGK solver on real silicon: it
finds a valid solution **90.2% of the time** (a random guess would be right 25%), and — the part a
cheater can't fake — it returns **all four** valid solutions **about equally often** (~22–23% each),
covering the whole solution set the way the real quantum algorithm must. A trivial classical mimic that
just outputs one fixed valid answer would ace "is it valid?" but **fail** the coverage test.

## One-line result — SOLVER-ON-SILICON, all four gates PASS

**P(valid z) = 0.9017 ± 0.0015 = 437.8σ** above the uniform-random floor (0.25), at **constant circuit
depth** (10 routed CZ, hardware depth 23). The solver **covers the entire solution coset
near-uniformly** — all four valid z at **0.2237 / 0.2229 / 0.2308 / 0.2243** (min 0.2229) — the
quantum-natural property no output-one-fixed-z classical mimic can reproduce. Pre-filed hardware band
[0.82, 0.93] **HIT at the top**.

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| W1_SOLVER | P(valid z) > uniform floor 0.25 + 5σ (beats chance on silicon) | 0.9017, **437.8σ** | **PASS** |
| W2_MAJORITY | P(valid z) > 0.5 + 5σ (a majority of shots solve it) | 0.9017 (≫ 0.5 + 5σ) | **PASS** |
| W3_COVERAGE | all four valid z sampled > 0.08 each (covers the whole coset — a fixed-z mimic fails) | min 0.2229 | **PASS** |
| G_SENT | sentinels ≥ 0.95 | 0.985 / 0.957 | **PASS** |

## The finding — the campaign's first computational-genre result, and the contextuality that powers it

- **The one scoreboard not yet won, now on the board.** The campaign certified advantage on games
  (F106), communication (F87/F107), sensing (F108/F109), and thermodynamics (F94/F95/F97) — but the
  *computational* genre was open, walled by depth (F54). F113 lands it in the **only genre-honest way
  available at NISQ depth**: not a raw speedup (that needs the deep circuits F54 showed we can't run),
  but the **shallow-circuit depth separation** — the BGK theorem's constant-depth solver, executed.
- **The hardness is contextuality-flavored, and theory-associated with a resource the campaign
  certified.** BGKT-2020 proves the separation *survives noise* via a construction that plays the
  **magic-square game** — the exact 8/9 Peres–Mermin game **F106 certified at 196σ**. But that gadget is
  BGKT-2020's, a *different* circuit family; the solver flown here is the plain **BGK-2018** circuit, and
  F106 certified the game in a *separate* experiment. So the link is **contextuality → computational
  separation in theory** — an association argued, not composed on one chip: the through-line the C4666
  groundwork promised, argued by theorem, **not** closed end-to-end on silicon (see audit C4715 below).
- **Coverage is the load-bearing gate.** Beating the floor (W1) or a majority (W2) could in principle be
  gamed by a classifier that memorizes valid strings; the **full-coset coverage (W3)** is the signature
  a genuine quantum solver produces and a shortcut does not — the "law the rate can't fake," the
  F98/F101/F108 discriminator lineage applied to a computational output.

## What this does and does not show (scope — the honesty fence, held explicitly)

**This does NOT prove QNC⁰ ≠ NC⁰ on-chip.** The BGK/BGKT separation is **asymptotic** (a statement
about families of circuits as n → ∞); a single n=4 instance cannot prove an asymptotic class
separation, and no such claim is made. **The certified claim is exactly**: a *constant-depth* quantum
circuit solves the 2D-HLF instance on real silicon at **90.2% / 438σ over the random floor, covering the
full solution coset, at O(1) depth** — the verified hardware apparatus of the theorem, with the
theorem carrying the asymptotics. It is the **honest complement to F54**: F54 measured the wall that
blocks *deep-circuit* speedups; F113 shows the *shallow-circuit* separation's solver runs cleanly right
where the wall isn't. Device-characterized; single instance; the O(1)-depth ledger (CZ-layers plateau
at 4 across n=4..16) lives in the C4673 sim groundwork, not re-flown here.

## Lineage and reuse — and a numbering-discipline note

- **Arc**: computational genre (new) — the first on-silicon computational-genre result, tied to
  Bravyi–Gosset–König (2018) / BGKT (2020), completing the advantage-genre set (games F106 · storage
  F107 · metrology F108 · **computation F113**). Complements **F54** (the measured deep-circuit wall);
  rests on **F106** (the contextuality that is the classical hardness).
- **Numbering discipline (the C4154/C4155 rule, validated)**: the sim tier was ruled **not** an
  F-number (docs/bridge tier) and the number **deferred to silicon**; the hardware flight earned it.
  This is the *hardware-anchored-vs-sim-only* discriminator working as designed — the number tracks a
  job ID, and the deferral kept the milestone crisp (the first computational-genre F is a *hardware*
  first, not a sim first).
- **Method reuse**: the **coverage gate** (certify the whole solution set is covered, not just that
  outputs are valid — a fixed-output mimic fails coverage); recompute-the-solution-set-in-artifact
  (= the circuit's Gauss-sum support, the Exp126 house standard, which caught the Z₄-polarization bug
  at sim tier); honesty-fence-stated-first (certify the finite-instance apparatus, let the theorem carry
  the asymptotics — do not inflate a single instance into a class separation).
- **Status-ledger claim type**: **existence** (a constant-depth quantum circuit solves 2D-HLF on
  silicon at 438σ over the random floor, full-coset-covering, at O(1) depth — the first computational-
  genre on-chip result). Figures of merit: **P_valid 0.9017 / 437.8σ** and **full-coset coverage**
  (min 0.2229). Subclaim: **contextuality-is-the-hardness** (CONFIRMED-by-composition — the BGKT
  hardness construction plays the F106 magic-square game the campaign certified at 196σ). HW tier;
  single instance; UNTESTED (a larger-n ladder or a second device would be the follow-up).

---

## Adversarial audit caveat (Whisper C4715, `docs/findings/adversarial-audit-F113-computational-bridge-whisper-c4715.md`)

Creator-directed adversarial run. VERDICT: **apparatus is real, advantage is theorem-carried, not
run-carried at n=4.** The scope fence above is *correct and credited*. But: (1) **no empirical gate
benchmarks the theorem's actual competitor** — W1's 438σ is over *random guessing* (0.25), W3 coverage
defeats only a *fixed-output mimic*; the real classical competitor (a constant-depth / poly-time
classical circuit) clears both trivially at n=4 (2D-HLF ∈ P; the Ω(log n) bound is asymptotic and does
not bind at n=4). So the σ correctly measures *beats-chance-on-silicon*, not *beats-classical*.
(2) The plain-English hook "solves a problem shallow classical circuits **provably can't**" is literally
false at n=4 and contradicts this section's own fence — the "as n grows" qualifier is load-bearing.
(3) The **contextuality-is-the-hardness** subclaim is **overstated**: the circuit flown is the plain
**BGK-2018** Clifford solver (`H·CZ·S·H`), not the **BGKT-2020** magic-square construction the F106 link
names, so "CONFIRMED-by-composition / closed end-to-end" → downgrade to **theory-associated** (real
association, not a demonstrated on-chip composition). Suggested fix: add a "compared-to-what?" row to the
grade table stating the classical NC⁰-vs-QNC⁰ competitor at n=4. The WIN stands as an apparatus
milestone; it is NOT downgraded to "just random-beating" (that would be the inverse over-claim).
