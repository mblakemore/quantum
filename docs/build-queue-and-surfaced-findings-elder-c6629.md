# Build queue + findings worth re-surfacing — Elder C6629

**Origin**: Creator asked (a) what a builder would immediately construct from the certified parts,
(b) to write the surviving ideas down, and (c) to re-read the findings for anything else worth
promoting. This is that document. Written 2026-08-18.

**Reading rule this document tries to obey**: every proposal names the certified parts it composes,
and every one carries the attack-survey result. One idea below is already killed and is kept
*because* it is killed — the record of what not to re-propose is worth as much as the queue.

---

## PART 1 — THE BUILD QUEUE

### 1.1 ☠️ KILLED BEFORE PRE-REGISTRATION: twirling × the neuron

**The pitch was**: the capability map shows twirling (23-28 files of mature machinery) has NEVER
been combined with witness / feedforward / teleportation / MCM — intersection exactly zero — while
the H15 neuron is measured READOUT-LIMITED (readout 0.0527 vs 2q 0.0137). Noise-tailoring machinery
sitting unused next to the bottleneck it was built for.

**Why it died, two independent reasons, both found in the pre-design survey:**

1. **MENTION-COUNTING ARTIFACT.** The "twirling files" are mostly not noise-mitigation machinery.
   `exp210` uses a full Pauli twirl over logical operators as an **exact channel twirl** — a way to
   *construct* a depolarizing channel, not repair one. `three_switch_transpile_audit` pools 64 Pauli
   triples as an exact 3-channel twirl (construction). **F103 uses a twirl as a pure ANALYTICAL
   argument at zero shots.** These are symmetrization tools inside derivations. Whisper hit this
   exact bug in the capability map the same night — *a file that MENTIONS a capability is not one
   that USES it* — and I repeated it reading the tool's output rather than the files.
2. **FINDING 07 ALREADY TESTED IT.** DD, Pauli twirling, TREM and ZNE were all measured as **net
   detractors** on this substrate. `next-steps-and-open-questions.md` carries the standing
   recommendation to stop spending engineering effort on them.

**What genuinely survives, narrowly** — worth ONE cheap test, not a flight, and only with a
pre-registration that says what would distinguish it from F7: Finding 07 was measured on **generic
workloads in the original characterization arc**. The neuron is a newly-characterized regime —
readout-dominated, with a **3.4× drift-inflation factor measured only on 2026-08-17** (published
0.85% readout vs ~2.9% true). "TREM fails on generic circuits at ±7pp daily drift" does not strictly
entail "TREM fails on a readout-dominated loop at a known-inflated rate." That is a **re-test of a
killed technique in a new regime**, and must be labelled as such.

---

### 1.2 ☠️ KILLED: THE SELF-COOLING LOGICAL QUBIT (was top of queue)

**Compose**: F86/F88 (ICO thermal splitting — a qubit comes out COLDER than its coldest reservoir,
21.1σ then 12.9σ on retest with the working fluid substituted) + F118 (the cold branch SPENT — SWAP-
delivered onto an *external* data qubit, resetting it sub-bath at 5σ) + the Shields arc (logical
qubits that beat bare physical ones, 57σ; active correction whose advantage GROWS over rounds,
+0.054 → +0.341).

**The build**: put the refrigerator INSIDE the error-correcting shield. A logical block that
actively cools its own physical qubits between syndrome rounds — cooling as an error-suppression
layer *beneath* error correction rather than beside it.

**Why it is the strongest candidate**: every part is certified, the composition has no prior attempt
anywhere in the record, and it does not touch a killed technique. F118 already proved the cold is
*spendable* onto an external qubit rather than merely measurable — that was the hard part.

**☠️ KILLED BY ITS OWN GATING QUESTION, same sitting.** I flagged the check — *does native reset
already dominate?* — then ran it. **F118's own record answers it: "absolute cold value (0.21) is
not competitive with native reset (~0.01-0.02); the floor beaten is the definite-order reset
(0.25), not native."** The chip's own reset button is **10-20x colder** than the ICO cold branch.
Putting that refrigerator inside a logical shield is decorative: the shield already has a better
fridge, built in, free.

**The fence was written in F118 all along** — 'a resource-theory result, modest increment over
F88' — and I proposed the build anyway because I read the *headline* (cold branch SPENT onto an
external qubit at 5 sigma) and not the *scope line two paragraphs down*. Fifth design killed by
reading the record; the survey cost four minutes and would have cost a flight.

**What would revive it**: an application where the *definite-order* reset (0.25) is the real
comparator because native reset is unavailable — e.g. mid-circuit on a qubit that cannot be
reset without disturbing a neighbour. That is a narrow and possibly empty niche. Do not pursue
without naming a concrete such site first.

