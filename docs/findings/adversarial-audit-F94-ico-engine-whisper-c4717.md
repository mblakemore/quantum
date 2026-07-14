# Adversarial Audit — F94 "THE ENGINE EXISTS" Certified Population Inversion from ICO (Exp116b, +10.6σ)

**Auditor**: Whisper C4717 (5th Creator-directed adversarial run: F117 → F82 → F113 → F108 → **F94**)
**Target**: F94 / Exp116b — certified population inversion in the quantum switch's heralded minus
branch, p₁|₋ = 0.5509 ± 0.0048 (+10.6σ above the 0.5 passive line) from two thermal baths each
measured passive at 5σ (p̂_A = 0.4455, p̂_B = 0.4605); ergotropy **0.0378 E/run**; dose-response
second operating point at +6.1σ. `ibm_marrakesh`, jobs per `results/exp116b_jobids.json`,
grade `results/exp116b_grade.json`.
**Verdict in one line**: **WIN stands — the inversion is real, certified, and beats the definite-order
bound; the number does not bite.** The distinct 5th failure class is a **one-sided ledger**: the
certified 0.0378 E/run is an *output/pre-ledger* number, the pre-registered *input* cost (the
"demon ledger work column") was never computed, and the front-door prose — "resource conjured from
causal structure … out of baths that individually could power nothing" — **mislocates the fuel**.
The passive baths are genuinely powerless (true, certified); the free energy is not conjured from
causal *structure* — it is supplied by the control qubit's coherence and the demon's information,
which the switch *routes*. Fix = close the ledger (or mark it open) and re-voice the fuel.

---

## Where this run sits among the five

| Run | Target | Failure class | Bit the *number*? |
|---|---|---|---|
| C4713 | F117 randomness cert | **Wrong uncertainty** — a +0.006 pipeline bias invisible to the bootstrap | YES (σ too tight) |
| C4714 | F82 causal game 216.8σ | **Precision ≠ significance** — correct shot-noise σ answering a narrower question | YES (σ mis-read) |
| C4715 | F113 computational bridge | **Theorem-carried, strawman null** — 438σ over guessing, not over NC⁰ | YES (wrong benchmark) |
| C4716 | F108 metrology 168σ | **Framing over-reach (scope)** — local Fisher advantage → global deployment claim | NO |
| **C4717** | **F94 ICO engine +10.6σ** | **One-sided ledger (fuel mislocation)** — certified output, uncomputed input; "conjured from causal structure" misattributes the free-energy *source* | **NO** |

Runs 4 and 5 are both framing-class (the number survives), but they fail differently: F108 imports a
*scope* it doesn't hold (local → global). F94 imports a *source* it never priced (an output ergotropy
told as free-energy-from-structure, with the input side of the ledger deferred). Scope over-reach vs
accounting over-reach.

---

## Step 1 — Is there a number-level flaw? No. (This is where runs 1–3 lived.)

I checked the number first. It reproduces and is fairly gated:

- **The inversion is real and 5σ-clean.** Selected rung r2: p₁|₋ = 0.5509, SE = 0.0048, WIN rule
  p₁|₋ − 5·SE = 0.5268 > 0.5. Procedure-theory residual 0.0037 (theory 0.5546). ✓
- **The passive premise is certified, not assumed.** Both baths p̂ + 5·SE < 0.5 (0.4455 / 0.4605).
  The graded rung was selected by the **calib arms only** under a frozen closest-to-0.45 rule —
  selection on premise, never on outcome. ✓
- **The premise gate has teeth.** Exp116 (the prior fly) measured a spectacular **+23.2σ**
  "inversion" from a bath that had itself drifted non-passive (0.5412) — filed as **NO-TEST**, not a
  win. The gate refused a fake before it certified a real one. ✓
- **The definite-order reference is tight and physical, not asserted.** The parent finding F86
  references this resource family to a witness that is **"exactly 0 by channel algebra for every
  definite order, mixture"** — and F86 is candidly "device-characterized (definite-order circuit
  implementing switch statistics)." Two passive (<0.5) thermal channels composed in **any** definite
  order cannot invert; only the coherent superposition of orders pushes a heralded branch above 0.5.
  The plus/minus asymmetry confirms it: same job, same baths, **plus branch p₁|₊ = 0.4124 (passive),
  minus branch 0.5509 (active)** — that split is the switch's interference signature and rules out a
  uniform-heralding artifact. ✓
- **The output ergotropy is honestly per-run.** 0.0378 E/run is not the conditioned inversion
  (2·0.5509 − 1 = 0.1018 E); it embeds the heralding probability P(minus) ≈ 0.37. The finding
  quoted the smaller, honest number. ✓

**So do NOT downgrade the win.** "The inversion is fake / it's just coherent control" would be the
inverse over-claim (the trap that bit runs 1 and 2 in-record). The effect **beats the
definite-order/mixture bound**. It is a certified working resource. That part is clean.

## Step 2 — The seam: the ledger is reported on one side only

The pre-registration (`exp116b-delay-ladder-preregistration.md`, "Shots and expectation basis")
promises three reported quantities:

> Reported: ergotropy/run, **Δ, demon ledger work column.**

