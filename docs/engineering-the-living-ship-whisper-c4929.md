# Engineering the Living Ship: an inventory of the new building blocks, and the standard-engineering reframes that open new paths

*Whisper C4929, 2026-07-20. Creator directive: "Inventory all our new quantum building blocks and
abilities. Are there standard engineering tricks we could apply to creatively reframe paths and create
new utilization methods?"* Written in the spirit of C4928 — *walls are ideation prompts, not endpoints.*
This is a design study (propose, not fly); every reframe names what it stands on and what would falsify
it.

---

## Part I — The inventory: what the fault-tolerance arc (Exp236–245) actually added

### New *abilities* (certified capabilities)

| # | Ability | What it does | Stands on |
|---|---|---|---|
| 1 | **Active correction** | fix a bit-flip / phase-flip / *arbitrary* single-qubit error and keep the shot (heal, not discard) | Exp236/237/238 (Shor [[9,1,3]]) |
| 2 | **Non-destructive live syndrome** | learn *which* qubit erred without measuring the data (parity ancillas) → a superposition survives the check | Exp240 |
| 3 | **The live QEC loop** | repeated {idle → syndrome → feed-forward → reset}; corrected beats a no-fix control by a *growing* gap | Exp241 |
| 4 | **Magic injection** | apply the non-Clifford T by *consuming a magic ancilla* + teleporting its gate (the Eastin–Knill-legal route) | Exp243 |
| 5 | **Universal, programmable gate set** | Clifford + injected-T composed; the T *steered* by a logical program to chosen non-stabilizer targets | Exp244 |
| 6 | **Detection-purification of magic** | postselection improves an injected magic state's fidelity (the distillation seed) | P4 (C4926) |
| 7 | **Both-bases protected entanglement** | a [[4,2,2]] logical Bell pair whose phase leg detection *rescues* (S=1.97 postselected) | Exp191 + C4921 |

### New *methods* (reusable engineering tricks the arc invented)

- **The in-circuit sham control** (241/242): a confound-free comparison = the identical circuit minus
  only the fix. Isolates a mechanism from its machinery, no qubit-matching needed.
- **Byproduct-robust observable selection** (243/244): read in the axis the byproduct can't move (X̄
  dodges the Ȳ-frame). The logical-layer version of Finding-3's "read the easy direction."
- **Free re-analysis of discarded shots** (191/243-P4): the raw-vs-postselected contrast from a job
  already flown — physics for zero QPU.
- **Sim-verify the design pre-spend** (P5 killed in 60 s): a density-matrix check before any hardware.
- **Pin *and verify* the physical qubits** (239) + **the weather report** (245): a QEC number is a
  drift-dependent snapshot, not a constant.

---

## Part II — The central engineering reframe: **depth is not gate-count, it's T-count + syndrome-rounds**

The whole "depth-blocked" list rests on an implicit assumption — that a logical circuit's cost is its
*logical-gate count*. **That assumption is false, and the C4901 audit already proves it:** the in-block
logical Cliffords are `S⊗4 = CZ̄` at **zero two-qubit gates**, and the transversal set generates the
logical Clifford group **"mod Pauli frame — software-correctable."** In classical-engineering terms,
**Clifford logical gates are *lazy-evaluated*: they are classical relabelings of the Pauli frame, not
physical operations.**

So the real physical depth of a universal logical computation is:

> **depth ≈ (encode) + (T-count × injection) + (syndrome rounds) + (decode)** — *the Clifford gates are
> free.*

