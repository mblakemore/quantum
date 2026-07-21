# Beam the Power — Quantum Energy Teleportation: Implementation Plan (v1)

**Author**: Whisper (DC15W), C4940 · **For**: `demo/energy-teleport/`, added to **WING VI "Time & the Observer"** (the Exp184–195 arc's capstone; the Creator's "natural neighbor of the eraser").
**Finding**: Exp195c (CERTIFIED, 9.8σ) — Hotta quantum energy teleportation, isolated as a differential.
**Substrate**: claude-opus-4-8. Every number is measured hardware (`ibm_fez`), traced to a job ID.

## 0. Verify-before-duplicating (the standing step)
- `demo/negative-energy` = **F97** (sub-ground-state *negative* local energy, coherent extraction) — a *different* result; its own QET leg **failed** and is logged there as a LOSS. **Exp195c is the separately-certified QET** and has **no exhibit**. Genuine gap → build.
- `demo/teleportation` = state teleportation; `demo/teleported-witness` = causal-order teleport. Neither is energy teleportation.

## 0b. ELI5 — what this is
Alice and Bob share two qubits in their **ground state** — the lowest possible energy, nothing left to extract locally. Bob, on his own, can pull **no** energy out. But if Alice **measures her qubit** and texts Bob **one bit** saying what she got, Bob can use that bit to **extract energy from his own qubit** — energy that seemingly "teleported" from Alice's side. The twist that makes it real: the bit has to **carry information** about how the two qubits are correlated. Send Bob the **same bit stripped of information** (a coin flip) and he gets **nothing** — in fact his energy goes *up*. **Information is the fuel.** (No faster-than-light: Alice's measurement cost the energy up front; the bit just tells Bob how to claim its share.)

## 1. Goal & the "aha"
Flip between three bits driving Bob's energy-extraction kick and watch his local energy **E_B**:
- **Alice's bit (QET)** — carries information about the A–B correlations → E_B **−1.669** (dips toward the ground line −1.7).
- **A coin (no info)** — gate-for-gate identical circuit, information-free bit → E_B **−1.471** (energy *up*).
- **Fixed kick (no measurement)** — → E_B **−1.509**.
The certified result is the **gap between the two gate-identical arms**: QET − coin = **−0.198 at 9.8σ** (target −0.200). One bit's *information content* alone moves Bob's energy a fifth of a unit downward.

**ELI5 aha**: "Same machine, same wires — the only difference is whether the bit Bob receives *knows something*. When it does, he extracts energy. When it's a coin, he can't. Information carried the energy."

## 2. Data — verified (Exp195c, job `d9e7454jeosc73fie4dg`, `ibm_fez`, 16000 shots)

| arm | what drives Bob's kick | E_B | Δ vs ground baseline (−1.7) |
|---|---|---|---|
| **qet** | Alice's info-carrying bit | **−1.6692** | +0.0308 |
| **coinfrozen** | a coin (no info), same circuit | **−1.4714** | +0.2286 |
| **nomeasure** | fixed kick, no measurement | **−1.5088** | +0.1912 |

- **PRIMARY (certified)**: GAP(qet − coinfrozen) = **−0.1978 ± 0.0202 (9.8σ)**; pre-registered band [−0.30, −0.10], exact target −0.2001 → observed gap is **99% of exact**. The two circuits are **gate-for-gate identical** (same ground prep, same two measurements, same feed-forward window, same kick angles) — the *only* difference is which classical bit conditions Bob's rotation. The common noise-heating subtracts out.
- **FALSIFIERS ✓**: both no-information arms **pay** (+0.2286, +0.1912; band [+0.02, +0.50]) — an information-free bit cannot extract.
- **SECONDARY (honest, not verdict-gating)**: absolute ΔE_B(qet) = **+0.0308** — still noise-heated *above* the ground baseline (a λ>0.943 damping problem this fabric doesn't clear; predicted by 195b's budget). **The certified claim is the differential, not the absolute level.**

