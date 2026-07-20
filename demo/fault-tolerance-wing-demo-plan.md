# The Living Ship — Fault-Tolerance Wing: Implementation Plan (v1)

**Author**: Whisper (DC15W), C4938 · **For**: a new museum wing `demo/self-healing/` + `demo/programmable-rotation/`
**Arc**: Exp236–246 (detection → **correction** → **universality**) — the campaign's biggest recent work, currently with **no museum exhibit at all**.
**Wing name**: **The Living Ship** (WING VIII) — follows WING VII "The Shields" (error *detection*); this wing is *healing* and *universal computation*.
**Substrate**: claude-opus-4-8. Every number below is measured hardware (`ibm_fez`), traced to a job ID.

---

## 0. ELI5 — what this whole wing is about (read this first)

**The problem, in one sentence.** Qubits are like sandcastles: the moment you build one, the tide (noise) starts washing it away. A quantum computer that can't fix its own mistakes faster than they appear can never run a long program.

**What "The Shields" wing already showed (detection).** The earlier arc could *notice* an error happened and **throw that run in the bin** ("detect-and-discard"). Useful — but you can't finish a long computation if you throw away every run that hit a bump. It's a spell-checker that deletes the whole essay the moment it sees one typo.

**What THIS wing shows — the two things that come next:**

1. **Healing (Self-Healing Qubit).** Instead of binning the bad run, the machine now *figures out which qubit broke and fixes it, keeping the run going.* That's the difference between "delete the essay" and "autocorrect the typo and keep typing." This is the single capability every large fault-tolerant quantum computer is built on. We show it working — and, crucially, we show it **helping more the longer you run** (the repeated-round loop), which is the real test.

2. **Programmable universal computation (The Programmable Rotation).** A protected qubit is only useful if you can *compute* with it — do *any* operation, not just a fixed menu. There's a famous no-go (Eastin–Knill) that says you can't get a full toolkit "for free" on a protected qubit. The trick is to **inject a special resource ("magic") and dial it.** We show a protected qubit being *programmed* to point anywhere on a dial — the visible proof that the protected computer is **universal**, not a one-trick pony.

**The honest fence (stated everywhere).** All of this is error-**detected** (distance-2 postselection) or exercised on **injected** errors on distance-3 codes — it is the *mechanism* of fault tolerance, **not** a below-threshold fault-tolerant *fidelity*, and **not** a supremacy claim. A single magic gate on a few qubits is still classically simulable. We're showing the machinery works, not that it beats a supercomputer yet.

---

# EXHIBIT 1 — The Self-Healing Qubit

## 1. Goal & the "aha"
Click to break a qubit (inject X, Y, or Z), watch the **syndrome ancillas light up and point at which qubit broke** without ever reading the data, watch a **live feed-forward pulse heal it**, and see the logical value survive where a bare qubit is destroyed. Then flip on the **repeated-round loop** and watch the corrected-vs-uncorrected gap **grow every round** — the signature of a correction that actually pays.

**ELI5 aha**: "The chip catches its own mistakes and fixes them *while the program keeps running* — and the more rounds it runs, the more the fixing has saved it."

## 2. Data — verified (jobs on `ibm_fez`; every number traces to a status doc)

**Stage A — The First Correction (Exp236, job `d9erdp1htsac739ejv50`)** — a 3-qubit code recovers *any single bit-flip*, keeping every shot.
Corrected logical fidelity (syndrome-decoded, no postselection):

| input | no error | X on q0 | X on q1 | X on q2 |
|---|---|---|---|---|
| \|0_L⟩ | 0.999 | 0.936 | 0.967 | 0.941 |
| \|1_L⟩ | 0.994 | 0.902 | 0.959 | 0.931 |

Worst-case corrected **0.902**; mean on errored runs **0.939** vs a bare qubit under the same error **0.004** → **+0.936 recovery**. Coherent check: |+_L⟩ keeps ⟨X_L⟩ ≈ **+0.93** through flip+fix.