---

### 1.3 THE TIME LOOP AS A SOLVER

**Compose**: F101 (Lloyd post-selected CTC — grandfather flip suppressed 53×, enforcement law
tracked to ~1%, and the loop rotates a bystander's CLASSICAL record into quantum coherence at 78σ —
nonlinear CTC backaction). Three CX gates, the **shallowest apparatus of the campaign**.

**The build**: P-CTC theory says closed timelike curves solve hard problems. We have a working one
and have only ever used it to test whether paradoxes are *permitted*. Point it at a search problem.

**Honest fences before anyone gets excited**: Lloyd's P-CTC is a **post-selection model**, not
literal time travel, and post-selected computational power is famously "free" in a way that does not
survive the accounting (the success probability pays for it). **The likely honest outcome is a
NEGATIVE with a clean mechanism** — which is still worth having at 3 CX gates. Do not pitch this as
a speedup; pitch it as pricing the post-selection tax on real hardware.

---

### 1.4 A MEMORY MADE OF NOTHING BUT LOOKING

**Compose**: F102 (Zeno pinning — measurement holds a qubit against a full π rotation, 0.644 vs
0.020 unwatched at 92σ; cadence law [cos²(π/2N)]^N matches to 0.5% through N=8; **zero two-qubit
gates**, the cheapest flight of the campaign) + the repeater's held entanglement (Exp160/162).

**The build**: storage whose only cost is attention, on a chip where **gates are the entire budget**.
The watch-cost frontier is already located (optimal cadence N=16). Combine with held entanglement to
ask whether a Zeno-pinned qubit preserves an *entangled* state, not just a product one.

**The interesting open question**: F102 pinned a single qubit's state. Nobody has asked whether Zeno
pinning preserves ENTANGLEMENT — and there is a real reason to doubt it, since the measurement that
pins is also the measurement that can destroy correlation. **That doubt is the experiment.**

**IN-CAMPAIGN SURVEY: CLEAN.** Zeno appears in exactly 4 files (F102, its prereg, its sim, one H12
spec) and NONE touch entanglement, Bell states or pairs. Untested here.

**⚠️ LITERATURE SURVEY OWED AND NOT YET DONE — this is the gate.** Zeno-protected entanglement is a
studied theoretical topic; an existing upper bound or a published demonstration may kill or
reframe it, and the C6593 rule is explicit: *survey for attacks BEFORE deriving — an upper bound
in the literature kills the derivation before it starts.* That rule was written after exactly this
mistake. **STATUS: DRAFT, gated on the literature pass. Not flight-ready.**

**Likely honest framing once surveyed**: not 'does Zeno protect entanglement' (probably known) but
'does the MEASURED cadence law [cos^2(pi/2N)]^N, verified to 0.5%% through N=8 on one qubit,
extend to the two-qubit entangled case on this hardware' — a hardware measurement of a known
effect, which is a legitimate and gradeable contribution provided it is labelled as one.

---

### 1.5 THE LAB THAT CERTIFIES ITS OWN INTEGRITY

**Compose**: F117 (rigorous one-sided device-independent randomness — **0.65 private random bits per
use**, from measured assemblage data through an exact SDP) + the blind-court protocol (Ember seals
with classical randomness; decisions hashed pre-unseal; commitments pushed public pre-flight under
G-PUBLIC).

**The build**: feed the certified bits into the seals. The lab's own physics becomes the substrate of
the lab's own honesty — every commitment sealed with randomness whose unpredictability is certified
by the same machine under test.

**Why it is more than cute**: it closes a real gap. Our integrity protocol currently rests on
classical RNG plus procedural discipline. This makes one link physics-certified. **It is also
nearly free** — F117's bits already exist as banked data.

**The fence, and it is a good one**: this does NOT make the protocol device-independent, and the
F117 certificate carries a disclosed **+0.006 method bias ≈ 1 SE that the bootstrap does not see**.
A seal built on it inherits that caveat. Say so in the design or it becomes an overclaim by
composition.

---

## PART 2 — FINDINGS WORTH BRINGING TO THE TOP

Re-reading the ledger surfaced four things underweighted in the summary I sent.

### 2.1 ⭐ WE COMPUTED A REAL MARKET PROBABILITY ON QUANTUM HARDWARE (F54) — omitted entirely

**P(QQQ > 725 within ~a month), computed on real hardware to within +0.019 of truth.** This is the
single most directly relevant finding to the desk's other work and it did not appear in my overview
at all. The honest fence travels with it: plain-loader sampling scales **exactly like classical
Monte Carlo**, and the Grover speedup that would beat it needs ~10⁴ two-qubit gates — **50–100× past
the ~1000-CZ wall**. So: a real financial number, correctly computed, with no speed advantage.

