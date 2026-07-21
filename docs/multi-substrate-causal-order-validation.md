# Multi-Substrate Validation of Indefinite Causal Order: The Quantum Switch Certified Across Three Superconducting Dies, Two Vendors, and a Trapped-Ion Processor

**An empirical white paper from an autonomous multi-agent characterization campaign.**
Substrate of authorship: `claude-opus-4-8` (v1, C4941); revised `claude-fable-5` (C4946, restoration).
Whisper (DC15W), 2026-07-21. All results are measured quantum hardware; every number traces to an IBM
Quantum job ID or an Amazon Braket quantum-task ARN (see §8, Data Availability). This document is the
repo-native publication; it makes no external submission.

---

> ## CORRECTION HISTORY (C4942 → C4946) — withdrawal, root cause, certified restoration
> **This paper's IonQ claim was withdrawn and later restored. The full arc stays here on purpose.**
>
> **C4942 — WITHDRAWN.** An external review (Gemini, relayed by the Creator) pressed on the weakest link:
> the IonQ result used a $16 semantic-smoke port check instead of a downstream definite-order null. The
> proper null (Exp211b) was flown and **FAILED as instrumented** (W_definite read +1.96, not ≈0), a
> known-input CX calibration appeared to rule out endianness, and the certification was withdrawn per
> pre-commitment.
>
> **C4943-45 — ROOT CAUSE.** Re-analysis of the recorded counts' ungraded target bit, exact offline
> reproduction of the client compile, and the raw device payloads localized the failure to a
> **client-library decode bug**: qiskit-braket-provider 0.18.1's *program-set* result branch returns
> counts keyed in raw Braket qubit order, omitting the little-endian reversal its single-task branch
> applies (its own `memory` field reverses; `counts` does not). Every multi-circuit (program-set) flight
> in this campaign decoded bit-swapped; every single-circuit calibration decoded correctly — which is
> exactly why the C4942 calibration failed to catch it. The structurally-matched null flown as **Exp212**
> reproduced the swap signature; its raw payload shows a **physically perfect null collapse**.
>
> **C4946 — CERTIFIED + RESTORED.** A pre-registered **known-input program-set calibration** (two
> opposite-outcome known inputs, entangled + gate-free, flown through the exact indicted path) returned
> both keys **unreversed** (0.99/1.00) → the decode correction is certified by paid ground truth. Under
> the certified correction and the unchanged frozen bands: Exp212 matched null W_matched = **−0.09**
> (all marginals pass), same-window witness W = **+1.91** (13.5σ), separation 2.0 (11.6σ) →
> **LOOPHOLE-CLOSED(restore)**. Exp211b regrades **NULL-CLOSED** (W_def = 0.00 — the null that triggered
> the withdrawal was always clean). The IonQ device is exonerated entirely; it executed every circuit
> correctly. The Rigetti numbers in this paper are the corrected decode (they *improved*: W 1.114 →
> 1.2165). See §6b for the incident report and `experiments/braket-exp212-*` for pre-registrations,
> frozen reading rules, and prediction grading (including the misses).

---

## Abstract

The quantum switch places the *order* of two operations into coherent superposition — a process with **indefinite causal order (ICO)** that no definite-order (causally separable) process can reproduce. Prior hardware demonstrations, including the earlier phases of this campaign, established ICO on a single family of superconducting processors (IBM Heron). A natural skeptical question remains: *is ICO a genuine property of quantum mechanics, or an artifact of one hardware technology?* We answer it empirically by transporting a **frozen, pre-registered causal-order instrument** — the same circuits, graded against the **same theory-fixed bounds, with no retuning** — across the deepest hardware divide available to us. The causal witness **W** (ideal 2.0; causally-separable bound 0) certifies on **three IBM Heron dies** (W = 1.89–1.95), on a **different-vendor superconducting chip** (Rigetti Cepheus-1-108Q, W = 1.2165, 54.4σ over the bound, full three-number PASS-CAUSAL), and on a **trapped-ion processor** (IonQ Forte-1, same-window witness W = 1.910 ± 0.141 at 13.5σ **with a structurally-matched, validated definite-order null** W_matched = −0.09; corroborated by an earlier 500-shot witness at W = 1.892, 29.9σ). Trapped ions store each qubit in a single atom, use all-to-all connectivity and GPI/GPI2/RZZ native gates, and carry **none of the CZ Z-biased dephasing** on which the superconducting devices' error budget is dominated — yet ICO fires there at essentially the same strength as on tuned Heron, and collapses to zero there the moment the control's coin is made classical. Across three physically distinct substrates from three vendors, the witness strength **does not cluster by modality**: the two highest-contrast chips (Heron and IonQ) sit on *opposite* modalities, while a third superconducting chip (Rigetti) separates below — consistent with ICO being a quantum resource whose *observed* magnitude is attenuated by each device's **total, depth-integrated error budget** rather than by its qubit technology or its per-entangling-gate error. We conclude that indefinite causal order is substrate-general. We are explicit about the asymmetry of evidence (Heron: full three-axis bench; Rigetti: full causal axis; IonQ: witness + matched definite-order null, no capacity/null-integrity arms), about a client-library decode bug this campaign found, certified, and corrected along the way (§6b), and about what the result is and is not.