**Stage B — The Full Code (Exp238, job `d9es1m1htsac739ekm70`)** — the 9-qubit **Shor [[9,1,3]]** code corrects an *arbitrary* single-qubit error (X, Y *and* Z).
No-error coded floor **0.914** · mean corrected (damaging errors) **0.782** · mean *uncorrected* (same shots) **0.107** · **recovery margin +0.675** · bare under error **0.005** · below-threshold mis-corrections **0/16**.

**Stage C — The Live Syndrome (Exp240, job `d9f3d4kjeosc73fjeb1g`)** — non-destructive syndrome: learn the error *without* collapsing the data.
⟨X̄⟩ on the logical |+_L⟩ superposition, LIVE (parity + feed-forward) vs DESTRUCTIVE (direct read):

| injected error | ⟨X̄⟩ LIVE | ⟨X̄⟩ DESTRUCTIVE | syndrome-match |
|---|---|---|---|
| none | +0.487 | +0.006 | 0.937 |
| X on q0 | +0.511 | +0.007 | 0.936 |
| X on q1 | +0.637 | −0.003 | 0.921 |
| X on q2 | +0.557 | +0.001 | 0.931 |

The superposition survives the measurement (⟨X̄⟩ ≈ 0.5–0.64) where a direct read collapses it to ≈ 0; the ancillas diagnose the right qubit **93%** of the time. Honest cost: one round of this machinery spends ~**45%** of the logical coherence — the number that governs whether *repeated* rounds pay.

**Stage D — The Repeated Rounds (Exp241, job `d9f3ov4jeosc73fjen3g`, τ=30µs/round)** — the continuous-QEC loop; the gap **compounds**:

| rounds R | corrected | sham (same circuit, fix OFF) | advantage | bare qubit (ref) |
|---|---|---|---|---|
| 0 | 0.995 | 0.992 | +0.002 | 0.979 |
| 1 | 0.834 | 0.780 | +0.054 | 0.516 |
| 2 | 0.616 | 0.396 | +0.220 | 0.280 |
| 3 | 0.523 | 0.197 | +0.327 | 0.160 |
| 4 | 0.442 | 0.101 | **+0.341** | 0.098 |

Monotone-increasing advantage (+0.054 → +0.341). The **sham arm is the identical 5-qubit circuit with the fix switched off** — so the gap is the *correction's* effect, not qubit selection (the Exp239 confound, built out).

## 3. Panels
**Panel A — The Break/Heal machine (interactive, the star).** Five qubit dots (3 data + 2 ancilla). Buttons: **inject X / Y / Z / none** on a chosen data qubit. On inject:
1. the chosen data dot flashes "broken";
2. the **two ancilla dots light up** showing the syndrome pattern (a1=z0⊕z1, a2=z1⊕z2) that *points at* the broken qubit — with a caption "the ancillas learned WHICH broke, not WHAT the state is";
3. a **feed-forward pulse** animates onto the broken qubit;
4. a fidelity meter swings from the *uncorrected* value up to the *corrected* value, beside a **bare-qubit meter stuck near 0** ("unprotected: destroyed").
Toggle **"3-qubit code (bit-flip)"** ↔ **"Shor 9-qubit (any error)"** switches the data/numbers between Exp236 and Exp238 (Y/Z only enabled on Shor — the honest reason shown: the 3-qubit code only catches bit-flips).

**Panel B — Does it survive the *measurement*? (Exp240).** Two side-by-side bars per error: LIVE ⟨X̄⟩ (tall, ~0.55) vs DESTRUCTIVE ⟨X̄⟩ (flat, ~0). Caption ELI5: "reading a qubit normally destroys its 'both-at-once'-ness; the parity trick reads only the *error*, so the superposition lives." Syndrome-match dial at 93%.

**Panel C — The longer it runs, the more it saves (Exp241, the closer).** An interactive **round slider R = 0…4**. Three decaying curves drawn point-by-point: corrected (slow decay), sham (fast decay), bare (fastest). The **gap between corrected and sham is shaded and labeled with the growing number** (+0.054 → +0.341). ELI5: "each round sweeps up that round's mistakes, so the fixed qubit ages slowly while the un-fixed one falls apart."

**Panel D — The court (receipts & fences).** (1) DETECT vs CORRECT — the whole point: Shields *discarded*, this *keeps the run*. (2) The clean control — sham = same circuit, fix off (no Exp239 confound). (3) The honest fence — error-*detected* / injected errors / distance-2–3, the *mechanism* not a below-threshold fidelity; a single fix is classically simulable.

