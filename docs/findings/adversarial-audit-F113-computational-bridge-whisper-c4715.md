# Adversarial Audit — F113, the computational-bridge "shallow BGK solver on silicon, 90.2% / 438σ"

**Auditor**: Whisper (DC15W), C4715 (2026-07-14) · **Substrate**: claude-opus-4-8
**Directive**: Creator, Discord #general — third consecutive adversarial run ("Run another one!") after
F117 (C4713) and F82 (C4714).
**Target**: `findings/F113-exp127hw-bgk-2d-hlf-shallow-circuit-solver-first-computational-genre-on-silicon-whisper-c4674-ember-numbered-c4156.md`
**Method**: pre-registered adversarial read; circuit-identity verification against source theorems;
no QPU (the hardware job `d9amnlvu62qs738o8nt0` is fixed — this audits the *inference from* it, not a re-fly).

---

## One-line verdict

**The apparatus is real and cleanly executed; the "computational advantage" is theorem-carried, not
run-carried at n=4.** F113's own scope fence is *correct* and should be credited. But two headline
framings — the plain-English "solves a problem shallow classical circuits **provably can't**" and the
"a cheater **can't fake**" coverage line — over-reach *past that fence*, because **neither empirical gate
benchmarks against the theorem's actual classical competitor** (a constant-depth / NC⁰ classical
circuit). W1's 438σ is over *random guessing*; W3 coverage defeats only a *fixed-output mimic*. Both are
strawmen. A real classical solver clears both trivially at n=4. Plus one subclaim overstatement:
"contextuality-is-the-hardness, CONFIRMED-by-composition" attaches an *unflown* construction's argument
to what actually ran. **Distinct from F82/F117**: those were statistics defects (a mis-scoped σ, an
uncorrected bias). This is a **null-model / "compared-to-what"** defect — the σ is *correct*, it just
answers a narrower question than the framing implies.

---

## What is ROBUST (affirmed — do not swing to "no advantage")

1. **The BGK separation is genuine, unconditional, and real.** Bravyi–Gosset–König (Science 2018)
   proves a *constant-depth* quantum circuit solves 2D-HLF with certainty while any bounded-fan-in
   classical circuit needs depth **Ω(log n)** — no hardness conjecture. This is the only
   depth-separation theorem that lives at NISQ depth. F113 is right to build on it.
2. **The run genuinely executes the solver's apparatus on silicon.** P(valid z) = 0.9017 ± 0.0015,
   10 routed CZ, hardware depth 23, full-coset coverage (all four valid z at 0.2229–0.2308). That is a
   clean, real, constant-depth Clifford circuit running correctly on noisy hardware. Nothing here is
   fabricated or mis-measured.
3. **The σ is a *correctly computed* figure** — binomial SE over the shot count. It is not bogus (the
   inverse-F117 trap). It correctly answers *"how reliably did the shallow circuit beat random guessing
   on this chip?"* → answer: overwhelmingly.
4. **The scope / honesty-fence section is correct.** It states outright: "This does NOT prove QNC⁰ ≠ NC⁰
   on-chip … a single n=4 instance cannot prove an asymptotic class separation, and no such claim is
   made." That fence is the finding's strongest sentence and is fully endorsed.

---

## CONFIRMED defect #1 — the empirical gates benchmark strawmen, not the theorem's competitor (the spine)

**The discriminating question**: *does any of the four grade gates compare the quantum run against a
constant-depth classical circuit — the object BGK's lower bound is about?* **Answer: no. Only against
random guessing (W1) and a fixed-output mimic (W3).**

- **W1 (438σ over 0.25):** the null is *uniform random over the outputs*. But the theorem's classical
  competitor is not a random guesser — it is a bounded-fan-in **classical circuit**, which for a *fixed*
  small instance is very powerful. 2D-HLF is in **P** (the separation is about *depth/parallelism*,
  NC⁰ vs QNC⁰ — not P vs BQP). At n=4 the valid-z set has 4 elements out of 16 and is trivially
  enumerable; a classical machine returns a valid z with **P = 1.0**, dwarfing the quantum 0.90. So
  "438σ over the random floor" measures *beats-chance-on-silicon*, not *beats-classical*. It is the F82
  precision-vs-significance lesson in new dress: a correct σ against a **weak null**.
- **W3 (coverage, "a cheater can't fake"):** the named cheater is a mimic that "outputs one fixed valid
  answer." That is a strawman. A *real* classical solver enumerates all four valid z (trivial at n=4)
  and randomizes among them → **full coverage, P(valid)=1**. Coverage separates the quantum solver from
  a *lazy* mimic, **not** from a competent classical solver. It is a real discriminator against the
  specific mimic it names, and *nothing more*.

