# Design Doc — Two Exhibits from Five Findings: "The Vault" & "The Past Is Not Fixed"

**Author**: Whisper (DC15W), C4878 · **Creator direction**: fold the Exp183–187 backlog
(general chat, 2026-07-19) · **Builds on**: findings 183, 184, 185/185b, 186, 187/187b —
all decode JSONs in `results/`, every number below verified against them.

**The folding rationale**: five pending stories are not five siblings. Exp183 is a *capability*
(multi-party cryptography) that completes the quantum-network wing's arc. Exp184–187 are four
facets of **one thesis** — the past is not fixed on quantum hardware — sharing interaction
motifs (late choices, off-switches, no-signaling audits) that become a spine when unified and
repetition when separated. Five backlog items → **two builds**.

---

# PART 1 — THE VAULT (`demo/vault/`, quantum-network wing)

## 1.1 Goal & the "aha"

A secret that opens to both officers together and to **neither alone** — enforced by physics,
not policy. The visitor's journey: look over Bob's shoulder (coin flips), look over Charlie's
(coin flips), turn both keys (Alice's secret reads out at 92%) — then switch the resource to a
mere Bell pair and watch the vault *invert*: one officer reads everything, and the group secret
dies. Wrong entanglement topology isn't weaker security; it is the complement of the protocol.

## 1.2 Data — verified (`results/exp183_secret_sharing_decode.json`, job `d9e3cqsjeosc73fi9lqg`)

| quantity | value |
|---|---|
| group reconstruction, 4 sifted bases (XXX/XYY/YXY/YYX) | 0.922 / 0.918 / 0.920 / 0.924 |
| single-officer blindness (worst \|⟨AB⟩\|,\|⟨AC⟩\|) | 0.028 |
| Mermin certificate M (LHV bound 2) | **3.369 — 61σ** |
| anti-pattern bellAB: ⟨AB⟩ / group recon | **+0.902** / 0.517 |
| product-state null: M / recon | +0.003 / 0.500 |
| sift-discard sectors (ideal 0) | +0.096 / −0.101 (coherent-prep residual, shown honestly) |

## 1.3 Panels

**A — Turn the keys (interactive).** A 3-way viewer selector: `[Bob alone] [Charlie alone]
[both together]`, over a resource selector: `[GHZ (the protocol)] [Bell pair (the anti-pattern)]
[nothing (null)]`. Center: Alice's secret bits (one row) vs the selected viewer's best guess —
mismatches flagged at the measured rate (GHZ: singles ~50%, together 8%; bellAB: Bob alone 5%!,
together 48%). A Mermin gauge (LHV line at 2, marker at 3.369±se) certifies the resource.
Verdict boxes: "can this viewer read the secret?" / "resource certified non-classical?"

**B — The court.** (1) WHY NEITHER OFFICER CAN PEEK — GHZ two-party marginals are maximally
mixed: blindness is a theorem, measured at ≤0.028. (2) THE ANTI-PATTERN — both failure modes in
one dataset (leak 0.902 AND group-death 0.517). (3) THE DISCARDED ROUNDS TALK — sift sectors
read ~0.10 where theory says 0: a real coherent-prep residual, harmless to the protocol
(discarded by design), kept on display as the free diagnostic it is. (4) FENCE — 3 qubits, one
die; information-theoretic layer only (no auth/EC/PA); deterministic per-circuit bases.

## 1.4 Gap review

| # | gap | fix |
|---|---|---|
| G1 | "unbreakable" overclaim | copy: blindness holds for the *quantum* record under HBB99's assumptions; fence names what's absent |
| G2 | key-stream honesty | seeded illustrative streams at the *measured* rates, labeled (per the relay-key precedent) |
| G3 | sift-residual could look like failure | own receipt framing it as diagnostic, with the finding's numbers |
| G4 | a11y/mobile/theme/measured-only | house rules; every number from the decode JSON |

## 1.5 Pre-dev & acceptance

Data kernel pasted from decode JSON; reuse relay-key stream + gauge idioms; selector = two
button rows (aria-pressed); stub-run all 9 viewer×resource combos. **Accept**: singles ≈ coin
flips on GHZ, together = 92%; bellAB inverts (Bob-alone reads, together fails); Mermin marker
3.369 vs line 2; null flat; card added (network wing).

---

# PART 2 — THE PAST IS NOT FIXED (`demo/past-not-fixed/`, flagship — seeds a sixth wing, "Time")

## 2.1 Goal & the thesis

One exhibit, four rooms, one sentence: **on quantum hardware, the past is not a fixed thing —
what happened is structure selected by choices made later.** Each room is one experiment with
its signature one-click; three spine motifs run across all four rooms instead of being
repeated: (i) **the late choice** (a control you flip *after* the record is closed), (ii) **the
off-switch** (one gate removes the phenomenon), (iii) **the no-signaling strip** (a live audit
bar under every room: "nothing propagates backward — the marginals never move").

## 2.2 The four rooms — data verified per room

**Room 1 — NO FIXED MOMENT (Exp184, job `d9e3ngcinv1c73appedg`).**
Qubit A measured/destroyed before D existed; late swap → F(A-record, D-record) = **0.832, 40σ**
over the 1/2 witness (ZZ +0.824 / XX +0.759 / YY −0.745); same schedule with a late *product*
measurement → **0.249, flat**; null 0.250; A-marginal spread across all later choices 0.0191.
*Interactive*: the late-choice lever — [Bell measurement] vs [product measurement] — resorting
the identical early record across the witness line. Gauge with the 1/2 witness; correlation bars.

**Room 2 — TIME IS ENTANGLEMENT (Exp185b, job `d9e4bgphtsac739dpt20`).**
Tick dial 0–3: conditional Bloch hand sweeps 90°/tick — (X,Y) = (+0.936,+0.035) →
(−0.039,+0.949) → (−0.952,+0.051) → (−0.034,−0.947), mean F 0.973. Outside view: correct-law
translation echo = **0.907 of the prep ceiling** vs wrong-law at **0.469 ≈ the theoretical ½**.
*The off-switch*: cut the two entangling gates → every tick identical at F 0.998.
*Interactive*: the tick dial + the TIME OFF button (the exhibit's emotional peak). Honest strip:
185 v1's leg-2 letter-fail by 0.008 and the rule-derived 185b amendment, told in one receipt.

**Room 3 — NO DEFINITE VALUE (Exp186, job `d9e4jsineu4c739o0shg`).**
K₃ meter: C₁₂ +0.493, C₂₃(INRM) +0.461, C₁₃ −0.511 → **K₃ = 1.465 vs the macrorealist bound 1
(24σ)** — mid-time value credited only from detectors that provably never fired (kept 0.998);
invasive agrees with INRM to 0.021. *The off-switch*: the dephasing toggle → C₁₃ flips to
+0.259, K₃ = 0.695, under the bound. *Interactive*: the K₃ needle crossing the red line, and
the toggle dragging it back to classical.

**Room 4 — NO DEFINITE ORDER (Exp187b, job `d9e4r2sjeosc73fib9hg`; v1 window numbers from 187).**
The same closed target record: Z-sort → the two definite orders (F 0.963/0.974); X-sort →
ensembles **17σ / 29σ off the equator** every definite-or-mixed order is pinned to (W₊ +0.218,
W₋ −0.657; hull broken X−Y = 1.326 > 1); decohered control sorts flat (difference 0.073);
no-signaling 0.0162 (pinned layout). *The twist that tops the room*: the echo lever —
defer-and-echo (W₊ **+0.467**) beats measure-now (+0.345); 196% of the delayed-choice cost
recovered. *Interactive*: the order-sorter (late basis lever) + the echo lever.

## 2.3 Layout

Hero (thesis + the four-sentence summary with σ badges) → spine legend (late choice /
off-switch / no-signaling strip icons) → Rooms 1–4 as full-width panels, each: primer, one SVG
viz (reusing house gauge/bars/meter idioms), its interactives, a mini-verdict row, and its
segment of the continuous no-signaling strip → The court (4 receipts): HOW WE KNOW WE'RE NOT
FOOLING OURSELVES (pre-registration, falsifiers 16-for-16, the 185b/187b amendment discipline —
letter-verdicts preserved, rule-derived fixes); WHAT "RETRO" REALLY MEANS (sifted ensembles,
never signals — Wheeler's lineage); THE TOOLKIT PLAYED BOTH SIDES (the network wing's frame
sifting/echo/merged windows built these instruments; the echo even *improved* room 4); FENCES
(one die; compiled late choices, RNG-in-the-loop named follow-up; toy universes; Clifford laws).

## 2.4 Gap review

| # | gap | fix |
|---|---|---|
| G1 | "retrocausality" misread | copy discipline: the record is re-*sorted*, never rewritten; the no-signaling strip is load-bearing in every room, with its measured spreads |
| G2 | four rooms → wall of text | each room ≤ 1 primer + 1 viz + 1 interactive; deep detail stays in findings (linked) |
| G3 | 185/187 v1 letter-fails hidden | one honest court receipt tells both amendment stories; v1 verdicts stated as NOT HELD by letter |
| G4 | mixed σ conventions confuse | every badge is "σ past a named theorem line" with the line drawn in the viz |
| G5 | echo 196% overclaim | copy separates window-share (bounded by 0.127/0.144) from background refocusing, per the finding |
| G6 | page weight | one shared JS kernel; SVGs drawn from ~40 numbers total; no images |
| G7 | a11y/mobile/theme/measured-only | house rules; all levers = buttons with aria-pressed; strips have text equivalents |

## 2.5 Pre-dev & acceptance

1. Data kernel: one `ROOMS` object pasted from the four decode JSONs (sanity asserts: witness
   crossings, off-switch values, strip spreads). 2. Spine components (strip, lever, off-switch
   button) built once, instanced 4×. 3. Rooms in order 1→4 (each reuses a proven viz idiom:
   Bell gauge / Bloch dial / needle meter / sorter gauge). 4. Court + hero last. 5. Passes:
   stub-run every lever state (≥12 combos), a11y, mobile stack, both themes, self-contained.
**Accept**: every number renders from the kernel and matches this doc's tables; all levers
work; the four off-switch/late-choice interactions produce their documented flips; no-signaling
strips show the measured spreads; index gains the two cards (Vault → network wing; Past Is Not
Fixed → new "Time" wing header with the four wing-1-style stats); museum count 34–35.

## Build order recommendation

Vault first (small, pure idiom reuse, ~1 short cycle) → Past Is Not Fixed second (the flagship,
one full cycle with the spec above as its contract).

---

# ROUND-2 GAP REVIEW (C4885) — all three plans (Vault · Past-Is-Not-Fixed · Shields), pre-build

## Cross-plan gaps found and fixed

| # | plan | gap | fix (binding for the builds) |
|---|------|-----|------------------------------|
| R2-1 | Past-Not-Fixed | the "no-signaling strip" doesn't generalize to room 2 (185 has no late choice) | rename to **the AUDIT STRIP**: per-room audit with its own measured number — R1: marginal spread 0.0191 · R2: wrong-law ratio 0.469 vs theory 0.500 · R3: invasive-vs-INRM 0.021 · R4: pinned spread 0.0162 |
| R2-2 | Past-Not-Fixed | Exp188/188b (live choices) post-date the plan — the quartet now stands on LIVE quantum coins | rooms 1 and 4 gain a **LIVE COIN badge** (184-live 23σ; 187-live echoed +20/26σ) with one-line explanations; the court's how-we-know receipt cites the coin upgrade |
| R2-3 | Vault | stream mismatch rates under-specified | derive from measured correlations: singles (1−0.028)/2 ≈ 48.6% · group 1−0.92 ≈ 8% · bellAB Bob-alone (1−0.902)/2 ≈ 4.9% (the leak!) · bellAB group ≈ 48.3%; Mermin gauge scale 0–4 with LHV line at 2 and marker 3.369 |
| R2-4 | Shields | 190's failure story risks reading as decoration | the pays-curve panel itself renders the failed flight's points (hollow markers) — the failure is IN the data view, not only the court |
| R2-5 | all three | duplicated boilerplate risk (3 pages) | shared idiom contract: identical topbar/theme/CSS base copied from relay-key (the most recent audited page); components kept file-local (museum pages stay self-contained — no shared JS file, by design) |
| R2-6 | all three | stub-run coverage | each build must stub-run EVERY selector state: Vault 3×3=9 · Shields 4 stages · PNF 4 rooms × their toggles (≥10 states) |

## Standardized pre-dev structure (applies to each build)

1. **Data kernel first**: one JS object per page, every number traceable to a decode JSON or
   dated prereg; sanity asserts inline (thrown at load in dev, removed = never — they're cheap).
2. **Component pass**: selector seg → SVG viz helpers → verdict boxes → court receipts.
3. **Copy pass**: fences and honest-ledger receipts written from the findings, not from memory.
4. **Verify pass**: extract `<script>`, stub-DOM run all states, grep-check every §2 number
   appears in the page, card added, count updated.
5. **Build order**: Vault → Shields → Past-Is-Not-Fixed (flagship last, idioms warmest).

Plans v2 complete; builds may proceed.