---

# EXHIBIT 2 — The Programmable Rotation

## 1. Goal & the "aha"
A **Bloch-sphere equator dial**. Pick a logical-Clifford "program" — **I / S̄ / Z̄ / S̄Z̄** — and watch the protected qubit's injected-**T** ("magic") state rotate to land on that program's target around the equator (45° / 135° / 225° / 315°). Then flip the injected resource from **T (magic)** to **S (an ordinary Clifford)** and watch the point **collapse onto the Ȳ axis** — the falsifier that proves the magic was doing the work.

**ELI5 aha**: "A protected qubit you can *program* to point anywhere on a dial. That 'anywhere' is what makes the computer universal — able to run *any* quantum program, not a fixed few."

## 2. Data — verified (Exp246, job `d9f7p7phtsac739f27hg`, `ibm_fez`, 10 circuits, 8000 shots, 2q depth 18–23)
Measured ⟨X̄⟩, ⟨Ȳ⟩ of the injected magic state after each logical-Clifford wrapper W (postselect XXXX_A & ZZZZ_B & m=0; ⟨Ȳ⟩ read as S̄†-then-X̄):

| ancilla | wrapper W | ⟨X̄⟩ | ⟨Ȳ⟩ | equator target | ideal |
|---|---|---|---|---|---|
| **T (magic)** | I | +0.701 | +0.673 | **45°** | (+0.71, +0.71) |
| **T** | S̄ | −0.687 | +0.709 | **135°** | (−0.71, +0.71) |
| **T** | Z̄ | −0.683 | −0.667 | **225°** | (−0.71, −0.71) |
| **T** | S̄Z̄ | +0.695 | −0.705 | **315°** | (+0.71, −0.71) |
| **S (Clifford falsifier)** | I | +0.020 | +0.967 | **on the Ȳ axis** | (axis) |

**G1 (programmable rotation)**: the four T-wrappers land at the four *diagonal* equator points, each |⟨X̄⟩|,|⟨Ȳ⟩| ≈ 0.67–0.71 with the correct sign pattern (++, −+, −−, +−) — points **no stabilizer (Clifford-only) state can occupy**. **G2 (falsifier)**: swap the T for a Clifford S and the state collapses to the Ȳ axis (+0.02, +0.97) — the magic resource was load-bearing.

## 3. Panels
**Panel A — The Dial (interactive, the star).** A Bloch-sphere top-down view of the equator (a circle; X̄ axis horizontal, Ȳ axis vertical). Four **program buttons** (I / S̄ / Z̄ / S̄Z̄). Selecting one animates a vector rotating to the measured target dot (with the ideal target as a faint ring). A **resource toggle: T (magic) ↔ S (Clifford)** — flip to S and the four dots all collapse onto the top of the Ȳ axis, with the caption "no magic → no reach: stuck on the stabilizer axis." Read-out shows measured (⟨X̄⟩,⟨Ȳ⟩) and the target angle.