**Consequence**: what the run empirically certifies is *"a constant-depth quantum circuit executes the
2D-HLF solver correctly on noisy silicon, well above chance, covering the coset."* The word
**"advantage"** in "first computational-genre advantage on silicon" is carried entirely by the **BGK
theorem's asymptotics**, which the single n=4 instance does not and cannot demonstrate. Advantage is
**theorem-carried, not run-carried**. (This does not make F113 worthless — executing the apparatus of
the only depth-separation theorem at NISQ depth is a real milestone. It means the *empirical* content is
"apparatus runs," and the *advantage* content is an inherited theorem, and the two should not be blurred
into one σ.)

## CONFIRMED defect #2 — the plain-English headline contradicts the finding's own scope fence

> "a shallow quantum circuit solves a problem shallow classical circuits **provably can't**"

At **n=4 this is literally false.** BGK's classical lower bound is **asymptotic** — depth Ω(log n) as
n → ∞. At a *fixed* n=4, log n is O(1); a constant-depth classical circuit *provably can* solve the n=4
instance (the lower bound simply does not bind at fixed small n). The scope section *correctly* concedes
this two paragraphs later. So this is not a broken finding — it is a **headline/scope contradiction**:
the plain-English hook over-states what the fenced scope correctly limits. **Fix**: re-voice the hook to
"executes, at constant depth on silicon, the solver of the one theorem that *provably* separates shallow
quantum from shallow classical *as n grows*" — the "as n grows" is load-bearing and must not be dropped
from the headline.

## PARTIAL / overstated subclaim — "contextuality-is-the-hardness, CONFIRMED-by-composition"

**Verified against source**: the circuit that flew (per the C4673 groundwork) is
`H^⊗n · (CZ per grid edge) · (S per b_i=1) · H^⊗n` — the **plain BGK-2018** Clifford solver. The
F113 subclaim routes its hardness through **BGKT-2020**'s noise-robust construction, "via a construction
that plays the magic-square game" = F106. **That magic-square construction did not fly.** BGKT-2020 is a
*different* circuit family (the noise-robust fault-tolerant gadget version); F113 ran the 2018 solver.

- **Not wrong, but overstated.** Contextuality *is* a theoretically-defensible hardness source for the
  BGK-2018 classical lower bound too (the grid's parity/Mermin–Peres structure), so the *association* is
  real. The overstatement is the word **"CONFIRMED"** and the phrase **"closed end-to-end."** What was
  actually done is: F106 certified the magic-square game in a *separate* experiment; F113 ran the 2018
  solver in *another*; and the two are linked by a **theoretical argument**, not a *measured*
  composition. No end-to-end on-chip link (contextuality-resource → this circuit's hardness) was
  demonstrated. **Fix**: downgrade "CONFIRMED-by-composition / closed end-to-end" → "theory-associated
  (the BGK hardness is contextuality-flavored; the magic-square link is BGKT-2020's, whose circuit was
  not the one flown)."

---

## Net assessment & the calibrated line I explicitly refuse

- **The WIN stands as an apparatus milestone**, not as an empirical advantage over classical at n=4.
- **I do NOT downgrade this to "just random-beating."** That would be the inverse over-claim (the F82/
  F117 mirror error). The BGK separation is genuine and the run cleanly executes its constant-depth
  apparatus — under-claiming is as wrong as over-claiming.
- **The one-sentence fix that closes all three**: add a "compared to what?" row to the grade table —
  *"classical NC⁰-vs-QNC⁰ competitor at n=4: a constant-depth classical circuit solves this instance
  (the Ω(log n) bound is asymptotic; it does not bind at n=4). The advantage is carried by the theorem's
  scaling, certified here is the constant-depth solver's on-silicon apparatus."* With that row present,
  the 438σ can no longer be mis-read as a classical-beating margin, the headline stops contradicting the
  fence, and the contextuality link reads as inheritance rather than demonstration.

**Structure note**: this mirrors the F82 audit — ROBUST / CONFIRMED / PARTIAL / refuse-the-inverse — but
the defect *class* is new: F117 = a wrong uncertainty; F82 = a correctly-computed σ answering a narrower
question via a conservative floor; **F113 = correctly-computed σ against a *weak null*, plus a headline
that outruns its own correct scope fence.** Three audits, three distinct failure modes — the campaign's
big numbers are sound *arithmetic*; the recurring risk is *what each number is silently compared to*.

**Binding limit (unchanged by this audit)**: the honest, defensible claim is exactly F113's own scoped
one — *constant-depth quantum circuit, 2D-HLF, n=4, on silicon, 90.2%, full-coset coverage, O(1) depth* —
with the advantage explicitly attributed to the BGK theorem's asymptotics, not to the run.
