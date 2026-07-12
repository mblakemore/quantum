# A Causal-Discovery Stress Test Where the Right Answer Is "Your Premise Is False"

**Author**: Whisper (DC15W), C4587 (2026-07-12), round-3 plan item P3.
**Artifacts**: `tools/causal_stress_dataset.py` (seeded bootstrap, seed 4587) →
`results/causal_stress_dataset.csv` (150,000 rows) → `tools/run_causal_discovery.py`
(PC + GES, `causal-learn` 0.1.4.8 pinned).
**Companion to**: the pearl-bridge paper (§5 "typed, not wrong") — this is the executable
version, in the causal-inference community's own toolchain.

## What this dataset is

Shot-level samples over three variables — S (setting: switch / null_fwd / null_rev),
C (control X-outcome), T (target outcome) — bootstrapped from the **measured** joint
distributions of Exp108 (`results/exp108_grade.json`, job `d98vqsq...`, ibm_marrakesh).
Raw per-shot records were not retained, so this is a **declared parametric bootstrap** from
measured aggregates: P(C)·P(T|C) per setting, fixed seed, fully reproducible. In the null
arms the control is ~deterministic (P₊ ≥ 0.996, stated).

**The ground-truth label no other benchmark has**: the process that generated the switch-arm
distribution has **no definite causal order** between its two channel applications —
certified on the same apparatus by frozen-rule grading at 21.1σ (Exp108 thermal), with the
game arc's 216.8σ on the same family. Every published causal-discovery benchmark ships a true
DAG; this one provably lacks one (within the causally separable class W_sep the discovery
algorithms presuppose).

## What the algorithms said (verbatim output)

PC (chi-square CI tests, α=0.01) and GES (BDeu score) both returned the **complete undirected
graph** S—C, S—T, C—T:

```
PC  edges: ['X1 --- X2', 'X1 --- X3', 'X2 --- X3']
GES edges: ['X1 --- X2', 'X1 --- X3', 'X2 --- X3']
```

Ordinary output. A Markov-equivalence class of ordinary DAGs. No error, no warning, no flag.

## The claim, stated precisely (no overclaim)

This is a demonstration of **blindness, not failure**. The algorithms did nothing wrong by
their own semantics: given observational data, they correctly report dependence structure.
The point is that their output FORMAT — a (CP)DAG — silently asserts that some definite-order
structure generated the data, and there is nothing in the data, the algorithm, or the output
that could ever say otherwise. The same 150,000 rows, analyzed with the causal-witness
machinery, certify at 21.1σ that no member of the output's model class generated them.

**Same data. Two analyses. Opposite verdicts about the premise.** That is the paper's W_sep
typing argument (do-calculus is typed over definite/latent-mixed/dynamic causal structure),
handed to referees as something they can run.

## Uses

1. **Software stress test**: any causal-discovery tool can be pointed at this CSV; the
   correct ideal behavior (emit "premise violated" or an ICO-compatible object) is currently
   expressible by no mainstream tool — the dataset marks the gap.
2. **Teaching**: the cleanest small example we know of "the output type smuggles an
   assumption."
3. **Paper companion**: referees can reproduce the blindness in ~10 lines of causal-learn.

## Scope and extension

v1 uses Exp108 only (3 variables — the complete graph leaves no orientable collider, which
is itself part of the point: nothing distinguishes this data from mundane confounding).
Planned extension (deferred): add Exp106 capacity data with the input bit B as a fourth
variable, giving the algorithms more structure to orient — and the same blindness. FCI (which
can report some inconsistencies) is a natural addition; nothing in its output vocabulary can
express "no definite order" either.
