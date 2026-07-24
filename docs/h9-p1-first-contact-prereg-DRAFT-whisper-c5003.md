# H9 · P1 — First Contact: the external-ready F119 sample-complexity claim (PREREG DRAFT)

*Whisper C5003, 2026-07-25, substrate claude-fable-5. H9 program P1 (Creator: "Fly P1"). Prepares
the F119 two-copy Pauli-learning advantage to survive First Contact with an external auditor — it
must clear all five gates ([P0 harness](../tools/claim_grade_harness.py)) and print its floor-type.
Builds on the extensive prior work; nothing below rebuilds it: the frozen exp142b pure-state kit
(shots=1, SPRT min-decoder, attack gate, realized-count freeze), the [F119 audit](exp142c-mixed-state-washout-honest-negative-whisper-c4999.md),
the [P3 grade](h9-p3-prime-directive-audit-whisper-c5001.md) (F119 = NEEDS-GATE, best-known-conditional),
and the [field audit](field-audit-google-learning-advantage-obstruction-elder-c6567.md).*

## ⟵⟵ FROZEN REGISTRATION — COMMITTED (Creator "Re-fly go" #1216). SEAL AUTHORIZED.

**This registration is FROZEN as of this commit.** Both court pieces are in and correct:
- **Elder** — decoder **6649628** (blind, no true-P; all-Paulis option-a; support-parity; **per-candidate
  weight-based p0**; **arm-rate distinction**: C1 single-copy arm bills (1+α)/2=0.975 ⟨P⟩, Q two-copy
  Bell arm bills (1+α²)/2=0.9512 ⟨P⟩², each vs its OWN on-device rate) + Def-2 wording verbatim.
- **Ember** — kit-confirm PASS (6649628 kit takes the α=0.95 all-Paulis 0-CZ shot-ensemble prep,
  noiseless Bell rate 0.9512 all rungs), validity-keystone confirmed, **edges PINNED** (n4/n6/n8;
  fly-those-or-re-cert-$0-at-flight-epoch).

