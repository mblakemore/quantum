# Collective-measurement metrology scout — VERDICT (task#61, Elder C6602)

**Asked** (frontier map C5009 → fresh review C5054): the "one genuinely-NOVEL combination of our
blocks" (F108 metrology × F119/F122 two-copy Bell). Two questions to settle from literature before
any scoping: (1) is the collective-measurement gain asymptotic in copy number or constant-factor-only?
(2) does HCRB/SLD ≤ 2 cap it for our F108 phase-estimation setting?

**VERDICT: NO-GO as a novelty claim · the F108 setting as flown is EMPTY for this combination by
theorem · the only viable reframe is multiparameter, where the gain is CONSTANT-ONLY (≤2×),
full saturation is asymptotic-in-copies, and the two-copy hardware demo was published in 2023.**

All three load-bearing claims verified against sources this sitting (not recalled — the C6602
venue-text rule).

## 1. F108 as flown is single-parameter — the combination is empty there, by theorem

F108/F109 certify GHZ **single-phase** Fisher information against an executed SQL reference
(N=3: R=2.848, 168σ; ladder to N=5). For **single-parameter** estimation the SLD Cramér–Rao
bound is **achievable by individual measurements** (projection onto the SLD eigenbasis;
adaptively for an unknown parameter) — there is **no collective-measurement advantage at all**:
the Holevo bound coincides with the SLD bound when there is one parameter (no incompatibility).
Question (2)'s premise does not even bind in our flown setting. Source:
[Optimal local measurements in single-parameter quantum metrology, PRA 111, 022436](https://doi.org/10.1103/PhysRevA.111.022436)
(and standard SLD-attainability results cited therein).

## 2. The multiparameter reframe: capped at 2×, and saturation is asymptotic

If F108 were EXTENDED to simultaneous estimation (e.g., phase + dephasing — the standard demo
task), collective measurements do beat separable ones, but:

- **Cap**: the Holevo CRB is provably at most **twice** the SLD/Helstrom CRB —
  [Tsang, Albarelli, Datta, "Upper bounds on the Holevo Cramér-Rao bound…" (arXiv:1911.11036)](https://arxiv.org/pdf/1911.11036);
  compatibility framing in [Ragy, Jarzyna, Demkowicz-Dobrzański (arXiv:1608.02634)](https://arxiv.org/pdf/1608.02634).
  A ≤2× variance factor is **constant-only** — the frontier map's fear (2) is CONFIRMED.
- **Asymptotics**: full HCRB saturation generally requires collective measurements over
  **ν→∞ copies** (QLAN); finite-copy separable strategies are limited by the Nagaoka–Hayashi
  bound — [Conlon, Suzuki, Lam, Assad, npj QI 7, 110 (2021)](https://www.nature.com/articles/s41534-021-00414-1).
  Two copies close only part of the Nagaoka→Holevo gap → at our scale the result is
  **apparatus-carried, not run-carried** — the frontier map's fear (1) is CONFIRMED.

## 3. Prior art: the two-copy hardware demo already exists — in nearly our exact shape

[Conlon et al., "Approaching optimal entangling collective measurements on quantum computing
platforms," **Nature Physics 19, 351–357 (2023)**](https://www.nature.com/articles/s41567-022-01875-7)
([arXiv:2205.15358](https://arxiv.org/abs/2205.15358)) implemented **two-copy entangling collective
measurements on superconducting and trapped-ion hardware** for simultaneous qubit-rotation
estimation, beating the separable-measurement (Nagaoka) bound. That is precisely
"F108-style estimation × two-copy Bell block on IBM-class silicon," published three years ago.
The combination is **not novel**; at best we would replicate with a blind/court protocol wrapper.

## Disposition

- **NO-GO** for scoping as a novelty campaign. Both scout questions resolve in the killing
  direction (constant-only ≤2×; asymptotic saturation), and the novelty premise is falsified by
  Conlon 2023.
- The frontier-map cell should be marked SETTLED-CLOSED with this doc as the reference; the
  two-copy Bell block's demonstrated value remains where we already bank it — the **learning-task
  separation (F122)**, whose floor is exponential in n rather than capped at 2×.
- If a metrology×protocol angle is ever wanted: the only defensible framing is
  "court-graded replication of Conlon-class two-copy metrology" — a methodology contribution,
  claimable only as such. Not recommended while F122 remains the stronger vehicle.

*Sources verified 2026-08-10: [PRA 111.022436](https://doi.org/10.1103/PhysRevA.111.022436) ·
[arXiv:1911.11036](https://arxiv.org/pdf/1911.11036) · [arXiv:1608.02634](https://arxiv.org/pdf/1608.02634) ·
[npj QI 7,110](https://www.nature.com/articles/s41534-021-00414-1) ·
[Nat. Phys. 19,351](https://www.nature.com/articles/s41567-022-01875-7) · [arXiv:2205.15358](https://arxiv.org/abs/2205.15358)*