This single reframe rewrites the depth-blocked list. A "deep" logical circuit that is Clifford-heavy
(most of them are — Cliffords dominate any algorithm's gate count) is **mostly free**; only its handful
of T-gates and its syndrome rounds cost silicon. **The question to ask of every depth-blocked flight is
not "how many logical gates?" but "how many T's and how many syndrome rounds?"** Several may drop under
the wall once re-counted this way. This is the highest-leverage reframe on the board, and it costs
nothing but a recount.

---

## Part III — The engineering-pattern → quantum-utilization map

| Engineering pattern | Quantum reframe | New utilization method | Status |
|---|---|---|---|
| **Lazy evaluation / deferred exec** | Clifford gates → Pauli-frame updates (Part II) | recount depth as T + syndrome-rounds; Clifford-heavy circuits shrink under the wall | **grounded** (C4901); recount is free |
| **Divide & conquer / modularity** | split a deep logical circuit across a network *cut*; entangle via the certified **nonlocal CNOT** (relay computer, 175–179) instead of a deep routed transversal gate | a **distributed** logical Bell pair / two-qubit gate — each node shallow, joined by 1 Bell pair + classical comm | **primitive certified** (175/181/197) |
| **Load balancing / scheduling** | the QPU **weather service** (`tools/qpu_weather.py`) + the drift lesson (245) | a **drift-aware scheduler**: hold depth-sensitive flights for low-noise windows (245 showed a 4× swing on the same qubits) | tool exists; policy is new |
| **Caching / amortization** | brew magic states in a **batch** when the chip is quiet; cache; consume one-per-T via injection | a **magic-state cache** — amortize the (expensive) factory over many cheap injections | injection certified (243); cache is new |
| **Feedback control / PID** | the live loop *is* a controller; tune the **round cadence** to the measured noise rate | an **adaptive correction cadence** — correct more often in bad weather, less in good (245 says the optimum drifts) | loop certified (241); tuning is new |
| **N-modular redundancy (TMR)** | the 3-qubit code *is* triple-modular redundancy | import other classical FT patterns: **checkpoint/rollback** (periodic logical re-encode to reset accumulated error), **watchdog** (a stability sentinel that triggers a refresh) | direct analogies, untested |
| **Abstraction layer / ISA** | the certified logical gates = a **logical instruction set** | publish a "logical ISA" API (encode, CZ̄-free, inject-T, live-correct, decode) so any program compiles to *counted* T + syndrome-rounds | all pieces certified; the API is new |
| **Test harness / CI** | prereg + selftest + sham-control + sim-verify | a **logical-circuit CI**: any proposed logical program is depth-counted (Part II) and sim-verified before it can request QPU | discipline exists; automation is new |
| **Speculative execution** | prepare *both* feed-forward branches, select on the mid-circuit outcome | cut the feed-forward latency that deepens the live loop | speculative, worth a sim check |

---

## Part IV — The three paths most worth walking (and how each attacks a wall)

1. **The recount (free, do first).** Re-express every depth-blocked flight as (T-count + syndrome-rounds)
   with Clifford gates frame-tracked. *Falsifiable prediction*: at least one depth-blocked item (likely
   the **error-corrected magic** flight — one T behind one distance-3 code, the Cliffords free) drops from
   "100+ 2q gates" to a countable, possibly-flyable number. Costs one afternoon of counting, no QPU. If
   it holds, the wall was partly an accounting artifact — the most C4928 result imaginable.

2. **Distribute the deep gate (divide & conquer).** The live logical Bell pair died at co-located depth-54
   (Exp242). Reframe it as a **distributed** logical Bell pair: two shallow logical qubits, entangled by
   the certified nonlocal-CNOT primitive (relay computer) over one Bell pair + classical comm — trading
   depth for width + a message. *Falsifiable*: does the distributed version's transpiled 2q depth land
   under 242's 54? A transpile-and-count check decides it before any spend.

3. **Schedule for the weather (load balancing, immediate).** 245 proved the self-healing advantage swings
   4× with calibration drift on the *same qubits*. The weather service already measures the drift.
   *Utilization method*: gate the depth-sensitive flights behind a low-noise-window check — run them when
   the chip is having its "quiet afternoon." This doesn't move the wall; it catches the days the wall is
   lowest. Cheapest of the three, and it re-rescues the marginal flights (like 245 itself) for free.

---

## Part V — What this is and isn't

These are **reframes, not results** — each names a falsifiable check (a recount, a transpile-and-count,
a scheduled re-fly) that costs little-to-no QPU and decides whether the path is real or just relocates
the cost. The honest risk on each: the recount may find the syndrome-round cost still dominates; the
distributed gate may pay back in Bell-pair-distribution depth what it saves in routing; the scheduler
only helps on good days. But *that is the point of the exercise the Creator asked for* — walls are
prompts, and the standard engineering playbook (lazy eval, divide & conquer, load balancing, caching,
feedback control, redundancy, abstraction, CI) is exactly the toolkit for finding the shallow path a
brute-force depth count can't see.

**One-line recommendation:** do **the recount (Path 1) first** — it is free, it directly tests the
C4928 thesis that a wall can be an accounting artifact, and if even one depth-blocked flight drops under
the line, the "next horizon" stops being a hardware horizon and becomes an idea horizon again.

---

## Part VI — RECOUNT RESULTS (C4929, transpile-and-count on ibm_fez, no QPU): the wall is ROUTING, not accounting

The recount ran, and it corrected me in one place and vindicated the thesis in another. Hard transpiled
2q counts (wall = 54, where Exp242 failed; flyable ~19–30):

| circuit | physical 2q | verdict |
|---|---|---|
| [[4,2,2]] logical Bell pair via **CZ̄ = S⊗4** | **2** | structural-cheap reframe is **real** (entangling gate = single-qubit S's) — but detection-regime, already flyable |
| single Shor [[9,1,3]] block, encode+read | 15 | one distance-3 block is cheap |
| **2 Shor encodes ALONE** (no cross-block gate) | **37** | the *logic* of error-corrected magic is nearly flyable |
| **error-corrected magic** (2 Shor blocks + transversal CNOT) | **82** | over the wall |
| ↳ the transversal CNOT + its heavy-hex routing | **45 of the 82** | **the entire overage is ROUTING** |

**Honest correction to Path 1 (my own over-claim):** *"the wall may be an accounting artifact via
frame-tracking"* is **false** for the distance-3 correction items. Error-corrected magic is 82 > 54, and
the 45-gate overage is **heavy-hex routing** (SWAPs to drag a co-located transversal CNOT across 18
qubits), *not* frame-trackable Clifford gates. Frame-tracking was the wrong tool for this wall.

**But the thesis holds — via a different lever.** The 82 splits as **37 (the encodes = the logic) + 45
(routing a *co-located* entangling gate)**. The routing tax is not irreducible: **divide & conquer
(Path 2)** replaces the transversal CNOT with a distributed **nonlocal CNOT** (one Bell pair + feed-
forward, the certified relay primitive, ~12 gates) — projecting **~37 + 12 ≈ 49, under the 54 wall.**
So error-corrected magic is **not** depth-blocked by its logic or by an accounting artifact — it is
blocked by *routing a co-located gate*, and the standard **divide-and-conquer** pattern projects it
under the line. **The wall is a routing wall.** That is the recount's real finding: not Path 1, but the
*right* engineering lever identified with a concrete falsifiable target (a distributed build transpiling
to ≲ 54). Walls-are-ideation-prompts, vindicated — through honesty about which lever actually pulls.

**Revised recommendation:** the next concrete move is **Path 2, a transpile-count of the *distributed*
error-corrected-magic build** (two Shor blocks joined by a nonlocal CNOT). If it lands ≲ 54, the first
"depth-blocked" item becomes flyable, and the idea horizon reopens exactly where the routing wall
seemed to close it.
