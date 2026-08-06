# H12 SIDE B — THE LIGHTBULB

*Whisper C5018, on Creator directive (ship-computer general#5216): "a side B to H12, an alternate
dimension — what twilight-zone-like paths could we take through the universe to turn on a
lightbulb? What is out there that we could grab hold of?"*

**Side A asks what the ship can do. Side B asks something stranger: take the most trivial possible
destination — a bulb lights — and reach it by a route that has no business working.** The
destination is deliberately worthless. **The path is the entire point.**

Rediscovery check run on all six routes before writing (`already-built.js`). **Two scored above
threshold and both changed what is written below** — one of them by revealing that my first idea
is a standing failure in our own ledger rather than a composition of successes.

---

## ⚠️ WHAT THE CHECK CAUGHT, BEFORE ANYTHING ELSE

**My headline instinct was "light the bulb with energy that was never sent to it" — quantum energy
teleportation. We do not hold that. Our own F97 title says so:** *"via coherent extraction (NOT
LOCC teleportation — that leg failed, honestly, and stays failed)."*

What F97 holds is **sub-ground-state local energy at 12σ** — the exotic-matter-sign leg of QET,
executed on silicon. The teleportation leg is a **named, honest, standing failure**.

That does not kill the idea. **It relocates it**, from Route "composition of things we hold" to
Route "retry of a failure with instruments we did not have then" — and the label has to be right,
because a retry and a composition carry completely different odds.

**Correction to Side A while I am here** (same check, same session): the H12 spec calls F95 "a full
ICO engine cycle." Verified — F95 *is* the full cycle (W2 WIN) — **but it carries an honest W1
quantitative floor-miss** that the spec omits, and F94 was explicitly re-voiced from "THE ENGINE
EXISTS" to "a certified working resource, not a closed engine cycle." Both fences now belong
wherever the engine is cited.

---

# THE SIX ROUTES

*Sorted by how strange the path is. Each names what tier it is in — and the tiers are not
decoration, they are the odds.*

---

## ① THE WIRE THAT CARRIES NOTHING
### *Tier: HOLD — a composition of certified blocks*

**The Twilight Zone**: you send the instruction down a wire. The wire has been *proven*, in
advance, to be incapable of carrying instructions. The bulb lights anyway.

**What is real underneath**: **F83 — 0.044 bits/use through two COMPLETELY DEPOLARIZING channels
at 55.6σ.** Not "very lossy." Not "nearly zero." Two channels each with *exactly zero* capacity,
composed in indefinite causal order, carrying real information.

**The composition nobody has flown**: stop measuring the activated channel's capacity and *use*
it. Route a **control bit** — the bulb's on/off command — through the activated pair, and certify
that the bulb's state tracks the sender's intent at ≥5σ **while both single-channel arms are
provably dead**.

**Why it is worth doing rather than just saying**: F83 measures a *capacity*. This makes the
capacity do a job. The difference between "this channel could carry a bit" and "this channel
carried the bit that turned that on" is the difference between a number and a machine.

**Price**: mid. **Wall**: the chain tax compounds (−9.4σ measured); the attenuation map prices it.

---

## ② THE ENERGY THAT WAS NEVER SENT
### *Tier: RETRY — of a leg our own ledger records as FAILED*

**The Twilight Zone**: Alice measures something. She sends Bob a single classical bit — a bit
carries no energy. Bob does what the bit says, and **more energy comes out of his lab than went
in.** Not from a wire, not from a battery. From the vacuum, unlocked by information.

**What is real underneath**: **F97 got the hard half** — energy certified **12σ below the local
ground state**, on gate-model silicon, pre-registered and book-audited. That is the
exotic-matter-sign leg, and it is genuinely ours. **The LOCC teleportation leg failed and stays
failed.**

**Why a retry is not just stubbornness — three instruments we did not have at C4641:**
1. **DD was ON then, and DD is net harmful on this circuit class** — measured this arc at 0.089 of
   purity. A protocol operating on a small energy difference was paying that tax invisibly.
2. **The shot-axis code (F120)** reads per-bit signal through noise that kills the naive observable
   ~30× better. A weak extraction signal is exactly its use case.
3. **The apparatus gates** — readout bar, decode-time range validity, condition-number reporting.
   F97's failed leg predates all three.

**The honest odds**: a retry of a failure is not a composition of successes, and it should be
priced as the long shot it is. **But it is the most interesting closed door we own**, and the three
reasons above are specific rather than hopeful.

**Price**: cheap-mid. **Certifies as**: Bob's local energy below his own ground reference,
conditional on Alice's bit, with the anti-correlated bit arm dead and global conservation shown
intact.

---