**Whisper pre-freeze reconcile — resolved as a CONFLATION on my part (owned):** I flagged Elder's
0.475 as α/2 vs the two-copy α²/2=0.4512. Both constants are CORRECT, for DIFFERENT arms (Elder
first-principles #1230, verified n=2 P=ZZ; Ember #1229 concurs on the physics):
- **C1 classical single-copy arm** measures ⟨P⟩=α directly → rate (1+α)/2 = **0.975**, signal
  **α/2 = 0.475** (Elder's decoder constant — correct). Shot-ensemble cross-check: 0.95·1 + 0.05·½ =
  0.975 exactly.
- **Q quantum two-copy Bell arm** measures ⟨P⊗P⟩=α² → rate (1+α²)/2 = **0.9512**, signal
  **α²/2 = 0.4512** (Ember's arm — the α²-law, quadratic functional of ρ off ρ⊗ρ).

The single-copy ceiling 0.975 is HIGHER than the two-copy 0.9512 (two copies square α); "on-device ≤
noiseless" holds per-arm, 0.975 exceeds nothing — I had measured the single-copy arm against the
two-copy ceiling. **Decoder stays 6649628, no re-commit.** The brief hold was cheap; pre-freeze is
where such checks belong, and applying the "fix" (α²/2 on the C1 arm) would itself have overstated
the margin — the error it warned against, on the wrong arm.

**Blind-court invariants (hold through seal):** estimator frozen pre-reveal (decoder 6649628 committed
public before any seal); secret P held by **Ember alone**; Whisper never sees P (P-independent spec
only); the flight flies the pinned G3 edges or re-certs $0 at flight epoch.

**Spec** (C5003, all gates cleared): distribution Def 2 — ½ null (I/2ⁿ, O=uniform Pauli∖I), ½ alt
((I+0.95·sP)/2ⁿ, O=P), **P uniform over ALL Paulis∖{I}** (option (a) → floor 1/(2ⁿ+1) verbatim),
s=±1; **α=0.95** (off the authors' open α=1 boundary); **prep = 0-CZ shot-ensemble** (per shot: 0.95
random +1-eigenstate of P / 0.05 random comp-basis — verified fidelity-safe); **task** = identify-P
SPRT kit + the identify≥distinguish reduction (floor transfers); **decoder** = support-parity
(measure over each candidate P's support, not all n bits — Elder's variable-weight fix).

**Ember's three handoff riders (#1217) — folded as freeze conditions:**
1. **Validity keystone**: the public-test-P (XYZX…) G3 PASS transfers to the sealed P because the
   two-copy Bell READOUT (CX(i,n+i)+H+measure) is **P-independent**; only prep angles are P-dependent
   (same single-qubit-fidelity class). Blindness preserved — not reopened.
2. **Edge/epoch binding** (the P2 drift-census lesson): the G3 cert is bound to those Bell-pair edges
   at that calibration. **Gate B flies the same G3-certified edges OR re-runs `--predict` at flight
   epoch to re-cert ($0) BEFORE seal** if the calibration boundary moved. Ember owns `pick_layouts`;
   no silently-stale PASS.
3. **Per-n rate billing**: constraint-error 0.067→0.118→0.154 steepens the copy-vs-n slope; the
   SPRT/C1 decoder bills copies against the **per-n** on-device rate (a flat average understates n=8
   erosion). The executed margin is the per-n-billed one; the advantage rides on slope-vs-floor.

**Freeze/seal order**: (i) Elder finalizes decoder + support-parity + Def 2 wording — **✓ IN
(310932f, BLIND, committed pre-seal; Def-2 verbatim confirmed; per-n billing; all-Paulis
support-parity validated on interleaved-i.i.d. flown shape)**; (ii) Ember confirms kit takes the
α=0.95 all-Paulis prep + pins/re-certs edges — **⏳ awaiting**; (iii) Whisper commits this as FROZEN;
(iv) *only then* Ember seals (secret P) + submits blind (~240 jobs); (v) decode (Elder C1/SPRT) → court
grades. **Everything below is the derivation trail behind this block.**

## ⟵ GATE A RESOLVED (Elder #1194, primary source read verbatim; doc 10752ad) + realization verified (Whisper #1196)

**CONDITIONAL PASS — the α=1 worry was RIGHT (authors' own flagged gap), with a clean paper-endorsed fix.**

- **Q2 (access model): PASS.** Google's "conventional/no-quantum-memory" bound covers arbitrary
  *adaptive* single-copy POVMs — eq C1 uses adaptive rank-1 POVMs, App B.2 (Naimark, eq B6) reduces
  ANY general POVM (incl. ancilla-entangled) to rank-1 WLOG; only *cross-copy coherence* is
  restricted. F119's C1 single-copy benchmark sits **inside** the lower-bounded class. Not
  fixed-basis-only. **The real classical competitor is bounded.**
- **Q1 (holds AT α=1?): FAIL — authors' own open gap.** The D.4 hard instance is (I+0.9sP)/2ⁿ; the
  bound rides on 0.9²=0.81 (D38). Authors' verbatim footnote: the α=1 case (I+sP)/2ⁿ has "a technical
  difficulty… unclear whether this difficulty is fundamental." F119's (I+P)/2ⁿ **is** that open case.
  The theorem does **not** cover F119-at-α=1.
- **THE FIX (paper-endorsed, Google-precedented): fly at α=0.95, not the α=1 projector.** The theorem
  covers any constant <1 → at 0.95 the Ω(2ⁿ) floor applies directly → **theorem-over-access**. Google's
  own experiment flew α∈{−0.95, 0.95} (App A.2).
- **Realization de-risk (Whisper #1196, VERIFIED n=3 max|dev|=6e-17): α=0.95 does NOT re-wash.**
  (I+0.95P)/2ⁿ = 0.95·(uniform +1-eigenstate mixture) + 0.05·(maximally mixed) → realizable by a
  **0-CZ product-state SHOT-ENSEMBLE** (per shot: 0.95 random +1-eigenstate of P / 0.05 random
  computational-basis state). No CZ-ancilla-trace prep → the exp142c washout mechanism is avoided; the
  prep stays fidelity-safe. Only the **two-copy Bell readout** remains fragile (Ember G3).

**Task-match RESOLVED (Elder #1197 from Def 2 verbatim + Whisper #1199 verified):** the D.4 task is
distinguish/predict-|tr(Oρ)| (O revealed at prediction → that's what forces Ω(2ⁿ)), *not*
identify-among-4ⁿ. But the SPRT identify-P kit inherits the floor via a one-line reduction
(identify-P + verify ⟨P̂⟩ ⇒ a distinguisher; identify ≥ distinguish ⇒ floor transfers) — **task-type
does not change.** The one caveat that bites is the **Pauli family**: D.4's constant 1/(2ⁿ+1) is
derived over *all* Paulis∖{I} (4ⁿ−1), and the kit's **full-weight** subset (3ⁿ) does NOT inherit it —
**verified** (Whisper #1199): worst-case φ is a maximally-entangled stabilizer state (Bell → Σ_fw=3 >
(3/2)²; GHZ → Σ_fw=4 > (3/2)³), so E_fw > 1/2ⁿ. **Clean fix = option (a): draw P over all Paulis∖{I}**
→ E_P = 1/(2ⁿ+1) *exactly, φ-independent* (verified dev ~1e-16) → theorem verbatim, no re-derivation;
prep stays 0-CZ for any P (incl. low-weight), and lower average weight is *less* fragile on-device.
(Option (b) keep full-weight → floor 3ⁿ/maxΣ_fw ≈ 2ⁿ, still Ω(2ⁿ) but constant ~1.2–1.33× worse,
needs a proven maxΣ_fw bound — reserve for a secondary dramatic-ratio panel.)

**Two-copy Bell G3 — $0 core DONE, on-device confirming (Ember #1206):** the readout-extended
pre-seal gate certifies the RAW per-Bell-sample symplectic-constraint rate ⟨Q,P⟩_sp (not
decoder-success — avoids the exp142c "noise-absorbed-by-C" trap), on the frozen kit's flight
template. **The fragility worry is structurally retired**: the two-copy Bell readout is n *disjoint*
Bell-pair measurements (copy-A qubit i ↔ copy-B qubit i) that survive routing at **depth-1 all
rungs** — NOT the deep CX-star (depth 6/22/44) that washed exp142c. Noiseless self-check exact
(true-P 1.000 / wrong-P 0.50); fez noise-model forecast 0.974/0.949/0.931 vs ~0.50 → would-PASS all
rungs, margin ~0.43 ≫ 0.20 floor. On-device confirmation (3 rungs × ~2k shots) flying; PASS/FAIL to
follow. *This is why the two-copy protocol is deliverable where single-copy mixed-state prep was not:
the advantage's MEASUREMENT is shallow-parallel, not deep-weight-n.*

**G3 ON-DEVICE PASS (Ember #1211, real ibm_fez):** Bell constraint-rate 0.933/0.882/0.846 (n=4/6/8)
vs wrong ~0.49, all ≫ 0.75 floor, margins 0.36–0.43, all depth-1 (jobs d9hq11l0…/d9hq460g…/
d9hq4aog…). Prep ~0.99 + this readout ⇒ the **full two-copy protocol is fidelity-correct on
hardware**. **Every P1 technical gate is CLOSED.**

**The degraded-rate nuance — separation robust, margin reduced (Whisper structural check):** the
on-device Bell rate is ~0.85–0.93 (<1) and decays with n (readout-limited), so each sample carries
<1 clean bit. Checked whether this erodes the advantage: the quantum copy-count blowup is a
*constant-ish* factor (~1.3× at n=4 → ~2.1× at n=8, a slow readout-**linear** decay c≈0.02), NOT
exponential, while the classical floor stays Ω(2ⁿ). **So the exponential separation is robust; only
the executed finite-n MARGIN shrinks ~O(2×) at n=8** (still a large multiple, and notably below the
ideal 2417×). Exact copy-sizing billed against the 0.846 rate is Elder's SPRT lane.

**Net**: theorem-over-access F119 is reachable, flyable, and **all technical gates cleared**. Gate-set:
Q2 access ✓, Q1 α→0.95 ✓, prep 0-CZ shot-ensemble ✓, task-type reduction ✓, family → option (a)
verbatim ✓, two-copy Bell G3 on-device PASS ✓. **Only the Creator's binary spend on the ~240-job
α=0.95 re-fly remains** — it buys a theorem-floored (Ω(2ⁿ) verbatim) real exponential separation,
delivered fidelity-correct, with an executed finite-n margin reduced by readout (the claim is the
separation + floor, not a headline ratio). Alternative: hold, F119 stays best-known-conditional at no
loss. **Sections below are the pre-Gate-A framing, retained for the record; the
α=0.95 + option-(a) results supersede the α=1 / full-weight assumptions throughout.**

## Three separable things — and only two of them can build an advantage

F119's original Exp142 produced big ratios (4.9×/31.5×/266.6×/2417.5×) but was **superseded-as-
executed**. The advisor pass (C5003) forced a clean separation that the earlier framing blurred:

- **(a) The theorem** — "F119's identify-P task has a *provable* single-copy floor" (from Google
  arXiv:2112.00778 Thm 1 / App D.4). A theory note. Valid at **$0 IF it pins** (it may not — see
  Gate A). This changes what the quantum arm is compared *against*.
- **(b) A clean executed quantum measurement that beats the floor** — requires the **delivery
  re-fly** (frozen exp142b pure-state kit: shots=1 fresh-b, SPRT min-decoder, attack-gate). **~240
  jobs.** This is the measurement itself.
- **(c) The original Exp142 numbers** — **unusable.** They carry the fixed-basis-batching artifact
  the determinism attack exploits, which means the *quantum arm's own executed numbers* may be a
  classically-attackable product of the delivery, not a quantum result. Re-grounding the floor (a)
  does nothing to clean (c) — it changes the comparison target, not the contaminated measurement.

**A First-Contact advantage needs (a) + (b).** (a) alone is theory, not a win; (c) is off the table
entirely (shipping (a)+(c) would be a proven floor bolted onto contaminated numbers — better
packaging on an unusable result, and the exact band-shopping the Creator prohibited). So the spend
decision is **binary**, and I state it that way to the Creator: **either the clean re-fly (b) is
authorized, or F119 stays NEEDS-GATE and is not shipped as an advantage.** There is no $0 shortcut to
the advantage — Gate A at $0 buys the *theorem*, not the claim.

**Sequencing (kept):** Gate A first ($0) — it gates whether proposing the ~240-job spend is even
worth it. If A fails to pin, the re-fly still gives a best-known-conditional claim (weaker), and the
Creator should know that before authorizing (b).

## Gate A — does the theorem even cover our instance? ($0, Elder's seat, G-1 discipline)

**Do NOT presuppose inheritance.** The earlier framing treated "F119 is the α=1 instance of Google's
ρ∝(I+αP) family" as if the floor near-certainly carries and only the constant needs pinning. The
advisor pass flagged this as the **load-bearing uncertainty**, and the reason is specific: **α=1 is
the special, easiest case.** The states {(I+P)/2ⁿ} are *maximally* pairwise-distinguishable at α=1,
so single-copy identification may be materially *easier* there than at small α — which means Google's
exponential floor could be proven precisely in a regime (small α, weakly-distinguishable) that
**excludes** our α=1 instance. Being "the α=1 instance of the family" is exactly as likely to *escape*
the floor as to inherit it, until the source says otherwise.

**What Elder pins from the primary source** (the two discriminating questions, not just the constant):
1. **Does App D.4's bound hold AT α=1** — the fully-distinguishable case — or only asymptotically /
   for small α? (This is the make-or-break question.)
2. **Does it cover adaptive, entangled single-copy POVMs** — the strongest single-copy strategy — or
   only fixed Pauli-basis single-copy measurements? (A floor that only bounds weak measurements
   doesn't bound the real classical competitor.)
3. Then, and only if 1–2 hold: the floor's exact form (Ω(2ⁿ)? constant?) and success criterion,
   matched to our SPRT-identify-P task.

**Outcomes**: if 1 and 2 both hold → F119 floor-type = theorem-over-access (the floor covers our
instance and the strongest classical strategy). **If either fails** → F119 stays best-known-
conditional; the theorem covers a different regime than ours, and the re-fly (b) then buys a weaker
(conditional-floor) claim, not a theorem-floored one. That is the fact of the matter, and the Creator
needs it *before* deciding the spend.

## Gate B — the delivery re-fly (~240 jobs, Creator cost-call)

The frozen exp142b pure-state kit, unchanged except sizing: shots=1 fresh-b per copy (kills the
determinism attack, sim-verified #815), SPRT min-decoder (C1 = min over best-known readout-robust
decoders, Wald boundaries, realized-count-weighted CI), the **attack gate** (determinism decoder on
the flown data → chance or DELIVERY-FAIL), 3-arm court (Q / C1 / attack). Logistics: shots=1 param-
rows → ~240 small jobs at the 10k control-hardware cap (n=4: 8, n=6: 94, n=8: 138). This is the OOM
wall; the mixed-state escape that tried to collapse it **washed** (prep depth destroyed the fragile
weight-n observable), so pure-state at the job cost is the path with a fidelity-correct *prep* — with
the two-copy Bell readout still to be certified on-device (Gate 3 below).

## The five gates (P0 harness) — P1 status

1. **Floor-type**: best-known-conditional NOW → theorem-over-access IF Gate A pins (the P1 point).
2. **Instantiation**: native-shallow (pure-state = 0-CZ product eigenstates — the mixed-state's
   exp-depth-Haar problem does not arise; this is why pure-state is fidelity-correct).
3. **On-device fidelity** — **must certify the FULL two-copy protocol, not just prep.** The advantage
   is generated by the *cross-register Bell measurement across two copies*, and that sub-circuit is
   NOT 0-CZ — it is exactly the kind of fragile weight-n observable that washed the mixed-state
   delivery. Ember's pre-seal gate PASSED the single-copy *prep* (0.99/0.98/0.97, readout-limited,
   0-CZ epoch-robust), but that is **necessary, not sufficient**. G3 for P1 requires a public-test-P
   fly of prep **+ the two-copy Bell readout** that survives on-device before any seal. If the gate
   as built only certifies prep, it is incomplete for this claim and must be extended (Ember's lane).
4. **Sealed court**: yes (frozen estimator pre-reveal, Ember sealer, Elder grader).
5. **Own-hand red-team**: yes (the attack gate IS the red-team, run on the flown data).

## Gates to freeze / decision points

- ✅→ **Gate A (Elder, $0, do first)**: from the primary source, answer the two discriminating
  questions above — does the floor hold **at α=1**, and does it cover **adaptive entangled single-copy
  POVMs**. Outcome: theorem-over-access (both hold) or stays best-known-conditional (either fails).
  This gates whether the spend is even worth proposing, and at what claim-strength.
- **Gate B spend (Creator, binary)**: the delivery re-fly (b) is the ONLY path to an executed
  advantage — there is no $0 shortcut, and the original numbers (c) are unusable (artifact-
  contaminated). ~240 jobs, ~300–500s, on the batched-job orchestration the P2 arc showed is fragile.
  Scope sub-options *within* authorizing (b): full n=4/6/8 (a slope with a CI), or n=4/6 (~102 jobs,
  2-point growth, no slope CI). **The decision is: authorize (b), or F119 stays NEEDS-GATE.**
- **G3 extension (Ember)**: extend the pre-seal gate to certify the **two-copy Bell readout**, not
  just prep, on a public test-P at the flight epoch. Mandatory before seal.
- **Build/submit**: I provide the P-independent scaffold + K1–K7; Ember injects the secret + submits
  blind (the exp142b division).

## Recommendation

**Do Gate A now ($0)** — but as a *test of whether the theorem covers our instance*, not a formality
expected to pass. The α=1 special-case concern is real and could leave F119 best-known-conditional.
**Report Gate A's result to the Creator, then let them make the binary (b) spend call** with the true
claim-strength in hand:
- If Gate A pins → the re-fly buys a **theorem-over-access** F119 (potentially EXTERNAL-READY) — the
  strongest outcome, worth the 240 jobs.
- If Gate A fails → the re-fly buys a **best-known-conditional** F119 (ADVANTAGE-CONDITIONAL) — still
  a real clean measurement, but a weaker claim; the Creator may reasonably defer the spend.

Either way, **I will not present "theorem-upgrade likely + we can skip the re-fly"** — neither half is
established, and the skip-path (shipping the contaminated original numbers) is off the table.

---

*Draft ends. Gate A is Elder's $0 primary-source pin (a genuine test, not a rubber stamp); Gate B is
the Creator's binary cost-call for the only path to an executed advantage; the two-copy G3 extension
is Ember's mandatory check. No QPU spent by this document. First Contact = the F119 claim graded by
all five gates before it ever meets an outside auditor — including the gate that asks whether the
theorem we want to lean on actually reaches us.*
