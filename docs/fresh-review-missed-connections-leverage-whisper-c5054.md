# FRESH REVIEW — what we missed, what connects, and where the remaining leverage is

**Author**: Whisper (DC15W), C5054 (2026-08-10) · **Substrate**: claude-fable-5
**Creator directive**: "do a fresh review cycle on anything we've missed and any connections we've yet to make, or any further way we could possibly leverage quantum abilities to our advantage."
**Method**: two parallel corpus sweeps (811 .md files: findings + docs cross-checked against results/ flight artifacts) + targeted rediscovery passes + Tier-0 gate verification. Everything below is receipt-backed; agent inventories are summarized, not trusted blind — the load-bearing items were re-verified against the primary artifacts.

---

## 1. THE BIGGEST MISS — six flown flights have no findings (the record has a hole in it)

The H10 wing flew five cells across C5015–C5018 and **none of them was ever written up**:

| Flight | Result sitting in results/ | Debt |
|---|---|---|
| **B1 Time Flip** (3 jobs, 2 backends) | forward/backward-superposed process beats the definite-time-direction ceiling at **113–200σ** — arguably the campaign's sharpest physics | no finding, no F-number, no museum presence |
| **A1/A1b/A1c Quorum Fact** (3 jobs) | A1b confirmed the encode-DAG depth mechanism (+2.07σ over bar); registered conjunction did not hold | no findings; preregs still read "awaiting seal" |
| **B4 Heat Backward** | cold→hot from correlations **NOT HELD** (−0.0052 at 2.3σ) vs uncorrelated control +0.137 at 22σ — separation 21.4σ, a clean registered negative | no finding, **and the comprehensive status doc says "never flown anywhere" — a direct artifact-vs-ledger contradiction** (two other docs repeat it) |
| **C2 Vacuum Harvest** | negativity dead on all arms — the negative that calibrated the **~250-2q many-body ceiling**; Elder-ratified | no finding |
| **C1 Winding Meter** (S0 pilot) | λ̂ = 0.0259 → **NO-FLY** at the stage gate — the negative that calibrated the **~475-2q interferometric ceiling** | prereg carries redesign notes; needs formal retirement or fresh scout |

**Why this is the top item**: un-written flights are invisible to `already-built.js` (it greps findings/ and the ledger) — so this is the rediscovery bug one level up: **flown ≠ banked**. The B4 contradiction proves the failure mode is live: our own status doc denies a 21σ result we possess. The fix is $0 and mostly mine (the flights were my seat): write the six findings, correct the three stale status lines, then hand the time flip to the museum. **This review's first concrete output: board row filed, my name on it.**

## 2. THE SECOND MISS — the flagship is flight-ready and was never promoted

**H13 Cell 2 (Causal Compass)** — the arc's only advantage-class claim, the Pearl seat's signature experiment:
- Tier-0 gate **T0.3 is a GO on its own numbers** (verified this cycle from `results/h13_t03_compass_design_c5048.json`): sign-product fingerprint **+0.78 (cause-effect) vs −0.81 (common-cause)** under the realistic noise model, classical analyst ceiling enumerated at **0.5029**, significance **61–134σ across 2000–8000 shots/basis**, 18 circuits + matching calibration, Z-marginal TVD 0.006 (the matched-statistics premise gate is nearly free).
- Its measurement pipeline is not hypothetical — it is **the Cell 3 instrument, already flight-certified at 293σ**.
- Remaining: court freeze (3-of-3), claim card + attack_preflight, and a small window (~15–25 QPU-s at the C5048 MCM-corrected pricing).
Nothing about this cell is speculative anymore; it simply was never moved from DRAFT after its gate passed.

## 3. NEW CONNECTIONS (not in any existing doc)

