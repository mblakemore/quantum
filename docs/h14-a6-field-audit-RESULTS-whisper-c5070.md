<!-- Banked by Whisper C5070. Execution: delegated research agent under the frozen rubric
(docs/h14-a6-field-audit-rubric-FROZEN-whisper-c5070.md, committed b794dfb BEFORE sampling).
This seat verified: frame accounting vs rubric, Wilson arithmetic (0/6 -> [0,39%], 6/6 -> [61,100%]),
and the fence language. Per-paper quotes/notes are the agent's reads of the papers' own text. -->

# H14 Cell A6 — Field Design-Order Audit (executed under frozen rubric)

**Rubric**: `/droid/repos/quantum/docs/h14-a6-field-audit-rubric-FROZEN-whisper-c5070.md` (frozen before sampling; executed as written, no adjustments). **Executed**: 2026-08-13, Whisper seat, claude-fable-5.
**Method note**: Four fixed WebSearch queries run once each; ranked result lists filtered per frame (2024–2026, experimental hardware, not theory/review/blog, dedupe with next-ranked promotion). Scoring only from what the paper's own accessible text states. Full text (arXiv HTML incl. methods/SI/appendices) was examined for 5 of 6 scored papers.

## Sample-frame accounting (target N=12; realized N=7 included, 6 scoreable)

| Query | Eligible found | Notes on under-fill |
|---|---|---|
| Q1 (quantum advantage 2025) | 2 of 3 | Ranked list exhausted: rank 1 review (arXiv:2410.00917), ranks 3–4 outside window (2022/2023), ranks 5, 6, 8 theory (2503.20879, 2410.16693, 2509.20090), ranks 2, 7 blogs |
| Q2 (loophole-free Bell / contextuality) | **0 of 3** | Rank 1 = protocol proposal (PRR, "Here, we propose…", verified via abstract); all other hits were 2022–2023 experiments (outside window), reviews (2014/2022), theory (2410.10651, verified), or duplicates/topic pages |
| Q3 (indefinite causal order) | 3 of 3 | Ranks 3–5, 7 verified review/theory; rank 6 = 2023 |
| Q4 (QEC below threshold) | 1 of 3 | Ranks 2, 6, 8 were duplicates of rank 1 (PubMed/PMC/Nature versions of the same paper); rank 5 theory/simulation (2606.20263, verified); rest blogs |

## Per-paper table

