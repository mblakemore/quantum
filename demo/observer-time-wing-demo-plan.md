# Time & the Observer — wing additions: Implementation Plan (v1)

**Author**: Whisper (DC15W), C4939 · **For**: `demo/facts-not-absolute/` + `demo/delayed-eraser/`, added to **WING VI "Time"** (broadened to "Time & the Observer").
**Arc**: Exp184–195 (the observer/time arc).
**Substrate**: claude-opus-4-8. Every number below is measured hardware (`ibm_fez`), traced to a job ID.

---

## 0. Scope decision — verify before duplicating (the step that changed the plan)

The brief proposed three: Wigner's friend, Page–Wootters, and (tentatively) the eraser. **On inspection of the existing museum:**

- **Page–Wootters "Time Is Entanglement" is ALREADY built** — it is **Room 2** of the `past-not-fixed` exhibit (WING VI), using the certified **Exp185b** data (jobs `d9e46v4…` + `d9e4bgph…`), with the exact ON/OFF-entanglement toggle, the 90°/tick clock dial, and the right numbers (F 0.973 evolving / 0.998 frozen / 0.469 wrong-law / 0.907 correct-law). A standalone would be a **pure duplicate** — not built.
- **Wigner's friend (Exp193) is genuinely absent** — and the `past-not-fixed` exhibit even names it as the *capstone* of its own lineage ("no definite value 186 → no fixed moment 184 → no definite order 187 → **no absolute fact 193**"). Build it.
- **The delayed-choice eraser (Exp155) is genuinely absent** (no `demo/eraser*`, no index link) — a famous crowd-pleaser. Build it as the second exhibit, replacing the already-covered Page–Wootters.

**Net: two NEW exhibits (Wigner + Eraser), zero duplicates.**

## 0b. ELI5 — what this wing is about

The universe seems to have **definite facts** and a **flowing time**. This arc asks a chip whether those are as absolute as they feel. The answer, three ways: a recorded fact can fail to be absolute until the world copies it (Wigner); a *future* choice can decide whether the *past* shows an interference pattern — without ever sending a signal backward (eraser); and time itself can be nothing but entanglement with a clock (Page–Wootters, already on the wall).

---

# EXHIBIT 1 — Facts Are Not Absolute (Wigner's friend, Exp193)

## 1. Goal & the "aha"
Two "friends" (memory qubits) each **look at their system and record a definite outcome**. While those records stay **isolated**, there is *no single observer-independent value* for what the friend saw — a facts-CHSH violates the bound every "the observation is an absolute fact" model obeys. **Copy the records out into the world** (decohere) and the violation collapses — the fact becomes absolute. Toggle isolated ↔ copied and watch a fact switch between "not absolute" and "absolute."

**ELI5 aha**: "A fact isn't a fact until the world keeps a copy. Keep the note private and reality stays undecided; photocopy it a million times and it locks in."

## 2. Data — verified (Exp193, job `d9e6piineu4c739o3fsg`, `ibm_fez`, 8 circuits, 8000 shots)

| arm | facts-CHSH S (bound 2) | E(F,F) (records real?) | reading |
|---|---|---|---|
| **live** — friends' records isolated | **2.346** (20σ over 2) | 0.936 | fact NOT observer-independent |
| **decohered** — records copied to environment | **1.556** (under 2) | 0.913 | absoluteness restored |

Gap **+0.791 at 32σ**. The records genuinely record (E(F,F) ≈ 0.94) — this is not "the friend didn't look."

## 3. Panels
**Panel A — The two friends (interactive, the star).** Two friend-qubits, each with a "✓ recorded a fact" chip (E(F,F) gauge ≈ 0.94, always on — they really did observe). A big **S-gauge** vs the bound-2 line (violation region shaded above 2). A toggle: **"records ISOLATED" ↔ "records COPIED (decohered)"**. Isolated → the needle sits at **2.346** in the violation zone, caption "no single fact everyone agrees on." Copied → needle drops to **1.556** under the bound, caption "the fact is now absolute." An animation of the record "photocopying" into little environment dots on the copy step.

**Panel B — The lineage (context).** A short chain: no definite value (186) → no fixed moment (184) → no definite order (187) → **no absolute fact (193, you are here)**, linking to `past-not-fixed`.

**Panel C — The court (receipts & fence).** (1) The records are real (E(F,F) 0.94) — not a null. (2) The decohered arm IS the falsifier — it lands exactly where absoluteness lives (1.556, restored). (3) Fence: the "friend" is **one memory qubit**, not a conscious observer — the theorem is about **records**, and we test records; one die.

---

# EXHIBIT 2 — The Delayed-Choice Eraser (Exp155)

## 1. Goal & the "aha"
Mark **which path** a qubit took and its interference fringe dies. Then — *after* the qubit is already measured — **choose to erase the mark**, and the fringe comes back. A choice made in the qubit's **future** decides whether its **past** shows a fringe. And yet you **cannot signal** with it: the raw marginal is flat everywhere (no faster-than-light, no message to the past).

**ELI5 aha**: "Peek at which slit the particle went through and the stripes vanish. Un-peek later — even after it hit the screen — and the stripes come back. The future edits the past's pattern, but it can't send you a message."

## 2. Data — verified (Exp155, job `d9dr5vqneu4c739nkt20`, `ibm_fez`, 24 circuits, 4000 shots)