1. **Temporal steering is a $0 re-analysis of data we already own.** Rediscovery pass (this cycle): clean — no prior anywhere. Cell 3's certified flight (`d9rufentfhrs73ds52cg`, 18 temporal circuits × 2000 shots, all 9 sequential Pauli-pair settings) contains exactly the joint distributions a temporal-steering witness needs. If IBM retains the raw counts (it retained exp135's from June), this is a **second certificate from an already-paid flight** — scoped honestly as post-hoc re-analysis against a theory-fixed bound, Hardy-style. One dataset, two findings.
2. **QSEED × the blind courts.** Sealed flights need instance-selection randomness; today the sealer's choice is trusted. QSEED seeds with anti-shopping receipts close a standing attack surface ("sealer chose favorable instances") on **every future blind flight** — court infrastructure, not just Monte Carlo seeding. Zero marginal QPU (pool v0 is banked).
3. **The entropy piggyback rule inverts the cost question.** Any future flight carrying Bell-health circuits donates shot-entropy to the QSEED pool at $0 marginal — science flights become entropy harvests as a by-product. Cell 2's own window qualifies.
4. **B1's time flip belongs in Cell 8's story.** The unwritten B1 result (time-direction superposition beats *even the switch*) is the natural capstone of the causal-structure wing the Cell 8 spec just organized — writing its finding wires the two arcs together and gives Dawn's temporal wing its missing centerpiece.
5. **Collective-measurement metrology (F108 × two-copy Bell)** — the frontier map called this "the one genuinely-NOVEL combination of our blocks" and its $0 literature scout (two named questions: asymptotic-in-copies? HCRB/SLD ≤ 2 constant-only?) **was never run**. Still the cheapest untouched novelty on the shelf.

## 4. GENUINELY OPEN LEVERAGE, RANKED (all F-arc-checked; walls honored — nothing below re-proposes the 10 standing NO-GOs)

**$0, executable now:**
- (i) Six H10 findings + three ledger corrections (§1) — unblocks museum + F-arc coverage.
- (ii) Temporal-steering re-analysis protocol + raw-count fetch check (§3.1).
- (iii) Collective-measurement metrology literature scout (§3.5).
- (iv) **P3 NISQ replication audit scoping pass** — proposed since C4108, never scoped; our refutation methodology (F06/F07) is battle-tested; pick 3–5 published NISQ-advantage claims with reproducible circuits and price the audit.
- (v) **Hidden-order diagnostics (T2.5)** — flagged C4586 as "the most underrated unexecuted hardware item… noted so it stops being silently deprioritized." It got silently deprioritized anyway; decide deliberately (scope it or retire it).
- (vi) Museum hygiene to Dawn: three mutually-contradicting exhibit counters on index.html, two built-but-unregistered exhibits (`casebook-pnp`, `shots`), the F122 *distribution* leg absent from the sealed-shadow floor, and (once §1 lands) the H10 wing.

**Cheap QPU (compete for the 181s ALT3 tank — the triage the Creator actually has to make):**
| Candidate | Cost | Standing |
|---|---|---|
| **Cell 2 Causal Compass** ⭐ | ~15–25s | T0.3 GO, instrument proven, advantage-class, court-freeze needed first |
| Cell 6+6b merged window | ~45–55s | designed, freeze-sim owed |
| door(b) i3 seal `338343d8` | fit-gate call | DRAWN, PUBLISHED, UNSPENT — must be the seal flown (no shopping) |
| Cell 5 pigeonhole leg / Cell 4 / Cell 7 | ~10–25s each | designed DRAFTs |
| F122 distribution i2/i3 (board #51, Ember) | needs 193.5s margin | blocked at current tank |
**Recommendation**: Cell 2 first — it is the flagship, its gate passed, and its window is the smallest of the advantage-bearing options. Then Cell 6+6b on the next refill alongside the standing spends already greenlit (steth Choi-purity C5010 "the move", P2 Diplomat ~250s, door(a) n=12/16 — the last **blocked on the HH25 tester that does not exist**, an Elder literature item, not QPU).

**Parked with named gaps (correctly parked — review confirms, no action):** t-doped stabilizer families (3 blockers, literature-first), hidden matching (unconditional but sequenced behind the computational path), SDI entropy bound (QSEED rung 2), route3 plateau (self-imposed reviewer stand-down), cross-platform wall tests (ORQ#4/5 — need non-IBM hardware we don't have).

**Standing anomalies left unexplained (visibility, not action):** Exp188b's sign-flipped unechoed residual (+0.128); Exp183's ±0.10 sift-sector residual at ~9σ where ideal is 0. Parked statistically, never mechanistically — flagged so they stay visible.

## 5. WHAT THE REVIEW SAYS ABOUT PROCESS (one paragraph, because the retrospective already said it)

Every miss above is the same species: **a result or a GO that existed only in an artifact no traversed path reads**. Flights without findings are invisible to the rediscovery tool; a Tier-0 GO without a promotion step never becomes a flight; a "most underrated item" note without an owner gets deprioritized again. The fix applied here: each §4(i–vi) item leaves this review as a board row with an owner, not a paragraph.

---

*The inventory says we are not short of quantum leverage — we are short of custody. The sharpest unclaimed result in the repo is one we already flew.*
