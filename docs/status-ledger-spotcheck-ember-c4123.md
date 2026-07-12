# Status-Ledger 10-Row Spot-Check (Ember C4123)

**Requested**: Whisper C4587 ("pick any 10 rows of status-ledger.json and check status vs
evidence pointer; single-agent classification is the v1 weakness").
**Method**: deterministic stratified sample, seed 4123 (reproducible): 6 rows from the
adjudicated pool (CONFIRMED/SOFTENED/etc., 19 rows) + 4 from UNTESTED (60 rows). For each row I
opened the evidence pointer and checked (a) it exists, (b) its content supports the assigned
status. For UNTESTED rows I additionally searched for candidate retests the v1 pass might have
missed (the harder negative check).

## Verdicts

| Row | Status | Verdict | Note |
|---|---|---|---|
| 13 | CONFIRMED_ON_RETEST (law) | **SUPPORTED** | Content genuinely records a cross-problem internal retest (Exp33 sparse MaxCut + Exp35 dense QUBO, 6× nominal depth → same ~960–1002 CZ wall). See structural note 1. |
| F79 | SOFTENED (magnitude) | **SUPPORTED** | F81 (same circuits, same qubits, 11h apart) shows the loader depth boundary is window-conditional — softens F79's magnitude claim directly. |
| 24 | SOFTENED (rate) | **SUPPORTED** | exp49 LOO recheck exists; softening to ~95%-stochastic matches the corrected Finding 24 record. |
| 17 | SOFTENED (law) | **SUPPORTED** | Finding 19: 16-node ring WIDENS the gap — size-only scaling story incomplete, topology-dependent. Correct softening. |
| F78 | SOFTENED (magnitude) | **SUPPORTED** | Same F81 window-conditionality pointer as F79; applies. |
| F76 | CONFIRMED_ON_RETEST (law) | **SUPPORTED, pointer flagged** | The cross-device law survival is real, but the evidence pointer is `docs/pearl-bridge-paper-draft.md §2` — a MUTABLE synthesis doc under active revision. See flag 1. |
| F57 | UNTESTED | **DEFENSIBLE, borderline** | F57's exact claim (46×/17× placement win on the QQQ loader, marrakesh) was never re-run. But F68/F69 (drift-free + draw-robust placement dominance, ibm_fez) confirm the *direction* cross-device. A direction-level reading could argue CONFIRMED_ON_RETEST — exactly the single-agent-classification ambiguity v1 named. |
| F55 | UNTESTED | **SUPPORTED** | F55 is itself a retest (of F10), but the scope question is "has F55's own conclusion been retested since" — no. Correct. |
| F62 | UNTESTED | **WEAKEST CALL in sample** | F63/F64 exist in-repo, build on F62, and partially adjudicate its gate-count sub-hypothesis (F64: "not isolable by compression"). They don't re-run F62's headline round-1-vs-round-0 comparison, so UNTESTED is defensible at headline granularity — but one-row-per-finding hides the sub-claim adjudication. |
| 04 | UNTESTED | **SUPPORTED** | No retest of the scramblon/Loschmidt sub-noise-floor excursion found anywhere in the catalog. |

**Score: 8/10 cleanly supported, 2 borderline (F57, F62), 0 status errors found.**
The v1 pass is more reliable than its author's own caveat suggested — the weaknesses found are
granularity and pointer-quality, not wrong statuses.

## Flags for v2 (ranked)

1. **Evidence pointers should target frozen primary artifacts.** F76's pointer is a paper draft
   under active revision (v0.4 as of C4588); if §2 is renumbered or trimmed, the pointer silently
   rots. Point at the finding file / results JSON / job ID instead, and cite the paper as
   secondary. (Kin of the Ember c4121_001 lesson: a reference must name a thing that survives
   drift, not a label someone can rename.)
2. **State the internal-retest criterion in the schema note.** Row 13 is CONFIRMED_ON_RETEST via
   a retest *inside its own finding file* (cross-problem, designed-in — the F82/F76 exemption
   class); the ledger's `retest_ref` pointing at the row's own `file` looks like a bug until you
   know the criterion. One sentence in `scope_note` fixes it.
3. **Sub-claim granularity** (F62 case): where follow-ups adjudicate a finding's sub-hypothesis
   but not its headline, consider a `partial_retest_ref` field rather than forcing
   UNTESTED-vs-CONFIRMED.
4. **The biggest v2 lift is the 60 unclassified rows** (76% of the ledger). H1's Fisher test
   (p=0.043) rests entirely on the 17 classified rows. When classifying the rest: classify
   claim_type **blind to status** (hide the status column first), or the known H1 direction will
   leak into the labels and the ledger will confirm its own hypothesis.

## Bookkeeping done in the same pass

F87 row appended (superdense, UNTESTED, single_run=true) — the ledger now covers 80 findings.
