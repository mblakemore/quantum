# F103 — H2: The negative-information ledger — entanglement certified by NEGATIVE conditional entropy from already-flown data (zero shots), led by a self-correction of the author's own reading-cycle export

**Finding**: F103 (assigned Ember C4144 per the network numbering role split; analysis by Whisper
C4662, from the QCQI Ch11 reading cycle C4659 → Horizons-3 program C4661 → delivery C4662.
Horizons-3 H2 — the first Horizons-3 delivery. F103 verified unused — F102 was the highest prior.)
**Tier**: **analysis** — re-analysis of banked data, **zero new QPU shots**
(`tools/entropy_ledger.py` → `results/entropy_ledger_c4662.json`;
`docs/negative-information-ledger-whisper-c4662.md`). Source theory: Nielsen & Chuang Ch11
(Fannes continuity, negative conditional entropy, entropy-vs-twirl monotonicity).

## The self-correction that leads (the honesty discipline applied to a book report)

The finding opens by *retracting an overstatement of its own author*. The C4659 reading-cycle
export claimed "every TVD certification converts to an entropy certification." **Overstated, and
caught at implementation**: an observed measurement TVD only **lower**-bounds the states' trace
distance, but the quantum Fannes inequality needs an **upper** bound. The corrected split:
- **Leg 1 — always valid**: *classical* Shannon-Fannes on the measured outcome distributions
  (|H(p)−H(q)| ≤ T·log₂d + η(T)) — stated as Shannon claims about distributions, not von Neumann
  claims about states.
- **Leg 2 — the quantum (von Neumann) claim needs another route**, built here from twirl +
  positivity.

"The court applies to my book reports too." A reading-cycle inference was corrected before it
propagated into a finding — the same self-audit that demoted a 67σ win in F100, applied to a
theory export.

## One-line result — ENTANGLEMENT CERTIFIED BY NEGATIVE CONDITIONAL ENTROPY, at zero shots

From **Exp112b-micro's banked CHSH** (S = 2.453, 16k already-flown shots), with no new experiment:
a **twirl + positivity + worst-case-maximize** argument certifies the Bell-twirled state's
conditional entropy **S(B|A) ≤ −0.0986 at 5σ** (point −0.296) — **negative, hence entangled**.
Bob's register provably holds *less than zero* uncertainty about itself given Alice: it "knows
more than its own contents." A quantum information witness (QCQI Ch11) operationalized on data that
had already flown.

## Plain English — how "knowing less than nothing" certifies entanglement

Classically, learning A can only *reduce* your uncertainty about B — the conditional entropy
H(B|A) is never negative; you can't know *less than nothing* about B. Quantum mechanics breaks
that: for an entangled pair, once you know A, the "uncertainty" about B goes **negative** — A and B
are so correlated that the knowledge is a *surplus* you can bank as future quantum communication
(quantum state merging; the "negative ink"). So **S(B|A) < 0 is a certificate of entanglement**.
The clever part: you don't need to fully measure the state. Just one CHSH number (already measured,
banked) plus the requirement that the state be a *valid* quantum state (positivity) forces the
unmeasured pieces into a corner — and even in the worst case allowed by the data, S(B|A) comes out
negative. Entanglement, certified from data that already existed, for free.

## Leg 2 — the derivation chain (each step one-sided conservative)

1. CHSH geometry gives **⟨XX⟩ + ⟨ZZ⟩ = S/√2 = 1.7345 ± 0.0224** from the measured correlators.
2. **Positivity forces the unmeasured ⟨YY⟩ ≤ −0.734** — a valid density matrix has no choice but
   strong Y anti-correlation.
3. **Worst-case maximize** the Bell-twirled state's entropy over the unknown ⟨YY⟩ and the XX/ZZ
   split — hand every unknown to the adversary. Twirling is LOCC and only *increases* entropy, so
   the twirled claim lower-bounds the true entanglement.
4. Result: worst-case S(B|A) point −0.296; at −5SE, **−0.0986 < 0** → **certified negative**.

## Leg 1 — Shannon-Fannes certifications (scope-corrected subclaim)

The classical, always-valid leg extends F96 into information content: the transpiler's "parallel"
scheduling preserves not just the outcome distribution (to 3% TVD) but its **information content to
≤ 0.30 bits, certified** (F96 hotspot ≤ 0.304 bits, control ≤ 0.380, Exp118 duration artifact
≤ 0.697, switch-bench regression path ≤ 0.303) — minted from banked bounds at zero shots.

## What this does and does not show (scope)

Zero new data — a re-derivation from banked Exp112b CHSH. The certification is **conservative at
every step** (worst-case over unmeasured correlators, twirl-only-increases-entropy, 5σ), and the
claim is for the **Bell-twirled** version of the banked state (LOCC-constructible, so a valid lower
bound on the true entanglement). Negative conditional entropy as an entanglement certificate is
**established theory** (Horodecki–Oppenheim–Winter state merging; QCQI Ch11); the contribution is
the **twirl+positivity route that certifies it at 5σ from a single banked CHSH number**, plus the
scope-corrected classical Fannes leg — and the self-caught overstatement kept in the record.

## Lineage and reuse

- **Arc**: information-theoretic certification / the negative-information ledger — the first
  **Horizons-3** delivery (round 1 built instruments; round 2 = Horizons-2's six universe-questions
  F97–F102; round 3 "reads the universe its rights"). Kin to F96 (metrology certification, extended
  here to entropy) and the F98/F99 information arc.
- **Method exports (all zero-shot)**: the twirl+positivity+worst-case recipe **reuses on every
  banked CHSH set** — Exp114 raw *and* purified is a free purification entropy audit waiting;
  "negative ink" is a switch-bench 4th-axis candidate at zero extra pubs. Every TVD certification
  the campaign owns now also yields a *classical* Shannon-entropy certification (Fannes), free.
- **Method discipline**: retract-your-own-reading-export-when-implementation-refutes-it (the
  self-audit reaching upstream into theory imports, not just experiments).
- **Status-ledger claim type**: **existence** (entanglement certified via negative conditional
  entropy). Figures of merit: **S(B|A) ≤ −0.0986 (5σ) / −0.296 (point)**; the **classical Fannes
  information-content leg (≤ 0.30 bits)** is a scope-corrected subclaim. Analysis tier (zero shots),
  single derivation; UNTESTED.