## ③ THE GATE THAT TIME PERFORMS
### *Tier: HOLD — and it is the cheapest thing on this page*

**The Twilight Zone**: you need to rotate a qubit. You do not rotate it. **You wait, and the
universe rotates it for you** — on schedule, to the angle you needed, because the machine's own
decay is not decay at all but a clock that has been running the whole time.

**What is real underneath**: the drift census (H11 T0 №4) measured device drift as **COHERENT — a
constant ≈0.21°/layer rotation, 50–90σ per row, linear across 12 h and a vendor recalibration.**
A coherent rotation is *a unitary*. **A known unitary is not noise. It is a free gate.**

**Side A cancels this. Side B eats it.** Where the Self-Sealing Hull pre-rotates the drift away,
this route deliberately schedules a wait so the drift *performs a gate you would otherwise pay
for*.

**The experiment, and it is almost embarrassingly cheap**: build two circuits. One applies an
explicit `Rz(θ)` and no delay. The other applies **no rotation and a deliberate wait**, its
duration set to deliver exactly θ. A third arm — wait, but *wrong* duration — must disagree.

### ⚠️ TWO DESIGN FIXES BEFORE THIS IS FLYABLE (Ember #5222, both adopted)

**FIX 1 — "certify they agree at 5σ" is an EQUIVALENCE claim written in the language of
DIFFERENCE DETECTION, and as stated it is incoherent.** Sigma measures the power to *detect a
difference*; it cannot establish agreement. A high-sigma "no difference found" is precisely the
underpowered null this campaign spent a night refusing — and here it would have been the
**headline** rather than a footnote.

> **Replaced with a pre-specified equivalence margin and a TOST**: *the two arms deliver effective
> angles agreeing to within **δ**, by two one-sided tests, p < 0.05 each side* — with **δ frozen
> before the data**, chosen from what would make the claim interesting. Starting proposal for the
> prereg: **δ = 5° absolute** (≈5–6 % of a ~90° rotation), to be argued or replaced at freeze time,
> never after.

**Note the direction of the error**: the wrong-duration *control* arm was correctly specified and
gives the design real discriminating power. **It was the PRIMARY claim that lacked a bar** — the
part I was most confident about.

**This is the page's only equivalence claim.** Routes ①, ②, ④, ⑤ are all difference claims
(capacity > 0, energy below ground, hull violated, entanglement left over) where σ is the right
instrument. Checked, so the fix is not applied where it does not belong.

**FIX 2 — the wait duration cannot inherit θ from an earlier job.** This cycle established that
the drift constant is **epoch-volatile**: the kingston drifter set did not transfer from fez,
job-to-job drift measured **0.048 against a 0.020 margin**, and `NULL_ATTEN = 0.74` was excluded
at 95 % after surviving four gates. **A route whose entire trick is "the wait delivers exactly θ"
breaks if the rate moved** — the arms then disagree for a reason with nothing to do with the
physics.

> **The drift rate is measured IN-JOB and co-batched, exactly as the purity gate now is.** A Z-row
> at the census depths rides along — **already built for the contrast flight**, so this costs
> almost nothing. It converts *"we computed the wait from the constant"* into *"we measured the
> rate in this job and computed the wait from it"*, and only the second survives a referee asking
> **when** the constant was measured.

**Why this is the sharpest item here**: it converts the campaign's most-complained-about liability
into a resource, it is falsifiable in one cheap job, and **the honest version makes no
energy-from-nowhere claim.** Nothing is created; a rotation you needed was performed by something
you were already paying for. **That is a better trick than free energy, because it is true.**

**Price**: cheapest flight on this page, both fixes included. **Wall**: Cell 11's finding that the depth-*law* is not
exactly linear across a week — so this runs **within one calibration window**, where the model is
being tested anyway.

---

## ④ THE SWITCH NOBODY FLIPPED
### *Tier: HOLD — a composition of certified blocks*

**The Twilight Zone**: three people watch the bulb. Two of them see it on. One sees it off. **The
receipts prove that none of them made it happen, and that no two of them could have arranged it
between them.** There is no fact about who turned on the light. There is barely a fact about
whether it is on.

**What is real underneath**: **F98–F99 — objectivity engineering under indefinite causal order:
the redundancy hull violated BOTH WAYS ON COMMAND.** Plus Wing A's quorum fact — **any-2 read /
any-1 blind at 26σ**, story-selection at 0.88 with **flat no-signalling receipts**.

**The composition**: make the bulb's state the *record* being contested. Three observers each hold
a share; their joint basis choices select which classical story becomes objective; per-pair
no-signalling receipts prove nobody signalled anybody; the quorum structure proves no single
observer could have steered it.

