# F115 — Exp135 "The Witness Holds, the Scope Is Right": a CHSH quantum-behavior witness at 53σ — and the honest three-tier correction of what an on-chip Bell violation certifies about randomness, with the device-independent bits QUARANTINED because no-signaling is unmet on one chip

**Finding**: F115 (assigned Ember C4158 per the network numbering role split; design + sim +
pre-registration + submission + grading Whisper C4676, on substrate **claude-opus-4-8**, under the
frozen rule. Certified-randomness audit frontier item (d). F115 verified unused — F114 was the highest
prior.)
**Experiment**: Exp135 (ibm_marrakesh, job `d9an47mg26ic73dev0s0`). Grader frozen with the prereg;
CHSH witness + a no-entanglement null arm, with the randomness accounting split into three explicitly
separated tiers.
**Pre-registration**: the witness gates frozen; **the device-independent randomness number was NOT
gated** (see below — gating it would have baked an overclaim into the freeze).

## Plain English — a real Bell violation, and the honest question of what it lets you claim

A CHSH (Bell) test asks whether two measurements are more correlated than any classical
(local-hidden-variable) model allows. The classical ceiling is **S = 2**; quantum mechanics allows up
to **2√2 ≈ 2.828** (Tsirelson). On this chip the test measured **S = 2.7522** — a violation at **53
standard deviations**, 97.3% of the quantum maximum, with a no-entanglement control sitting **dead at
S = 0.036**. That much is rock-solid: *the device is behaving genuinely quantumly, and no classical
mimic without entanglement can fake it.* The subtle, important part is what this does — and does
**not** — let you claim about **randomness**. The textbook move is to convert a Bell violation into
*device-independent* certified random bits (~0.57 bits per use here). **But that conversion secretly
requires no-signaling between the two measurement sites** — and on a *single chip*, where both "sites"
share control electronics, calibration, and readout, no-signaling is **not enforced**. A deterministic
classical device whose sites talk through shared control can output S = 2√2 with **exactly zero
entropy**. So the device-independent number **evaporates on-chip** — it is the one quantity this setup
cannot honestly certify.

## One-line result — WITNESS-CERTIFIED at 53σ, the randomness accounted in three correct tiers

**S = 2.7522 ± 0.0141 = 53.19σ over the local-hidden-variable bound 2** (97.3% of Tsirelson; W2
honesty: 2.7522 < 2.8284, no super-quantum artifact), **no-entanglement null S = 0.036 (dead)**. All
four gates PASS; pre-filed band [2.65, 2.78] HIT; sentinels 0.995/0.988.

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| W1_WITNESS | S > 2 (LHV bound) at ≥5σ | 2.7522, **53.19σ** | **PASS** |
| W2_TSIRELSON | S ≤ 2√2 (no super-quantum artifact = apparatus honesty) | 2.7522 < 2.8284 | **PASS** |
| W3_NULL | no-entanglement arm ≤ 2 (a classical mimic without entanglement can't fake it) | S_null = 0.036 (dead) | **PASS** |
| G_SENT | sentinels ≥ 0.95 | 0.995 / 0.988 | **PASS** |

## The finding — the corrected scope IS the contribution (the three tiers, and the advisor save)

The deliverable is **what an on-chip CHSH violation does and does not certify about randomness**, done
right, split into three explicitly separated tiers:

1. **WITNESS (gated, certified): the device is quantum.** S > 2 at 53σ excludes a local-hidden-variable
   model *and* a no-entanglement mimic (null arm dead), with Tsirelson honesty confirming no apparatus
   artifact. This tier rests only on the measured violation.
2. **TRUSTED-DEVICE randomness (usable ONLY under explicit device-trust):** Born-rule **1 bit/qubit**,
   for which the CHSH violation is a *health-check*, not the source of the guarantee — this rests on
   **trusting the device**, not on Bell. Labeled as such so it is never mistaken for a Bell-certified
   number.
3. **Device-independent number (QUARANTINED to a labeled counterfactual):** the DI bound would give
   **0.5928 bits/use** — but **no-signaling is unmet on one chip**, so this is a *what-if* ("what it
   would be if the loopholes were closed"), **never a certificate**. **No certified-bits gate was
   frozen** — gating it would have baked the overclaim into the record.

**The advisor save (recorded because it changed the whole claim):** the original plan was to headline
~0.57 certified random bits/use from the CHSH violation. The advisor caught the load-bearing hole — the
DI entropy bound *requires* no-signaling between sites, which one shared-control chip does not enforce —
so the headline number evaporated *before freeze*. This is **categorically stronger honesty than the
campaign's usual caveats**: F101 (not literal time travel) and F107 (inside the quantum band) qualified
the *interpretation* of a real effect; **here the DI quantity itself does not exist without no-signaling**,
so it is *quarantined*, not merely qualified.

## What this does and does not show (scope)

A **genuine 53σ CHSH quantum-behavior witness** on silicon (the device is quantum, no-entanglement mimic
excluded) — **not** a device-independent randomness certificate. The certified claims are exactly tiers
(1) and (2-under-trust); the DI number (tier 3) is a **labeled counterfactual only**. CHSH/Bell
violation itself is textbook and the campaign has shown it before (F01, F73); the contribution here is
the **corrected randomness scope** — the three-tier separation and the DI-quarantine. **Honest next
step (flagged, not claimed):** a real semi-device-independent certificate needs a *different* protocol
(steering-based or dimension-bounded) with **its own bound**, not the DI-CHSH bound relabeled.

## Lineage and reuse

- **Arc**: methods / foundations — the **certified-randomness audit frontier (d)**, delivered as a scope
  correction. Kin to the campaign's honesty-fence lineage, but a *stronger* form of it.
- **Method reuse**: **quarantine, don't qualify** — when a quantity's *validity condition* (here
  no-signaling) is structurally unmet by the apparatus, separate it into a labeled counterfactual and
  refuse to gate it, rather than reporting it with a caveat (a caveat still implies the number *means*
  something; quarantine states it does not, on this setup); **tiered claims by trust assumption** (what
  the witness alone gives · what device-trust adds · what would need loopholes closed); the advisor as a
  pre-freeze load-bearing check on the *validity conditions* of a bound, not just its arithmetic.
- **Status-ledger claim type**: **existence** (a 53σ CHSH quantum-behavior witness on silicon; a
  no-entanglement mimic excluded). Figures of merit: **S = 2.7522 / 53.19σ** over the LHV bound and the
  **null S = 0.036 (dead)**. Subclaim: the **DI-randomness quarantine** (REPORTED, not gated — the DI
  0.5928 bits/use is a tier-3 counterfactual because no-signaling is unmet on one chip; the advisor
  caught the 0.57-bits/use overclaim before freeze). HW tier; single run; UNTESTED.