## 3. Panels
**Panel A — The three bits (interactive, the star).** An **energy-level diagram**: a "ground state −1.7" reference line at the bottom; Bob's energy **E_B** shown as a marker/bar for the selected arm. A 3-way toggle — **Alice's bit (QET) / coin (no info) / fixed kick**. Selecting QET drops the marker toward the ground line (−1.669); the no-info arms sit higher (−1.47/−1.51). A small **Alice → [bit] → Bob** schematic above: on QET the bit glows "carries info about the correlation"; on coin it's greyed "information-free." Headline chip: the **differential gap −0.198 (9.8σ)** between the two gate-identical arms, always visible.

**Panel B — Why it's information, not magic.** ELI5 + the differential logic: the two circuits are identical gates; subtract them and all the shared noise-heating cancels, leaving only the effect of the bit's *information content* (−0.198, 99% of the exact Hotta prediction). No FTL: Alice's measurement paid the energy cost up front; the bit only tells Bob how to claim it.

**Panel C — The court (receipts & fence).** (1) Gate-for-gate identical arms — the gap is the information, not the wiring. (2) The falsifiers pay (both no-info arms go *up*, +0.19/+0.23). (3) Fence: the **absolute** E_B is still noise-heated above ground (+0.031) — certified claim is the **differential**; the teleported quantity is energy; 5th of the teleportation lineage; one die.

## 4. Gap review (v1)
| # | gap / risk | fix |
|---|---|---|
| G1 | **"Free energy / perpetual motion" overclaim** | Copy: Alice's measurement pays the cost up front; the bit routes the claim. No net free energy; no FTL. |
| G2 | **"Absolute energy extracted" overclaim** | The absolute ΔE_B is +0.031 (still above ground) shown plainly; the certified result is the **differential** between gate-identical arms, foregrounded. |
| G3 | **Duplicating negative-energy** | Verified distinct (F97 vs Exp195c); QET's own leg failed in F97. Linked, not duplicated. |
| G4 | **"Information moves energy" sounds spooky/wrong** | Panel B makes the differential-cancellation logic explicit: identical circuits, only the bit's info differs. |
| G5 | House rules (a11y / mobile / theme / measured-only / label overflow) | Reuse proven museum idioms (facts-not-absolute gauge, self-healing meters); amber "energy" accent + light-mode override. |

## 5. Pre-dev structure (standard form)
1. **Data kernel**: `Q = { qet:{E:-1.6692,d:0.0308,info:true}, coin:{E:-1.4714,d:0.2286,info:false}, fixed:{E:-1.5088,d:0.1912,info:false}, ground:-1.7, gap:-0.1978, se:0.0202, sigma:9.8 }`. Asserts: qet.E < coin.E and < fixed.E (qet lowest); gap ≈ qet.E − coin.E within 0.01; both no-info Δ > 0.1.
2. **Components**: energy-level diagram (new small SVG — ground line + arm markers + gap bracket); 3-way seg toggle (reuse `.seg`); Alice→bit→Bob schematic (small SVG dots + arrow). No libs.
3. **Build order**: single self-contained `index.html`, inline CSS/JS, CSP-safe.
4. **Wing integration**: WING VI, broaden desc to include "can information alone move energy?"; add card ("Beam the Power" · `Exp195c · 9.8σ`). Local accent **amber/gold (energy)**, distinct from the indigo observer exhibits.
5. **Validation**: JS `node --check` + DOM-mock; **Playwright render check** (0 console errors, click all three arms, light+dark screenshots eyeballed — the energy diagram + gap bracket must read correctly).

## 6. Acceptance
- One new exhibit (no duplicate); every number traces to §2 + job ID.
- Three-arm toggle moves E_B (qet lowest toward ground; no-info arms higher); the −0.198/9.8σ differential is the always-visible headline.
- Fences visible (no free energy / no FTL; absolute is noise-heated, differential is the claim).
- WING VI card added; Playwright render check passes (0 errors, light+dark eyeballed).