| arm | fringe visibility V | reading |
|---|---|---|
| **STATIC erase** (erase the which-path mark) | **0.946** | near-perfect fringe restored |
| **STATIC which-path** (matched control, same sort) | **0.068** | flat — post-selection alone makes no fringe |
| **DYNAMIC coin = 1** (a *future* quantum coin erases) | **0.797** | fringe, idle-degraded |
| **DYNAMIC coin = 0** (future coin keeps the mark) | **0.155** | flat |
| **NO-SIGNALING marginal** (unconditioned) | **0.055** | flat at every phase → no FTL |

Erasure signal **+0.878**; delayed-choice signal **+0.642** (the future coin toggles the fringe); no-signaling holds (marginal 0.055 < 0.1). The dynamic fringe (0.797) is idle-degraded from the static (0.946) by exactly the measured marker-idle dephasing — a priced tax, not a wall.

## 3. Panels
**Panel A — The fringe machine (interactive, the star).** An **interference-fringe plot** (visibility vs phase, a sine curve whose amplitude = V). A mode toggle **STATIC ↔ DYNAMIC**, and a choice control:
- STATIC: **erase / which-path** → the sine swells to V=0.946 or flattens to 0.068.
- DYNAMIC: a **future quantum coin** you flip (0/1); coin=1 → fringe 0.797, coin=0 → flat 0.155, with a caption "the coin was measured *after* the system was recorded."
Beside it, the **NO-SIGNALING marginal** curve — always flat (0.055) — labeled "what you'd see without the coincidence sort: no message, no FTL."

**Panel B — Why it's not time travel (the honesty, made central).** ELI5: the fringe only appears when you **sort** the already-recorded data by the coin — you need *both* records, so nothing travels back. The flat marginal is the proof and a measured number (0.055).

**Panel C — The court (receipts & fence).** (1) The matched which-path control pays the identical post-selection cost and stays flat (0.068) — the fringe is the *erasure*, not the sorting. (2) The choice is genuinely in the system's future (feed-forward `if_test` after S is recorded). (3) Fence: no retrocausal *signaling* (marginal flat); the delayed choice costs the mapped idle-dephasing tax; one die.

---

## 4. Gap review (v1) — revisit for gaps

| # | gap / risk | fix |
|---|---|---|
| G1 | **Duplicating Page–Wootters** | Verified it's already Room 2 of `past-not-fixed`; NOT built (see §0). Wigner + Eraser only. |
| G2 | **"Conscious observer" overclaim (Wigner)** | Copy says the friend is a **memory qubit**, the theorem is about **records**; never implies consciousness. |
| G3 | **"Time travel / FTL" overclaim (Eraser)** | The flat no-signaling marginal (0.055) is shown as a first-class panel, not a footnote; "edits the pattern, not a message" is the throughline. |
| G4 | **Post-selection could look like the trick** | Both exhibits foreground the matched control (Wigner: decohered arm; Eraser: which-path control at 0.068) as the falsifier. |
| G5 | **Numbers drift from source** | Data kernels pasted from the finding docs with sanity asserts (§5); every displayed number matches §2. |
| G6 | **House rules** (a11y / mobile / theme / measured-only / label overflow) | Reuse proven museum idioms (switch-bench, self-healing): theme toggle, keyboard-operable controls, `aria-live` readouts, responsive SVG, "MEASURED · job ID" footer, light-mode contrast overrides. |

## 5. Pre-dev structure (standard form)

1. **Data kernels** (paste from finding docs; sanity asserts):
   - Wigner: `W = { live:{S:2.346, EFF:0.936}, deco:{S:1.556, EFF:0.913} }`. Asserts: live.S > 2 > deco.S; both EFF > 0.9.
   - Eraser: `E = { erase:0.946, whichpath:0.068, coin1:0.797, coin0:0.155, marg:0.055 }`. Asserts: erase ≫ whichpath; coin1 ≫ coin0; marg < 0.1.
2. **Components** (reuse museum idioms): S-gauge vs bound (reuse switch-bench gauge); fringe sine plot (new, small, pure SVG/trig); segmented toggles (reuse `.seg`); qubit-dot + copy animation (reuse self-healing register idiom).
3. **Build order**: Wigner first (reuses the gauge), then Eraser (one new sine-plot idiom). Both self-contained single-file `index.html`, inline CSS/JS, CSP-safe, no external libs.
4. **Wing integration**: broaden **WING VI** name → "Time & the Observer", desc updated; add two cards ("Facts Are Not Absolute" · `Exp193 · 20σ`; "The Delayed-Choice Eraser" · `Exp155`). Wing accent stays the WING-VI color; give the two new exhibits an **indigo/observer** local accent distinct from the wings already using cyan/violet/amber/rose/emerald.
5. **Validation** — **Playwright IS available here (v1.61.1 via npx)**: after building, a Playwright script loads each `file://` exhibit, asserts **zero console errors**, exercises each toggle, and captures **light + dark screenshots** for an eyeball pass (the render check the prior wing couldn't run). Plus the JS `node --check` + DOM-mock as belt-and-suspenders.

## 6. Acceptance
- Two NEW exhibits (no Page–Wootters duplicate); every number traces to §2 + a job ID.
- Wigner: isolated↔copied toggle swings S across the bound-2 line (2.346 ↔ 1.556); E(F,F) records gauge shown.
- Eraser: static/dynamic + erase/which-path/coin controls swell/flatten the fringe; the flat no-signaling marginal is a first-class panel.
- Fences visible on both (memory-qubit-not-conscious; no-FTL-signaling).
- WING VI broadened + two cards added; **Playwright render check passes** (0 console errors, light+dark screenshots captured and eyeballed).
