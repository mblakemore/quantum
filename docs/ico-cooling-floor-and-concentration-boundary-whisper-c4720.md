# Can ICO cooling be driven colder? The cascade floor and the classical-concentration boundary

**Author**: Whisper (DC15W), C4720 (2026-07-15), Creator-directed ("can a single destination qubit
take multiple inputs — can we drive it colder? … work it out and fly it if possible").
**Verdict, up front**: via the **ICO resource itself, no** — the cooling *saturates*. Further cooling
past that floor is **classical entropy compression** (works on any biased qubit) or **colder baths**
("start colder"), neither of which is new indefinite-causal-order physics beyond F118. The answer is
**analytic** (cascade floor computed; concentration is a classical formula). The classical
concentration was subsequently **flown at Creator direction as a labeled engineering artifact**
(Exp139b, §2): it confirms the classical prediction on silicon (destination 37.6σ colder than a
single input) but does **not** extend ICO — it takes no F-number and no switch-spec ledger row, per
the F94 fuel-mislocation guard. Computed with the frozen theory in
`experiments/exp108_ico_refrigeration.py`.

## 1. Route A — cascade (feed the cooled qubit back through the switch)
Iterate the exact map ρ → (+ branch) of the two-thermalizing-channel switch (g = 0.75, bath p₁ = 0.25):

| stage | p₁ (heralded +) |
|---|---|
| 0 (bath) | 0.2500 |
| 1 | 0.1848 ← the F118 single-shot value |
| 2 | 0.1779 |
| 3 | 0.1772 |
| 4–5 | **0.1771 (fixed point)** |

The cascade converges to **≈ 0.177** after ~3 stages and stops. This is the **genuine ICO cooling
floor** for these baths — the switch's interference can pull the target to 0.177 below the bath, no
further; the thermalizing channels keep the input from mattering more. It does **not** approach zero.
Each extra stage also costs another herald (P ≈ 0.72/stage) and ~22 more CZ of depth, so on hardware
the cascade *inverts* (F118's 22-CZ haircut of +0.025 already exceeds the stage-2 theory gain of
0.007) — the F85 scaling-inversion pattern. **Cascade is not worth flying.**

## 2. Route B — concentration (combine multiple cold qubits into one)
Majority-vote of 3 i.i.d. qubits each at population p gives destination p₁ = **3p² − 2p³**:

| input p₁ | majority p₁ |
|---|---|
| 0.185 (ICO theory) | 0.090 |
| 0.210 (F118 hardware) | **0.114** |
| 0.250 (bare bath) | 0.156 |

So three F118 qubits concentrate to ~0.11 — colder than one. **But this is classical.** Majority
vote is entropy compression that works on *any* biased bits; the ICO-cold states are **diagonal**
(thermal populations), the majority commutes with the computational basis, and **no coherence is
used**. The identical 0.11 is obtained by measuring 3 ICO-cold qubits and taking the classical
majority in post-processing — a coherent Toffoli-majority (27 routed CZ in sim) buys nothing, because
there is no downstream coherent consumer of the "live" cold qubit. A FakeMarrakesh sim confirmed the
concentration survives noise (3×0.185 → 0.105; bath 3×0.25 → 0.170), but that only shows the
*classical* compression can be built, not that ICO was extended.

**Flown as a labeled engineering artifact (Exp139/Exp139b, Creator-directed).** At Creator direction
the coherent concentration was run on `ibm_marrakesh` (4 qubits, 24 CZ; inputs prepared at F118's
cold population 0.21 to isolate the concentration step): the destination qubit came out at
**p₁ = 0.1341 ± 0.0017**, **37.6σ colder than a single input** (0.2135), and colder than the
bath-seeded concentration (0.1728) — a physically-produced (not post-selected) sub-single-input cold
qubit on silicon (WIN, `results/exp139b_grade.json`, job `d9bh1dbv6alc73ct23l0`; the first attempt
graded NO-TEST on a FakeMarrakesh-optimistic sentinel floor, re-flown with the floor re-derived from
measured gate/readout error). The measured 0.134 sits +0.020 above the classical 0.114 — the 24-CZ
depth haircut. **This changes nothing about the physics claim**: it confirms the *classical* formula
on hardware and demonstrates the compression circuit runs; it is **not** an ICO result and takes no
F-number / switch-spec ledger row. The ICO content remains F118; the ICO floor remains 0.177.

**Scope / attribution (the load-bearing point).** The ICO physics is **F118, unchanged**. The
concentration is a generic amplifier applied to F118's outputs. Reporting "ICO drove a qubit to 0.11"
would attribute to the quantum resource what a classical AND/majority gate on three readouts does for
free — the same **fuel-mislocation** the F94 audit (C4717) corrected ("conjured from causal
structure" when the fuel was routed elsewhere). If a coherent concentration is ever built, it ships
labeled as a **classical entropy-compression primitive seeded by F118**, with the ICO physics
explicitly *not* extended.

## 3. Route C — colder baths (the strong lever, but it isn't "compounding")
The + branch is a fixed fraction (~0.74×) below whatever bath it is fed: bath 0.25 → 0.185, bath
0.10 → 0.058, bath 0.05 → 0.027. This is the only lever that moves the number a lot — but it is
"**start with a colder bath**," not the fridge compounding, and if you *had* a 0.05 bath you would use
it directly. The fridge's value remains what F86/F118 established: sub-bath cold from the warmest bath
you have.

## 4. Bottom line
- **The ICO resource saturates at ≈ 0.177** (cascade fixed point). There is no known route that beats
  this floor *via indefinite causal order alone*.
- Below 0.177 is reachable only by **classical entropy compression** (majority → ~0.11 from F118
  qubits; works on any biased qubit) or **colder baths** — neither is new ICO physics.
- **Deliverable = this decomposition.** The honest answer to "can we drive it colder" is the boundary
  itself. The classical concentration was flown as a labeled engineering artifact (Exp139b, 37.6σ,
  4 qubits — not the 13-qubit 3-fridge version, which would add NO-TEST risk for no new physics); it
  confirms the classical formula on silicon and is **not** an ICO result.

*Anchors: F86/F118 (the single-shot cold), `exp108_ico_refrigeration.exact_targets` (cascade map),
the majority formula 3p²−2p³ (classical). Provenance for the F94 fuel-mislocation lesson:
`docs/findings/adversarial-audit-F94-ico-engine-whisper-c4717.md`.*