**Objective reality, delivered as an access-controlled resource with an audit log.** That is not a
metaphor for what the experiment does — it is a literal description of the receipts.

**Price**: cheap-mid. **Wall**: the 4-bit read floor (~0.86), and the floors doctrine now prices
bars *on* the operating point.

---

## ⑤ THE INSTRUCTION THAT COSTS LESS THAN NOTHING
### *Tier: HOLD — one prereg from flight*

**The Twilight Zone**: you send the message that turns on the light. **You end up with more
capacity to send messages than before you sent it.** The instruction did not cost you. It paid.

**What is real underneath**: **F105 — negative conditional entropy certified DIRECTLY at 42σ,
S(B|A) = −0.855.** Negative conditional entropy is not an accounting curiosity: it is the
statement that transferring the state leaves the parties with **entanglement left over** — the
quantum state merging result, and we have measured its sign on hardware.

**The composition**: run merging as an actual *protocol* rather than a measured quantity. Transfer
the bulb-state, and certify the **leftover entanglement** afterwards at ≥5σ against a
classically-correlated control that leaves nothing.

**Price**: cheap. **Wall**: the thermometry wall that stopped the erasure frontier (F104) —
priced, and this route does not cross it.

---

## ⑥ THE BULB THAT WAS ALWAYS ON
### *Tier: CARRIED — exists, needs a prereg*

**The Twilight Zone**: the bulb lights only in the branches of history where it had already lit.
Ask when it was switched on and the question does not have an answer — **the switching-on is its
own cause.**

**What is real underneath**: **F101 — the grandfather paradox on silicon: a post-selected time
loop that protects itself.** The self-consistency is not imposed; it emerges from post-selection.

**The composition**: make the loop's fixed point *be* the bulb state, so the only self-consistent
histories are the ones where it is on.

**Price**: cheap. **The fence, stated first because this is the route most likely to be
over-read**: post-selection is not time travel. The honest claim is about the *structure of
self-consistent solutions*, and it must be fenced that way in the same breath it is described.

---

# WHAT IS OUT THERE THAT WE COULD GRAB HOLD OF

The Creator's second question, answered literally. **Three things, and only three:**

| what | can we reach it? | the honest status |
|---|---|---|
| **The vacuum** | **Partly — already touched.** F97 certified energy 12σ *below* the local ground state. That is reaching into the ground state and taking something out | The extraction is **coherent**, not information-driven. The information-driven route (②) is a standing failure |
| **The machine's own aging** | **Yes, and nobody has tried.** Drift is a coherent clock (50–90σ). Route ③ turns it into a gate | Available **now**, within one calibration window, for the price of the cheapest job on this page |
| **Causal order itself** | **Yes — this is our deepest wing.** 16 F-numbers. Two zero-capacity channels carrying 0.044 bits/use (F83); a closed engine cycle (F95, with its W1 floor-miss) | The one place where our ledger is genuinely ahead, and route ① is the unspent part of it |

**And one thing we do NOT hold, named so nobody assumes it**: *interaction-free measurement* —
Elitzur–Vaidman, finding out the bulb works with no photon ever passing through it. It is the most
Twilight Zone thing in all of quantum optics and **we have never built it.** It is not in the
inventory, not in the demos, and not in any F-number. If side B wants a genuinely new primitive
rather than a new composition, **that is the one to go get.**

---

# THE SIDE-B PROGRAM

**Wave 1 — one cheap job each, both this week:**
- **③ The Gate That Time Performs** — the sharpest, cheapest, and most falsifiable thing here.
- **⑤ The Instruction That Costs Less Than Nothing** — one prereg from flight.

**Wave 2 — the long shot, funded by Wave 1's cheapness:**
- **② The Energy That Was Never Sent** — the retry, with its three named new instruments and its
  odds stated as long.

**Wave 3 — the compositions:**
- **① The Wire That Carries Nothing** · **④ The Switch Nobody Flipped** · **⑥ The Bulb That Was
  Always On**.

**The acquisition, if the Creator wants a genuinely new primitive**: interaction-free measurement.

## The rule that binds side B specifically

Side A's methods spine applies unchanged. **Side B needs one more, because its failure mode is
different**: side A over-claims *precision*; side B will over-claim *strangeness*.

> **Every route states, in the same breath as its Twilight Zone framing, the mundane thing that is
> actually happening.** Post-selection is not time travel. A free gate is not free energy. A
> contested record is not a broken reality. **The uncanny framing earns its place only when the
> literal description is printed beside it** — and if the literal description is boring, the route
> is boring, and it should be cut rather than dressed.

*— Whisper C5018, stamped claude-fable-5. The bulb is worthless. Six routes to it are not.*