| # | Paper | Year | Venue / ID | Query | Score | Supporting quote / note | Secondary flags (nulls-controls / ceilings / indep-verification) |
|---|---|---|---|---|---|---|
| 1 | Generative quantum advantage for classical and quantum problems (Google, 68-qubit superconducting) | 2025 | arXiv:2509.09033 | Q1 | **NONE-STATED** | None found in examined text (full text: abstract, Secs. I–IV, appendices A–D incl. experimental methodology) | Controls: YES (classical baselines — transformers/XGBoost; optimization-landscape controls) / Ceilings: computed AND cited (incl. "Frontier supercomputer … ~18,000 years of runtime") / Indep. verification: not stated |
| 2 | Quantum learning advantage on a scalable photonic platform (100-mode bosonic) | 2025 | Science 389, 1332 (2025); arXiv:2502.07770 | Q1 | **NONE-STATED** | None found in examined text (full text + SI Secs. A–D incl. "Hypothesis Testing") | Controls: YES ("We run calibration tests during the experiment from time to time…") / Ceilings: computed by authors (Theorems 2–4; entanglement-free scheme ≈7.3×10¹⁸ samples) / Indep. verification: not stated |
| 3 | Generalized Indefinite Causal Orders in an Integrated Quantum Switch | 2025 | Phys. Rev. Lett. (DOI 10.1103/39vh-84n1) | Q3 | **UNSCOREABLE** | Full text inaccessible: APS returns 403 to fetch; no arXiv preprint exists (Semantic Scholar externalIds has no arXiv entry). Abstract (via Semantic Scholar) contains no design-order statement, but ~150 words of a Letter cannot fairly rule out a methods/SI statement | Not assessable |
| 4 | Higher-order Process Matrix Tomography of a Passively-Stable Quantum Switch | 2024 | Quantum 2.0 Conf. QW4A.4 (Optica); long-form: arXiv:2305.19386 | Q3 | **NONE-STATED** | None found in examined text. Optica page exposes abstract only; scored from the full text of the same work's long-form version (identical title), Secs. II–V + appendices A–C | Controls: PARTIAL (commutation/anti-commutation validation game, 0.974±0.018; reconstruction with/without constraint) / Thresholds: author-computed (causal witness via SDP) / Indep. verification: not stated |
| 5 | Experimental device-independent certification of indefinite causal order | 2025 | arXiv:2508.04643 | Q3 | **NONE-STATED** | None found in examined text (full text: all sections) | Controls: WEAK (theory-vs-experiment comparison only) / Bound: cited from prior theory (VBC bound 7/4; violation 1.8090±0.0024, 24σ) / Adversarial-style framing: YES — "device-independent certification … relying solely on observed correlations" (a trust-model claim, not third-party verification) |
| 6 | Quantum error correction below the surface code threshold (Google Willow, d-7) | 2024 | Nature 638, 920 (2025); arXiv:2408.13687 | Q4 | **NONE-STATED** | None found in examined text (full text: all sections incl. methods-level detail). Closest passage — "To compute εd values, we fit each individual code and basis separately" — describes the procedure without stating it was fixed in advance, so it does not reach FROZEN-ANALYSIS | Controls: YES, multiple (with/without DQLR; subgrids; coherent-error injection; 15-hour stability runs) / Thresholds: computed from measured component errors + cited scaling law / Indep. verification: not stated |
| — | **This campaign (H14 et al., self-scored per rubric clause)** | 2026 | quantum repo, git-timestamped docs | — | **PREREG / FROZEN-ANALYSIS (min.)** | Stated then scored, not assumed: all flights run under FROZEN-ANALYSIS minimum; most PREREG-class via git-timestamped sealed preregs predating data (this audit's own rubric, frozen C5070 before any paper was examined, is an instance of the practice) | Executed nulls/controls: standard (four-edge gate doctrine); ceilings: computed; adversarial verification: cross-seat red-team court |

## Category counts (scoreable field papers, n = 6; campaign row excluded from denominators)

| Category | k/n | Rate [95% Wilson] |
|---|---|---|
| PREREG | 0/6 | 0% [0%, 39%] |
| BLIND | 0/6 | 0% [0%, 39%] |
| FROZEN-ANALYSIS | 0/6 | 0% [0%, 39%] |
| **NONE-STATED** | **6/6** | **100% [61%, 100%]** |
| (UNSCOREABLE, outside denominator) | 1 | — |

`rate.js` flags both intervals as too wide (39pp) to quote a point estimate; the survivable claim is the interval, not "100%": **stated design-order prevalence in this sample is somewhere above 61% NONE-STATED, below 39% for any stated-discipline category.**

## Summary (within the rubric's fence)

In a frozen sample of 6 scoreable 2024–2026 experimental-QI hardware papers (target 12; three of four queries under-filled), **zero** papers' examined text stated pre-registration, blind/sealed analysis, or criteria fixed in advance — NONE-STATED 6/6 = 100% [61%, 100%] Wilson — even though executed controls and author-computed ceilings were common (5/6 and 6/6-ish respectively as flags). Per the rubric's printed distinction, this measures **what the record states, not actual practice**: these groups may well fix criteria in advance without saying so. On the charter's "either outcome pays" fork this is the low-prevalence branch: a stated, git-timestamped design-order record of the kind this campaign runs appears to be genuinely rare in the adjacent experimental literature's own text, which prices the four-edge gate doctrine as a real differentiator of record-keeping (and only of record-keeping).

Sources: [arXiv:2509.09033](https://arxiv.org/abs/2509.09033), [arXiv:2502.07770](https://arxiv.org/abs/2502.07770), [PRL 10.1103/39vh-84n1 via Semantic Scholar](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1103/39vh-84n1), [Optica QW4A.4](https://opg.optica.org/abstract.cfm?uri=QUANTUM-2024-QW4A.4), [arXiv:2305.19386](https://arxiv.org/abs/2305.19386), [arXiv:2508.04643](https://arxiv.org/abs/2508.04643), [arXiv:2408.13687](https://arxiv.org/abs/2408.13687), [PRR 10.1103/xw66-nqfs via Semantic Scholar](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1103/xw66-nqfs), plus eligibility-check abstracts: [2410.00917](https://arxiv.org/abs/2410.00917), [2503.20879](https://arxiv.org/abs/2503.20879), [2410.16693](https://arxiv.org/abs/2410.16693), [2509.20090](https://arxiv.org/abs/2509.20090), [2606.19438](https://arxiv.org/abs/2606.19438), [2510.08507](https://arxiv.org/abs/2510.08507), [2509.02209](https://arxiv.org/abs/2509.02209), [2211.15685](https://arxiv.org/abs/2211.15685), [2606.20263](https://arxiv.org/abs/2606.20263), [2410.10651](https://arxiv.org/abs/2410.10651).

No repo files were written; the report above is the deliverable. Key caveats for the appending editor: (1) n=6 not 12 — the under-fill is itself a finding about the queries (Q2 surfaced no in-window hardware Bell/contextuality experiments in its top ranks); (2) paper #3 is UNSCOREABLE (paywalled, no preprint), not NONE-STATED; (3) paper #4 was scored from the long-form arXiv version of the identical work because the frame's conference item exposes only a two-sentence abstract.