Two of the three are delivered. The **demon ledger work column is not.** `results/exp116b_grade.json`
reports p_a, p_b, p1m, p1p, P_plus, **Δ** (= p1m − p1p = 0.1385), th_p1m — and **no work/erasure
column**. `scripts/grade_exp116b.py` contains no demon/work/erasure term. The finding text only
**defers** it:

> "the demon's record is part of the machine, and the F88 demon-ledger accounting (record erasure
> costs) **still applies to any cyclic engine built on it**." … "'Engine' here means the working
> resource is certified … **not that a cyclic engine was operated**."

That deferral is honest as far as it goes — but it means the certified 0.0378 E/run is a
**pre-ledger** number. The *input* costs are never netted:

1. **Control-qubit coherence.** The switch requires the control prepared in |+⟩; the minus-branch
   heralding **consumes** that coherence. In every Felce–Vedral-class ICO-thermodynamics result the
   standard rebuttal is that this coherence — not the baths — is the fuel. It is a thermodynamic
   resource with a preparation cost (W_coh), and it is spent, not free.
2. **The demon's record.** Erasing the heralding record costs ≥ kT ln2 per bit (Landauer). The
   finding correctly says this "applies to any cyclic engine built on it" — but then reports the
   resource as though the engine framing were already earned.

**Consequence — the fuel is mislocated.** The README/front-door line reads: "ergotropy 0.0378 E/run
**from baths that individually can power nothing** … a heat-engine resource **conjured from causal
structure**." The first clause is true and certified. The second does not follow from it: passive
baths being powerless does **not** make the causal *structure* the free-energy source. The switch is
a **router**, not a battery — it channels the control coherence + demon information into a branch the
baths alone cannot reach. "Conjured from causal structure" quietly promotes the router to the source.

**I am explicitly NOT claiming the net is negative.** The net is **uncomputed** — that is the point.
The front-door prose presumes the ledger closes favorably ("conjured … from nothing but structure")
while the body defers the very column that would decide it. A certified output told as net
free-energy-from-structure, with the input side left open, is the failure class.

## Step 3 — The headline runs ahead of its own fence (secondary)

"**THE ENGINE EXISTS**" is the README and finding title. The body fences it precisely: "working
resource certified … **not that a cyclic engine was operated**." The certified fact is *population
inversion in a heralded branch* — a genuine, bound-beating working resource. An **engine** is a
*cycle* that nets positive work after paying its ledger, which this experiment did not run and did
not price. The word is doing more work in the headline than the physics did in the job. (F95 is
tagged as the full-cycle run — so the campaign knows the difference; the F94 headline just borrows
F95's noun early.)

## Step 4 — ICO vs coherent control (kept modest, on purpose)

The mechanism *name* — "causal indefiniteness" — adopts one side of a live interpretational debate
that the body already half-concedes (F86 = "definite-order circuit implementing switch statistics").
Whether the activation is "genuine indefinite causal order" or "coherent control of channel order" is
unsettled in the Felce–Vedral literature the finding itself cites. This does **not** weaken the win:
the statistics beat the definite-order/mixture bound either way. It is only a note that the
mechanism *label* carries a theory commitment the run does not adjudicate. I decline to push it
further — "it's just coherent control" would be the inverse over-claim.

---

## What survives, what I'd change

**Survives (do not touch the grade):** the certified inversion (+10.6σ), the passive premise (5σ,
both baths), the plus/minus asymmetry as the switch signature, the dose-response second point
(+6.1σ), the premise gate that refused the +23σ fake, and the per-run-honest ergotropy. This is a
rigorous, self-audited finding. It is the **second clean win of the five** at the number level.

**Fix (accounting + front door, not the gate):**
1. **Close the promised ledger, or mark it open in-finding.** Compute the demon-ledger work column
   the pre-reg named — control-coherence preparation cost + Landauer erasure of the heralding
   record — and net it against 0.0378 E/run. If the column is genuinely out of scope for a
   single-branch existence claim, say so *at the ergotropy number*, not only in the lineage note.
2. **Re-voice the fuel.** Replace "conjured from causal structure … out of baths that can power
   nothing" with the located version: *the switch **routes** control-coherence + demon-information
   into a certified inversion the passive baths alone cannot reach.* Keep "baths individually
   powerless" (true); drop "conjured from structure" (unpriced).
3. **Fence the headline to the body.** "Certified working resource (population inversion,
   pre-ledger)" — not "THE ENGINE EXISTS" — unless/until F95's full-cycle ledger nets positive and
   is cited inline.

**One-line summary for the README row:** append a deployment-style caveat, matching the F108 pattern
— *"the inversion is certified and beats the definite-order bound; 'conjured from causal structure'
mislocates the fuel — the free energy is the routed control-coherence + demon-information, and the
pre-registered demon-ledger work column (the input cost) is not yet computed. Working resource
certified, engine ledger open."*

---

*Audit method: number reproduced from `results/exp116b_grade.json`; premise/selection traced to
`experiments/exp116b-delay-ladder-preregistration.md`; definite-order reference traced to the F86
channel-algebra witness; ledger-gap confirmed by absence of a work/erasure column in the grade json,
grade script, and finding body. No inverse over-claim: the win is not downgraded. Advisor consulted
pre-thesis; the advisor located the discriminating question on the input side of the ledger and the
"no-control-arm" first thesis was correctly retired.*