---

## 1. Introduction

In everyday physics and in all of classical probability, two events occur in *some* order, even if we are ignorant of which. A **quantum switch** breaks this: a control qubit coherently superposes "operation A then B" with "B then A," producing a process whose causal order is genuinely indefinite rather than merely unknown. A single measurement — a **causal witness** — can certify that no fixed order, and no classical mixture of orders (a "causally separable" process), could reproduce the observed statistics [1,2].

The quantum switch is a theorists' construction; photonic laboratories demonstrated it first, and gate-model versions have since run on superconducting chips, including in the earlier phases of the campaign that produced this paper. What that earlier work contributed was not the switch itself but a **scoreboard**: pre-registered games and channels whose limits are provable theorems for any definite-order process, beaten on silicon and reported with the losses kept beside the wins.

This paper addresses the sharpest remaining objection to any single-platform ICO demonstration: **that the effect could be a hardware artifact** — a quirk of a particular chip, a particular vendor, or a particular qubit technology. We attack the objection the way one attacks any universality claim: by holding the experiment fixed and changing the substrate as radically as possible. Concretely, we take a **frozen instrument** — the exact witness circuits and the exact theory-fixed grading bounds used on IBM Heron — and run it, without retuning, on (i) two *additional* Heron dies, (ii) a superconducting chip from a *different vendor* (Rigetti), and (iii) a *trapped-ion* processor (IonQ) whose physics has almost nothing in common with a superconducting transmon. If the witness fires against the same bound on all of them, the artifact hypothesis fails at every level at which it could be stated.

---

## 2. Background: the causal witness

The instrument is the campaign's `switch_bench` causal axis. Its central observable is the **witness disc**

  **W = ⟨X_c⟩_comm − ⟨X_c⟩_anti**,

the difference between a control-qubit expectation measured under a "commuting" arm and an "anti-commuting" arm of the switch. The relevant reference values are theory constants, identical on every device:

- **Ideal (fully coherent switch): W = 2.0.**
- **Causally-separable bound: W = 0.** Any definite-order process, or classical mixture of orders, yields W ≤ 0 for this witness; W > 0 (at statistical significance) certifies indefinite causal order.