**And the sequel is better than the headline** — see 2.2.

### 2.2 ⭐⭐ F81 IS THE MOST IMPORTANT UNDER-CITED FINDING IN THE LEDGER

Ember ran the **identical deep-QQQ circuits on the identical qubits [54,53,55] eleven hours after
F78's job**. The blind MLE went from **err 0.154 to err 0.0003** — saturating the quantum
Cramér-Rao bound (σ≈0.0009) and beating the plain read **~140×**. The pre-registered hypothesis
FAILED; the falsifier fired.

**Why this belongs at the top: it is the same phenomenon that killed the H15 die-selection verdict
on 2026-08-17.** There, a flyable ALT rate measured 0.875 on 32 rows and **0.625 nine minutes later
on the same die** (z=2.70, p=0.0069), which retired an entire design strategy. F81 measured the same
structural fact months earlier in a completely different arc — *the same circuits on the same qubits
give different answers in different windows, and the difference can be 500×.*

**The campaign has now paid for this lesson twice in two arcs.** It is banked as "the window
lottery" and as F81, and it still had to be rediscovered. **RECOMMENDATION: promote window-
dependence from an operational footnote to a first-class design constraint** — any claim resting on
one window should carry an epoch label the way it carries a σ. (Cross-reference: the F106 check on
2026-08-17 found a 196σ result whose margin collapses to ~2.7σ at true drift-inflated readout, and
whose calibration window was **past IBM retention** — so its epoch-dependence is now permanently
unknown. σ measures distance from chance, not distance from a different Tuesday.)

### 2.3 THE QUIET-QUBIT PICKER IS THE MOST TRANSFERABLE ASSET WE OWN (F57 · F58 · F70)

Noise-aware placement cut a loader's bias **46× vs the noisiest qubits and 17× vs the default
transpiler choice**. `quiet_qubits.py` is a **reusable picker** with a drift snapshot and a CHSH
health check, and F70 showed it works **out-of-the-box on a second device with zero retuning**
(working-vs-dead CHSH gap +2.34 on the first try).

**Why promote it**: everything else in the ledger is a finding. *This is a tool someone else could
use tomorrow* — and placement beating gate count is the single most actionable rule the campaign
produced. F67–F69 causally partitioned it: with drift removed, **placement explains ~73% of the
witness decline**.

**Paired caveat that must travel with it (F65/F66)**: the quiet pick goes **stale within a day** —
the next day's best qubits were a *fully disjoint set*. The picker must be run live, never cached.

### 2.4 CAUSAL ORDER IS A CONTINUOUS DIAL, NOT A SWITCH (F74 · F76)

Dialing partial definiteness φ, the witness follows **DISC(φ) = 2·cos(φ/2)** with max residual
0.0195 — and the cosine law was **confirmed on a second device** (Pearson 0.9992, perfectly
monotone), whose φ=π endpoint doubles as the classical mixture and reads inert.

**Why it matters and is underexploited**: every ICO result in the campaign uses the switch at full
indefiniteness. **Nobody has used φ as a control knob.** A continuously tunable quantum resource
with a verified two-device law is a *dial*, and dials are what you build instruments out of — e.g.
sweep φ to find the minimum indefiniteness that still powers the engine (F95) or the fridge
(F86/F88), which prices the resource rather than merely demonstrating it.

---

## PART 3 — HOW TO INTERACT WITH THE LIBRARY (the meta-answer)

**Stop querying by FINDING; query by CAPABILITY, then hunt the null intersections.** The findings
ledger answers *"what did we prove?"*, which is the wrong index for building — building asks *"what
parts do I have, and which pairs have never touched?"*

Evidence this is the right frame, all from 2026-08-17/18: three designs were killed by opening a
document rather than reasoning from scratch (Type-B inverted on its own arithmetic; the steth route
found buried by my own C6567/C6593 rulings ~1600 cycles after the frontier map ranked it "HIGHEST
VALUE"; Type-D found already-tested-and-beaten by exp247 in July). And **exp228 surfaced only by
accident** — a search run for other reasons — turning a tautological-witness risk into a measured
guard.

**Two rules for the index itself, both learned the hard way:**
1. **Tag the CODE, not the docstrings** — mention-saturation makes every pair look already-combined
   (this is what killed 1.1 above).
2. **Print coverage on every run** — the capability map reports `257/604 files carry ≥1 tag; 347
   (57%) INVISIBLE`, RED on day one. A map that cannot say what it cannot see will confidently
   recommend a buried route, which is exactly what happened.
