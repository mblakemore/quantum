# Accuracy-correction table — the five Creator-directed adversarial audits (Whisper C4718)

**Directive** (Creator, 2026-07-14): *"go back through the results of the 5 adversarial runs and update any repo docs and demos for accuracy enhancement — refactor structure as needed rather than note append."*

This is the canonical spec for that sweep. Each row folds the audit's correction **into** the claim
sentence so the accurate statement *is* the claim — not a caveat bolted onto an over-claim. The five
audits (C4713–C4717) are the source of record; this table is what every reader-facing doc and demo is
edited to match.

**The one discipline that governs every row** (all five audits warned of it): the failure mode in a bulk
accuracy pass is the **inverse over-claim** — swinging past "accurate" into *understating* a real win.
Every correction below is **win + precise scope**, never a retraction. The σ's are correct arithmetic;
what each row fixes is *what the number is silently compared to* or *what the prose imports that the
number doesn't carry*. An edit that reads as walking the win back is wrong.

**Scope of the sweep**: presentation/reader-facing layer — `README.md`, root `index.html`,
`ELI5_SUMMARY.md`, the reckoning doc (`docs/quantum-advantage-audit-whisper-c4666.md`),
`docs/quantum-advantage-the-complete-answer-whisper-c4682.md`, and the public demos. Raw data tables,
scoreboards' numeric cells, pre-registration files, and experiment-results records keep their computed
numbers unchanged — a correctly-computed 216.8σ *is* 216.8σ of shot-noise precision; only the **framing
prose** that presents it as the significance of the physical claim is re-voiced. Historical planning docs
and other findings' files are left as timestamped record.

---

## F82 — causal-order game "216.8σ" (audit C4714)

- **WIN (preserve):** the quantum switch beats the causally-separable bound 0.869 → **0.9769**, replicated
  **0.9738** on a second chip; the SDP bound and the executed fixed-order null (0.615) are load-bearing
  safeguards; indefinite causal order is genuinely certified.
- **Over-claim:** headlining **216.8σ** as the significance of the physical claim.
- **Canonical phrasing:** "beats the causally-separable bound 0.869 → 0.9769, **replicated 0.9738 on a
  second chip (0.3 pp two-chip concordance, ~34σ run-to-run)** — the **216.8σ is within-run shot-noise
  precision, not the significance of beating the bound**; the binding limit is the disclosed
  device-characterized scope." Keep the σ; pair it with the concordance and frame it as precision.
- **Do NOT:** downgrade to a single "honest ~3σ" — that self-check was itself refuted (advisor-caught) and
  is a fresh over-claim.

## F108 — GHZ metrology "168σ / the advantage industry buys" (audit C4716)

- **WIN (preserve):** an N=3 entangled probe carries **2.848× the phase Fisher information** of the best
  separable strategy, measured against an *executed* SQL reference on the same 3 qubits (168σ), beating
  even perfect separable probes (239.5σ); scaling persists to N=5. Clean win — right number, fair
  reference, honest resource accounting.
- **Over-claim:** "**the advantage the sensing industry actually buys**" — imports a global deployment
  claim the local Fisher number doesn't carry.
- **Canonical phrasing:** "a certified **N=3 *local* Fisher-information advantage**. The *deployment*
  version (frequency standards, unambiguous absolute phase) pays two further tolls the local number
  doesn't: the k=3 super-resolution that certifies the win is also a **3-fold phase ambiguity** (absolute
  phase needs a Higgins-2007 cascade), and under *time-optimized* interrogation with dephasing (the
  F111-measured regime) the *scaling* advantage is **Huelga–Plenio-limited** — HP bites the
  frequency-standard framing, not the N=3 phase result." Front-door surgery only; the gates stand.

## F94 — ICO engine "THE ENGINE EXISTS" (audit C4717)

- **WIN (preserve):** certified population inversion **p₁|₋ = 0.5509 (+10.6σ)**, both baths passive at 5σ,
  the plus/minus asymmetry as the switch signature, the premise gate that had just refused a +23σ fake,
  and the **per-run-honest** ergotropy 0.0378 E/run; beats the definite-order/mixture bound (F86 witness=0).
- **Over-claim:** "**THE ENGINE EXISTS**" and "**conjured from causal structure … out of baths that can
  power nothing**" — mislocates the fuel; the ledger is reported on one side only.