The certification rule used throughout is **W − 5·seW > 0**, i.e. the measured witness must clear the causally-separable bound by five standard errors. This bound is a *theory constant*; it is never fit to a device. (The campaign's original Heron certification also included a discrimination-*game* form — a causal game with a causally-separable ceiling of 0.8695, won at p̂ = 0.9769 ± 0.0005 and replicated at 0.9738 on a second die — but the witness W is the observable common to all three substrates in this paper, so we report it throughout.)

---

## 3. Methods

### 3.1 The frozen instrument
The witness circuits are generated by `tools/switch_bench.py::build_causal()` and are byte-for-byte identical on every device. On IBM Heron the full three-axis bench (CAUSAL / SCHEDULE / HOLD) was flown; the CAUSAL axis additionally reports a channel-**capacity** signal R̄ (ideal 0.5333, causal 0) and a null-integrity control D. The grading — theory constants plus the fixed pass rules — is inherited unchanged across platforms.

### 3.2 Pre-registration
Every flight was pre-registered before submission: the circuits, the bounds, the pass rules, the shot budget, and a pre-filed prediction (including a named failure mode) were frozen in a committed document *before* any data was seen. Pre-registration files and their git commit hashes are cited in §8.

### 3.3 Cross-platform porting (Braket)
The non-IBM devices were reached through Amazon Braket via `qiskit-braket-provider`. The IBM qiskit circuit is submitted with `backend.run(native=True)`, which compiles the abstract circuit to the device's own native, angle-restricted gate set inside a verbatim box: Rigetti → Rx/Rz/CZ; IonQ → GPI/GPI2/RZZ. Measurement counts are read through qiskit's `get_counts()`, preserving the classical-bit convention. A local-simulator validation reproduced the ideal witness (W = 2.0000) through the full port before any hardware spend.

### 3.4 Cost-frugality, the null controversy, and the matched null
IonQ bills $0.08/shot; the full frozen axis (68 pubs, 112k shots) would cost ~$9,000 there, so the first IonQ flight (Exp211) was **witness-only** at reduced shots, guarded by a **semantic smoke check** (~$16.60) in place of a downstream null arm. External review correctly identified that substitution as the weakest link; the campaign then flew the proper definite-order control in three stages: (i) a gate-free `definite=True` null (Exp211b) whose *instrumented* failure triggered a withdrawal and ultimately exposed a client-library decode bug (§6b); (ii) a **structurally-matched null** (Exp212) — the witness circuit itself with only the control preparation changed from |+⟩ to a classical |0⟩/|1⟩ mixture, keeping all four entangling gates, so it shares the witness's compilation path exactly; and (iii) a **known-input program-set calibration** that certified the decode correction with paid ground truth. The matched null flew **in the same submission batch as a witness re-fly** (same-window), and its grading pre-registered *every* classical bit: deterministic target marginals per arm, ~50/50 control marginals, per-preparation bands, and the mixture band. Task handles were persisted before blocking on results throughout, so a long queue could never orphan a paid job.

### 3.5 Shot budgets
Heron and Rigetti witness pubs used 4,000 shots (seW = 0.0224). The IonQ Exp211 witness used 500 shots (seW = 0.0632) and the Exp212 same-window witness/null pubs 100 shots (seW = 0.1414) as cost choices; fewer shots **widen** the error bar and make the 5σ bar *harder* — they do not retune the bound.

---

## 4. Results

### 4.1 IBM Heron — three superconducting dies (full three-axis bench, F112)
The full bench was flown intact on three Heron-r2 dies against the same frozen bounds, no retuning. The CAUSAL axis:

| die | W (witness) | R̄ (capacity) | verdict |
|---|---|---|---|
| `ibm_kingston` | **1.9533 ± 0.0224** | 0.5245 | PASS-CAUSAL |
| `ibm_marrakesh` (home) | 1.9265 | 0.4978 | PASS-CAUSAL |
| `ibm_fez` | 1.8948 ± 0.0224 | 0.5080 | PASS-CAUSAL |

(Canonical-value note: `marrakesh` W is the decode value **1.9265**; the F112 finding card rounds it to 1.90. Both refer to the same measurement.) All three certify; the bench even **ranks** them on axes standard vendor metrics (QV/CLOPS/EPLG) do not touch (kingston ≥ marrakesh ≥ fez). ICO is a property of the Heron *generation*, not one lucky die.

### 4.2 Rigetti Cepheus-1-108Q — cross-vendor superconducting (full causal axis, Exp210)
The full causal axis (68 pubs, 112k shots) was flown on a non-IBM superconducting chip via Braket:

| quantity | value (certified corrected decode, §6b) | bound / rule | verdict |
|---|---|---|---|
| W (witness) | **+1.2165 ± 0.0224** | W − 5·seW > 0 (54.4σ over 0) | **PASS** |
| R̄ (capacity) | +0.2873 ± 0.0093 | > 0.10 (20.1σ) | **PASS** |
| D (null integrity) | −0.0039 | \|D\|+5·seD < 0.10 | clean |

**Verdict: PASS-CAUSAL** — the full three-number card, against the identical frozen bounds. (v1 of this paper reported W = 1.1138, R̄ = 0.2712, D = +0.0169 through the decode bug of §6b; the certified correction *raises* Rigetti by ~9% and makes its null even cleaner. PASS-CAUSAL holds under both decodes.) Rigetti remains a markedly *weaker* causal chip than Heron (W 1.22 vs ~1.90 — ~63% of Heron's witness). Importantly, the attenuation is **not** at the entangling gate: Rigetti's per-CZ error is ~0.003, *IBM-parity*. The low W is bought by the **rest of the depth-integrated budget** (readout, T2, single-qubit gates) accumulated over the witness circuit — precisely the campaign's own C4937 finding that comparable single-CZ error does *not* predict witness fidelity. It certifies unambiguously. This established cross-*vendor* device-independence: ICO is not a property of one company's fabrication.

### 4.3 IonQ Forte-1 — cross-modality trapped ion (witness + matched definite-order null, Exp211/212)
Trapped ions store each qubit in a single atom, provide all-to-all connectivity, and use GPI/GPI2/RZZ native gates with no CZ-biased dephasing. The certified IonQ result is the **Exp212 same-window pair** (all numbers under the §6b-certified decode):

| quantity (Exp212, one submission batch, 100 shots/pub) | value | rule | verdict |
|---|---|---|---|
| W (witness, same window) | **+1.9100 ± 0.1414** (13.5σ) | W ≥ 1.3 AND W − 5·seW > 0 | **FIRED** |
| W_matched (structurally-matched definite-order null) | **−0.0900 ± 0.0995** | \|W\| ≤ 0.3, per-prep \|W_D0\|,\|W_D1\| ≤ 0.3 | **CLOSED** |
| null all-bit marginals (8 checks) | targets 95–100% ideal, controls 41–52% | t ≥ 0.85; c ∈ [0.30,0.70] | all PASS |
| separation | **+2.0000 ± 0.1729** (11.6σ) | > 1.0 | PASS |

The matched null is the witness circuit itself — same four entangling gates, same depth, same compilation path — with only the control preparation changed from |+⟩ to a classical |0⟩/|1⟩ mixture. A classical mixture of definite orders is causally separable, so W_matched ≤ 0 is a theorem; measured, it collapses to −0.09 while the witness in the same window reads +1.91. **The switch's signal on trapped ions is carried by the control's quantum coin, and by nothing else.**

Corroboration: the earlier Exp211 witness (4 pubs, 500 shots) reads **W = +1.8920 ± 0.0632** (29.9σ) under the certified decode (its arms: comm +0.944/+0.952, anti −0.952/−0.940 — palindrome-dominated outcomes, hence decode-robust to within 0.002 of the v1 value). The Exp211b gate-free null regrades **NULL-CLOSED** (W_def = 0.00). The pre-committed Exp212 reading rule resolves to its restore branch with every band met.

### 4.4 The three-substrate comparison

| substrate | modality / connectivity | native 2-qubit gate | chip | W | scope flown |
|---|---|---|---|---|---|
| IBM Heron | superconducting, heavy-hex | CZ (Z-biased) | kingston/marrakesh/fez | 1.89–1.95 | full 3-axis bench |
| Rigetti | superconducting, limited | CZ | Cepheus-1-108Q | 1.2165 (54.4σ) | full causal axis (PASS-CAUSAL) |
| **IonQ** | **trapped ion, all-to-all** | **RZZ (no Z-bias)** | **Forte-1** | **1.910 (13.5σ); corrob. 1.892 (29.9σ)** | witness + matched null (same window) |

The trapped-ion chip **matches tuned Heron and far exceeds Rigetti.** The ordering of witness strengths is Heron ≈ IonQ ≫ Rigetti — which does **not** follow modality (the two extremes, IonQ and Rigetti, are on opposite modalities). It follows device fidelity.

---

## 5. Discussion

**Indefinite causal order is substrate-general.** The witness fires against the same theory-fixed bound on superconducting transmons (two vendors, heavy-hex and otherwise) and on trapped ions — a hardware divide about as wide as the gate-model era offers. The artifact hypothesis, in each form it can take, fails: it is not one lucky die (three Heron chips), not one vendor (Rigetti), and not one qubit technology (IonQ).

**The witness does not cluster by modality.** IonQ (trapped ion) and Heron (superconducting) both land near W ≈ 1.9, while Rigetti (also superconducting) sits at 1.22. If the witness value were a signature of the *modality*, the two superconducting chips would cluster and the ion would be the outlier; instead the two high-contrast chips cluster **across** the modality boundary and the lower-contrast superconducting chip separates. Two cautions govern how far this can be pushed:

- **"Fidelity" must mean the depth-integrated budget, not the entangling-gate error.** Rigetti's per-CZ error is IBM-parity (~0.003), so its low W is *not* an entangling-gate deficit; it is bought by the rest of the circuit's budget (readout, T2, single-qubit gates). This campaign measured directly (C4937) that comparable single-CZ error does not predict witness fidelity — so the ordering here is by total accumulated error, which is the honest sense in which "fidelity, not modality" holds.
- **N = 1 trapped-ion device.** With one ion chip we can show the witness **does not cluster by modality** across these three devices; we cannot establish that it *tracks* fidelity as a law. One modality-linked confound we do not fully exclude: IonQ's all-to-all connectivity removes routing error — a genuine modality feature. Here it is small (an adjacent-pair, 2-qubit witness, with the best CZ edge pinned on Rigetti so no SWAPs are incurred), but it is not zero.

With those cautions, the pattern is the expected behavior if ICO is a genuine quantum-mechanical resource whose *observed* magnitude is attenuated by each device's total error budget — and it is evidence against a modality-specific mechanism (e.g. one keyed to superconducting CZ dephasing).

**The trapped-ion result is not merely a repeat.** IonQ's error physics shares essentially nothing with a transmon: no charge qubits, no flux-tunable couplers, no CZ, no heavy-hex routing overhead, all-to-all connectivity. That the witness fires *cleanly* there — at ~95–97% single-arm contrast (⟨X_c⟩ ≈ 0.94–0.95) on individual atoms — is the strongest device-independence statement the campaign can make short of a full multi-axis card on every platform.

---

## 6. Limitations and scope (stated plainly)

1. **Asymmetry of evidence.** The three substrates were measured to different depths. Heron carries the *full three-axis bench*; Rigetti carries the *full causal axis* (witness + capacity + null → PASS-CAUSAL); IonQ carries the **witness plus a structurally-matched definite-order null** (same window). On IonQ the capacity (R̄) and full null-integrity (D) arms were **not** flown — the full frozen axis is ~$9k on ions and was outside budget. The IonQ claim is therefore narrower than Rigetti's: *the witness fires and its matched definite-order control collapses*, not the three-number certification.
2. **The decode-bug incident (§6b).** The IonQ null validation initially *failed as instrumented*, the certification was withdrawn, and restoration required diagnosing and ground-truth-certifying a client-library decode bug. The full arc — including two graded prediction misses along the way — is part of this paper's record; the certified correction is version-pinned in the runner and hard-fails on any un-recertified provider upgrade.
3. **Not a loophole-free test.** These are within-chip certifications against a *causally-separable* theoretical bound, executed under an experimenter-trusted apparatus. They are not device-independent Bell-type tests with closed detection/locality loopholes; the switch's own scope work in this campaign includes a retracted query-complexity claim (F80) marking the honest boundary of what a witness supports.
4. **Same-instrument, not same-instant.** Each device was measured in a single window; the cross-platform agreement is that the same frozen instrument certifies on each, not that they were run simultaneously or share entanglement. No cross-QPU entanglement is implied (Braket does not provide it).
5. **Shot-budget difference.** IonQ used 500 shots/pub (Exp211) and 100 shots/pub (Exp212) vs 4,000 on Heron/Rigetti, widening its error bars (seW 0.063 / 0.141 vs 0.022). This makes the bar harder, not easier, but the IonQ W values are lower-shot estimates.
6. **Single die per non-IBM platform.** One Rigetti chip and one IonQ chip; the Heron generation has three. Cross-*generation* IBM hardware (Eagle) was unavailable and is not claimed.

None of these limitations touches the central claim, which is deliberately modest and robust: **the causal witness clears the causally-separable bound on all three substrates, against identical theory-fixed thresholds — and on the trapped-ion platform, its structurally-matched classical control collapses to zero in the same window.**

---

## 6b. The decode-bug incident (C4941–C4946): an instrument failure, found and certified

The campaign's own record of this incident is a result in its own right, so it is summarized here rather than hidden.

1. **The artifact.** `qiskit-braket-provider` 0.18.1 returns counts for **program-set** submissions (multi-circuit batches — one quantum task, several executables) keyed in **raw Braket qubit order**, omitting the `[::-1]` little-endian reversal its single-task path applies. (The program-set branch's own `memory` field *does* reverse; `counts` does not.) Every multi-circuit flight in this campaign — the Exp210 Rigetti axis, the Exp211 IonQ witness, the Exp211b null, the Exp212 batch — decoded with the two classical bits swapped; every single-circuit calibration decoded correctly.
2. **Why it survived three certifications.** The witness's dominant outcomes ('00'/'11') are **palindromes** — invisible to a bit swap — so witness values were essentially unaffected (Exp211: 1.894 → 1.892). Rigetti's full axis *passed* under both decodes (the corrected numbers are ~9% better). The bug only became visible when a circuit with a deterministic *asymmetric* outcome (the definite-order null) flew in a program set — and then it mimicked a maximal physics failure (W_def = +1.96).
3. **The diagnosis chain, all free until the last step**: the ungraded target bit of the recorded 211b counts (theory demands '10'; recorded '01'); exact offline reproduction of the client compile (faithful — client exonerated); raw device payloads (physically perfect nulls); a 2×2 confound break across gate-content × submission-path; provider source inspection (the line-exact omission); and finally a **$16.60 known-input program-set calibration** (entangled known `'01'` read `'10'` at 0.99; gate-free known `'10'` read `'01'` at 1.00) certifying the correction with paid ground truth in the exact path.
4. **Governance.** The as-instrumented Exp212 verdict (NULL-FAIL) was recorded and predictions graded as misses *before* any correction was applied; restoration was executed only through a pre-registered reading rule gated on the known-input calibration, under an explicitly raised budget cap. The correction in the runner is version-pinned and hard-fails on un-recertified provider versions. The device vendors are owed the exoneration explicitly: **nothing was ever wrong with any QPU in this campaign** — IonQ executed every circuit, including both "failed" nulls, correctly.

---

## 7. Conclusion

Holding a pre-registered causal-order instrument fixed and changing the substrate from IBM superconducting transmons, to a different vendor's superconducting transmons, to individual trapped ions, the causal witness certifies indefinite causal order on every one — at a strength that **does not cluster by qubit technology** (the two highest-contrast chips sit on opposite modalities), consistent with attenuation by each device's total, depth-integrated error budget. On the trapped-ion platform the certification now carries its sharpest internal control: make the switch's control coin classical while changing nothing else, and the witness collapses from +1.91 to −0.09 in the same session. Cause and effect held in coherent superposition is not an artifact of a chip, a vendor, a modality — or, after §6b, a decoder. It is, to the reach of these instruments, a property of quantum mechanics — and it now has hardware receipts on three physically distinct substrates, for a total additional expenditure of ~$320 in cloud QPU time.

---

## 8. Data availability

- **IBM Heron (F112, three dies)**: `ibm_kingston` job `d9amd73v6alc73cs0lp0` (77 pubs, 208k shots); `ibm_fez` job `d9b9fvvu62qs738ov860`; `ibm_marrakesh` reference die. Finding: `findings/F112-*.md`.
- **Rigetti Cepheus-1-108Q (Exp210)**: Braket quantum-tasks `c5d0e765-a867-4bcc-becf-3db9b0409c37`, `4196545e-6c75-4b39-a313-8ba766b45e7b`. Pre-reg `experiments/braket-exp210-rigetti-cross-platform-causal-preregistration.md` (commit ab88b32); results `...RESULTS.md`.
- **IonQ Forte-1 (Exp211)**: witness quantum-task `b479e273-d4f9-4ab3-9833-ed3188c51b40`; semantic-smoke quantum-task `37c301c0-95a2-4d31-9b17-7734dc56a52f`. Pre-reg `experiments/braket-exp211-ionq-cross-modality-witness-preregistration.md` (commit cb9ca44); results `...RESULTS.md`.
- **IonQ Forte-1 (null-validation & decode-bug arc, Exp211b–212)**: gate-free null `ca68e121-605b-49eb-92e9-eddc6ec30c7b` (Exp211b, regraded NULL-CLOSED); CX bit-order cal `6750e981-914e-4f09-ae0b-5c89fd28e929` (C4942); Exp212 same-window witness+matched-null batch `29012b69-51bf-424f-99ba-be06f666bc0e`; gate-free cal `9e7acae7-1c4f-404e-9160-6125c45ffacc`; known-input program-set cal `675bf4b2-96b6-4222-99ff-c380fec70a30` (decode-bug certification). Pre-reg + frozen reading rules `experiments/braket-exp212-ionq-matched-null-preregistration.md` (commits 3cfea9c, 12ad868); results + incident report `experiments/braket-exp212-ionq-matched-null-RESULTS.md`. Corrected cards: `results/braket_causal_ionq_matched_CORRECTED.json`, `results/braket_causal_rigetti_CORRECTED.json`.
- **Instrument & runner**: `tools/switch_bench.py` (circuits + grader); `scripts/braket_switch_causal.py` (Braket port; witness/smoke/matched-null modes; version-pinned program-set decode correction `_programset_key_fix`). No credentials are stored in the repository.

## 9. References (selected)
1. G. Chiribella et al., "Quantum computations without definite causal structure" (the quantum switch).
2. M. Araújo et al., "Witnessing causal nonseparability" (the causal witness and causally-separable bound).
3. This campaign: `README.md` (headline results), `docs/beyond-the-ladder.md` (the causal-inference argument), `docs/quantum-advantage-audit-*.md` (wins and non-wins with their currency stated).

*Prepared as a repo-native publication. Corrections and adversarial review are logged in the campaign's finding record.*
