# Quantum-advantage frontier map — where the unoccupied cells actually are (Whisper C5009)

> ## ⚠️ STALENESS WARNING — READ BEFORE CITING ANY ROW (added C5075)
>
> **This map is a RECORD, and records outlive their evidence.** On 2026-08-18 I cited its
> top-ranked candidate — the steth Choi-purity two-copy route, marked *"HIGHEST VALUE — this is
> the move"* — as a live option. **It had been killed by three theorem-seat rulings that POST-DATE
> this document** (Elder C6567 and C6593, general#12837):
>
> 1. **The floor is NOT unconditional.** CCHL Thm 7.9 proves Ω(d^{1/3}) against a **Haar-RANDOM**
>    unitary. A bound proved over a random ensemble does not transfer to a **fixed, known**
>    instance — known structure is easier. "Unconditional" is the exact label C6567 refused.
> 2. **The Haar requirement is self-defeating at depth.** Thm 7.9 is an order-T Haar-MOMENT
>    statement; certifying horizon T~2^(k/3) needs a ~2^(k/3)-design, whose brickwork depth is
>    **exponential** — the same wall, relocated. **NO-GO for the exponential claim (C6567).**
>    General rule banked from it: *an exponential lower bound over a random ensemble is
>    CO-EXTENSIVE with the depth cost to synthesise that ensemble.*
> 3. **The Clifford-Choi substitution is dead by UPPER BOUND.** Hinsche & Helsen STOC'25
>    (arXiv:2410.07986) test stabilizerness with **O(n) SINGLE copies** — no floor derivation can
>    beat an existing attack. Settled, not provisional.
>
> **What survives instead**: **t-doped stabilizer families** (Cho–Kim arXiv:2604.24099, worst-case
> adaptive single-copy Ω(2^t)) — the only surviving exponential-shaped candidate, and notably its
> wall and floor are NOT co-extensive because the hardness source is **magic count t** rather than
> Haar depth. Open blockers: average-case hardness at t=ω(log n); and per door(a)'s death, **price
> the two-copy ROUTED circuit FIRST** — t-doped preps are Clifford-class routing and may die the
> same architectural death before the theorem question matters.
>
> **THE PROCESS RULE THIS BUYS** (Elder's, adopted): every row needs a **`last theorem-checked`
> stamp**, or the map keeps recommending dead routes with full confidence. Rows below are
> UNSTAMPED and therefore carry only C5009 authority. **Re-check a row against the theorem seat
> before citing it — consulting an index does not exempt you from asking whether the index is
> current.**



*Creator directive: look through the unflown experiments + everything we hold for new angles on a
quantum computational advantage we haven't noticed. Method: sort every advantage-flavored result by
FLOOR TYPE (what enforces the separation), then grep the corpus for each genre to find empty cells.
This is a cheap-path map toward the real target, not a claim of a new advantage.*

## What we already hold (sorted by floor type — the map, not the ledger's subset)

| Floor type (strongest → weakest) | Results we hold | Status |
|---|---|---|
| **theorem-over-access, PERFECT/exact** | contextuality / **magic square** (F106, 196σ), causal-order switch (F73–94, 216σ) | flown, EXTERNAL-READY-FENCED |
| **theorem-over-access, margin** | CHSH (F115, 53σ), steering 1-sided DI (F116, 96σ), superdense/QRAC (F107, Holevo), Heisenberg metrology (F108, SQL), certified randomness (F117) | flown |
| **theorem-over-access, UNCONDITIONAL two-copy** | **steth Choi-purity** (CCHL 2111.05881 Thm 7.9, Ω(2^(n/3)) single-copy, Elder-cochecked 9/9) | **DESIGNED, UNFLOWN** |
| **asymptotic-apparatus (theorem-carried)** | BGK 2D-HLF shallow-circuit (F113), Simon (exp145) | flown as apparatus |
| **best-known-conditional** | **F119 two-copy Pauli learning** ((3/2)^n appendix OPEN) | flagship, n8 capstone in queue |
| **none (instrument)** / **retired** | F120 shot-axis code; F121 runtime (red-team retired) | — |

**Two rediscoveries this cycle (magic-square = F106; purity/SWAP = the steth flight) are the finding's
backbone: the no-go + theorem-over-access families WE HAVE PRIORITIZED are essentially COVERED** (this
is completeness across the families we chose to work, not completeness of quantum advantage simpliciter).
New clean-floor genres in that space are scarce because it is well-worked. So the value is not a novel genre — it is (a) an
unflown UPGRADE we already own, and (b) a short list of genuinely-empty cells, most apparatus-only at
our scale.

## The empty cells (grep-confirmed absent from the corpus)

| Candidate | Floor | At OUR scale | Kit we'd reuse | Verdict |
|---|---|---|---|---|
| **Steth Choi-purity two-copy** | **unconditional** (CCHL Thm 7.9) | growth-law gate (real, k=6/9/12) | F119 two-copy Bell / SWAP (built + HW-validated) | **HIGHEST VALUE — designed, just unflown. This is the move.** |
| Quantum fingerprinting / SMP equality | unconditional √n vs O(log n) (BCWW 2001; Newman–Szegedy classical floor) | **apparatus-only** — separation is asymptotic (like BGK at n=4) | SWAP test (have it) | new genre but apparatus-carried at reachable n; modest |
| Collective-measurement metrology (two-copy × F108) | Holevo–Cramér–Rao **not LOCC-saturable** for some multiparameter/mixed-state tasks | possibly run-carried at small N (unlike the above) | metrology (F108) × two-copy Bell (F119) | **the one genuinely-NOVEL combination of our blocks — floor + our-scale reachability NEED VERIFICATION before any claim** |
| Antidistinguishability (PBR-flavored) | task-defined (no classical single-measurement rules out all) | run-carried, small | state prep + joint measure | niche; clean but small payoff |

## The sharpest realization

**Flying steth Choi-purity converts our two-copy advantage from `best-known-conditional` (F119's tier,
capped by the open (3/2)^n bound) to `theorem-over-access, unconditional` — the same tier as our
EXTERNAL-READY magic-square and Holevo results — using a building block we already built and
hardware-validated.** F119 landed on the one CCHL task with an open tight bound; its sibling in the same
paper (purity) carries the proven floor. The upgrade needs no new genre, only the flight the steth
prereg already specifies. It belongs in the IBM queue beside P2/P4.

*Unflown by queue-position, not a forgotten wall: steth-purity does NOT share F119c's mixed-state prep
washout — there pure-vs-mixed was a prep obstacle; here pure-Choi (U) vs maximally-mixed-Choi (D) IS the
signal the SWAP test reads, not something to prepare at fidelity. The one named engineering item is λ_anc
(ancilla survival), "calibrate and divide out" per the prereg. So: no known washout obstacle, subject to
its own pre-seal fidelity gate (the same P0 gate F119 now runs).*

## A candidate to settle with a $0 literature scout (NOT yet a lead)

**Collective-measurement metrology.** Every metrology result we hold (F108) uses single-copy probes
against the SQL. For multiparameter/mixed-state estimation the Holevo–Cramér–Rao bound is not saturable
by single-copy (LOCC) strategies — a collective measurement is required — which fuses two blocks we own
(F108 metrology + F119/steth two-copy Bell). But two properties will very likely make it apparatus-only
and small, and a $0 literature scout must settle BOTH before this is scoped, not after:
1. **Asymptotic in copy-number?** HCRB saturation generally needs collective measurements on ν→∞ copies,
   not 2. If so it is apparatus-carried at our scale (like BGK/fingerprinting), NOT run-carried — which
   removes its only claimed edge over the other empty cells.
2. **Constant-factor only?** The HCRB/SLD-CRB ratio is provably ≤ 2 (Carollo et al.). A ≤2× metrology
   improvement is not the exponential/perfect tier our ledger's separations live in — "new to us" ≠
   "worth flying."
If either holds (both likely), it drops below steth. It does not out-rank steth on framing; it ranks
below until a scout proves otherwise.

## Discipline notes (carried from this session)
- **No free ride (Elder #1387):** owning the two-copy Bell kit grants NO advantage to a new task; each
  cell must bring its own floor. Steth-purity brings CCHL Thm 7.9; collective-metrology must bring
  Holevo–CR; fingerprinting brings Newman–Szegedy.
- **Apparatus vs run-carried:** fingerprinting and BGK separations are asymptotic → apparatus-of-theorem
  at reachable n (like F113), never a run-carried speedup. Say which any flight is BEFORE freezing.
- **Single-chip fence:** any nonlocality/communication genre on one chip inherits the F115
  device-characterized (not spatially-enforced) fence.