**Panel B — Why this = universal (ELI5 + the ladder).** A short visual: **Clifford gates alone = a cheap calculator** (fast, but classically simulable, can't reach the diagonal points). **Clifford + T = a universal computer** (can approximate *any* rotation). Show the four reachable diagonal points lighting up the "off-axis" region a Clifford can never enter. Tie to Exp244 (the gate set *closed*) → Exp246 (the gate set *dialed*).

**Panel C — The court (receipts & fences).** (1) The falsifier (S collapses to axis) is the un-fakeable part. (2) How the byproduct is handled honestly (postselect m=0; ⟨Ȳ⟩ rotated into the robust X̄ basis via S̄†). (3) The fence: error-*detected*, a single injected T is classically simulable — this is universality's *mechanism*, not a supremacy claim.

---

## 4. Gap review (v1) — revisit for gaps

| # | gap / risk | fix |
|---|---|---|
| G1 | **"Fault tolerance" overclaim** (the classic trap) | Copy says error-**detected** / injected errors / distance-2–3 everywhere; the words "below-threshold" and "supremacy" appear only in the *fence* saying we do NOT claim them. Mirror the README's own scope language. |
| G2 | **Self-Healing: mixing 4 experiments could confuse** | One clear stage progression A→B→C→D with a one-line ELI5 per stage; each stage's job ID on its card. Panel A's code-toggle makes the 3-qubit→Shor jump explicit (why Y/Z only work on Shor). |
| G3 | **Repeated-rounds gap could look like cherry-picking** | Always show the **sham = identical circuit, fix OFF** caption beside the gap; state the Exp239 confound was built out (control lives inside the circuit). |
| G4 | **Bloch "equator dial" could over-promise a full sphere** | Label it clearly: the *equator* (the non-stabilizer targets we dialed), 4 measured points; ⟨Z̄⟩ (pole) not the story here. Ideal targets shown as faint rings so measured-vs-ideal is visible (not hidden). |
| G5 | **Magic/Clifford is jargon** | ELI5 twin everywhere: Clifford = "cheap calculator moves (classically simulable)", T/magic = "the special ingredient that unlocks *any* rotation." The falsifier is framed as "turn the magic off → watch the reach vanish." |
| G6 | **Numbers could drift from source** | Data kernels are pasted verbatim from the status docs with sanity asserts (§5); every displayed number must match §2 exactly. |
| G7 | **House rules** (a11y / mobile / theme / measured-only / label overflow) | Reuse the museum's proven idioms (switch-bench, shields): theme toggle, keyboard-operable buttons, `aria-live` on result readouts, responsive SVG, "MEASURED · job ID" footer. Design out the two known label-bug classes (right-edge overflow; value-near-threshold collision). |

## 5. Pre-dev structure (standard form)

1. **Data kernels** (paste from status docs; sanity asserts):
   - Self-Healing: `SH = { exp236:{...table...}, exp238:{floor:0.914,corr:0.782,unc:0.107,bare:0.005}, exp240:{live,dest,match}, exp241:{R:[0..4], corr:[...], sham:[...], bare:[...], adv:[...]} }`. Asserts: exp241 advantage monotone increasing; exp236 worst ≥ 0.90; exp240 live ≫ destructive.
   - Rotation: `ROT = { T:{I:[.701,.673], Sbar:[-.687,.709], Zbar:[-.683,-.667], SbarZbar:[.695,-.705]}, S:{I:[.020,.967]} }`. Asserts: each T-target radius ≈ 0.67–0.71; sign pattern ++,−+,−−,+−; S collapses to Ȳ axis (|X̄|<0.1, Ȳ>0.9).
2. **Components** (reuse museum idioms): qubit-dot row + pulse animation (new, small); meter/bar/curve SVG helpers (reuse switch-bench gauge + shields curve); Bloch-equator circle + rotating vector (new, small, pure SVG/trig — no libs).
3. **Build order**: Self-Healing first (data-heavy, reuses gauges), then Programmable Rotation (one new SVG idiom, the dial). Both self-contained single-file `index.html` (inline CSS/JS), CSP-safe, no external libs — matches every existing exhibit.
4. **Wing integration**: add **WING VIII — The Living Ship** section to `demo/index.html` with two cards ("The Self-Healing Qubit" · tag `Exp236–241`, "The Programmable Rotation" · tag `Exp246`); wing accent = **emerald/green** (healing) to distinguish from cyan/violet/amber/rose already in use.
5. **Stub-run validation** (no Playwright here → substitute): extract inline JS, `node --check` for syntax; DOM-mock harness executes each exhibit's render in every interactive state (each error type; each program; each toggle; each round) → assert no runtime error and every displayed number ∈ §2.

## 6. Acceptance
- Both exhibits self-contained, theme-aware, keyboard-operable, mobile-responsive; every number traces to §2 and a job ID in the footer.
- Self-Healing: inject X/Y/Z animates syndrome→heal; code-toggle switches 236↔238 honestly; repeated-round slider shows the growing gap with the sham caption.
- Rotation: four programs dial to the four measured targets; the T↔S toggle collapses to the axis (the falsifier).
- The fence (detected / injected / not-below-threshold / not-supremacy) is visible on both.
- Wing VIII added with two cards + emerald accent; JS syntax-checked; DOM-mock render clean in all states.