- **Canonical phrasing:** "a **certified working resource** — a population inversion the passive baths
  alone cannot reach, **routed** from control-coherence + demon-information through the switch (**a router,
  not a battery**). **Pre-ledger:** the pre-registered demon-ledger work column (control-coherence
  preparation + Landauer erasure of the heralding record) is **not yet computed**, so this is a certified
  working resource, **not a closed engine cycle**." Keep "baths individually powerless" (true, certified);
  drop "conjured from structure" (unpriced). Fence "engine" to F95's full-cycle ledger.

## F113 — shallow BGK solver "provably can't / 438σ" (audit C4715)

- **WIN (preserve):** a **constant-depth** quantum circuit executes the 2D-HLF solver on silicon at
  **P(valid) = 0.9017**, covering the whole solution coset near-uniformly (a fixed-output classical mimic
  fails this W3 gate), 10 routed CZ, O(1) depth — the on-chip *apparatus* of the one theorem (BGK-2018)
  that separates shallow quantum from shallow classical.
- **Over-claim:** "a shallow quantum circuit solves a problem shallow classical circuits **provably
  can't**" (the bound is *asymptotic*; at n=4 a constant-depth classical circuit *can* solve it);
  **437.8σ** read as a beaten classical bound (it is fidelity over the uniform-random floor 0.25);
  contextuality "**CONFIRMED-by-composition / closed end-to-end**."
- **Canonical phrasing:** "executes, on silicon, the solver of the one theorem that *provably* separates
  shallow quantum from shallow classical **as n grows** — at the fixed n=4 flown, a constant-depth
  classical circuit can also solve the instance (the Ω(log n) bound is asymptotic). The **90.2% /
  437.8σ is fidelity over the uniform-random floor 0.25, not a beaten classical bound**; the advantage is
  **theorem-carried**, the apparatus is what runs on-chip. The contextuality link is **theory-associated**
  (the BGK-2018 solver flew; the magic-square / BGKT-2020 gadget did not)." The "as n grows" is
  load-bearing and must not drop from the headline.
- **Do NOT:** downgrade to "just random-beating" — the inverse over-claim; the constant-depth apparatus is
  a genuine milestone.

## F117 — 1SDI randomness certificate "0.65 bits at 5σ" (audit C4713)

- **WIN (preserve):** **0.65 private random bits per use** from measured assemblage data run through an
  *exact* SDP (no Werner model), clearing the min-entropy floor — the second clean firing of the
  hardware-anchored discipline (after F113). The floor itself is robust.
- **Over-claim:** presenting **±0.0063** as the whole uncertainty; "**5σ**" as the honest limiting factor;
  "beats the model" at the full 0.027 gap.
- **Canonical phrasing:** "**0.65 private random bits per use** (bias-disclosed: the certificate carries a
  **+0.006 method bias ≈ 1 SE that the bootstrap does not see** — the honest signal is ~0.676 net of a
  systematic the method doesn't quantify, and *that bias*, not the ~100σ statistical margin, is the
  limiting factor). 'Beats the model' is **real but ~22% smaller** than the headline gap (~0.021 signal
  vs the claimed 0.027)." The MC models only tomographic bias from an isotropic truth, so +0.006 is a
  *lower bound* on the true bias — the honest error bar is wider than reported, in a direction the grader
  can't detect. The bits are certified; the uncertainty is disclosed.

---

## Meta — five audits, five distinct failure classes (the structural through-line)

The campaign's big numbers are sound **arithmetic**; the recurring risk is **what each number is silently
compared to, or what the prose imports that the number doesn't carry**:

1. **F117 — wrong uncertainty** (a systematic bias the method doesn't quantify).
2. **F82 — precision ≠ significance** (a correct σ answering a narrower question via a conservative floor).
3. **F113 — strawman null + headline outrunning its own scope fence** (σ over a weak floor; asymptotic
   bound cited as if it binds at n=4).
4. **F108 — framing over-reach of *kind*** (local Fisher number, global deployment prose) — the mildest.
5. **F94 — one-sided ledger / fuel mislocation** (a working resource certified pre-ledger, prose presumes
   the ledger closes).

Two of the five (F108, F94) are **clean wins at the number level** — the correction is entirely in the
front-door prose. None of the five is a broken finding. The through-line the sweep enforces: **the win is
the win; the scope is the scope; neither is inflated to match the other.**
