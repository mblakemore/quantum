# The Pocket Dictionary Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4699 · **For**: `demo/pocket-dictionary/` (Wing IV)
**Finding**: F107 (Exp128) — the 2→1 QRAC: two bits packed into one qubit, either retrievable at 0.84893, above the classical packing ceiling 0.75 and inside the quantum band (below cos²(π/8)=0.8536). Zero two-qubit gates.
**Upstream**: `demo/pocket-dictionary/spec.html` — the Full Spec Sheet, linked prominently.

> **Process (C4693 upgrade):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.
> **Wing IV accent = cyan.** advantage=good/cyan, classical=amber, band shaded. **Design out SVG-label-overflow (HTML labels + centered SVG text).**

## 1. Goal & the "aha"
Alice packs 2 bits into 1 carrier; Bob asks for EITHER bit (after receiving) and looks once. A classical bit caps at
75% (store one, guess the other). A qubit — two bits encoded as angles — lets Bob be right ~85% for EITHER bit. YOU
play Bob: pick Alice's message and which bit to read, and watch the retrieval beat the classical 75% wall — but stay
under the quantum law 0.8536 (two-sided honesty).

## 2. Data — verified first (results/exp128_hw_results.json, job d9al7om6hjac73fejisg)
8 cases (msg × which-bit), p = P(correct):
| msg | read bit1 | read bit2 |
|---|---|---|
| 00 | 0.84325 | 0.84455 |
| 01 | 0.84345 | 0.84940 |
| 10 | 0.85300 | 0.85410 |
| 11 | 0.85650 | 0.84715 |
- **pooled quantum 0.84893 ± 0.00090** = 110.5σ over classical 0.75, 5.2σ under quantum law cos²(π/8)=0.8536 (inside band).
- classical arm 0.74818 (honors its own 0.75 law). worst case 0.84325 (W2_MIN 36.3σ, every case above wall).
- Gates W1_QRAC/W2_MIN/G_QBAND/G_CLASS/G_SENT all PASS. Zero two-qubit gates. Sentinels 0.998/0.995.

## 3. The exhibit — panels
**A — You're Bob (interactive).** Alice's message selector (00·01·10·11) + Bob's query toggle (read bit 1 / bit 2) →
a success gauge on a [0.5,0.9] band with the classical WALL 0.75 and the quantum LAW 0.8536 marked, defining the
advantage band. Marker lands at that case's p (0.843–0.857), inside the band, above the wall. A mode toggle "use a
classical bit" drops the marker to 0.75. Big readout: "✓ retrieved 85% — beats the classical 75% wall". Show the qubit
encoding schematically (4 messages → 4 angles) as a small Bloch-diagonal glyph.

**B — Inside the band (chart).** The two-sided story: classical wall 0.75, quantum law 0.8536, the band between, the
pooled quantum 0.849 landing inside (110σ over wall, 5.2σ under law), and the executed classical arm at 0.748. One
glance: above classical, below the quantum ceiling — real physics.

**C — Receipts.** (1) the 0.75 ceiling is enumerated over 256 strategies (proven); (2) two-sided gate G_QBAND — over
the law would be flagged apparatus-error, so inside-the-band = certified physics; (3) both laws honored on one chip +
zero two-qubit gates. Scope pill (coding advantage not speedup). Spec link.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "QRAC / random access code" is jargon. | Primer + the "pocket dictionary" metaphor: cram 2 entries into 1-entry space, look up either. Success = P(Bob right). |
| G2 | Why is 75% the classical limit? | Primer: one classical bit stores one bit faithfully + guesses the other → 75% averaged; enumerated over 256 strategies = exactly 0.75. |
| G3 | Beating classical alone looks like "just a big number". | Panel B two-sided band: mark the quantum LAW 0.8536 too; the result must land BELOW it. G_QBAND receipt: over-law = apparatus error. |
| G4 | Could read as data compression / free storage. | Scope: it's a probabilistic random-access advantage (~85%, not perfect), a coding advantage not a speedup; Bob gets EITHER bit ~85%, not both perfectly. |
| G5 | "Either bit" property (the whole point) easy to miss. | Make Bob's bit-choice a live toggle; show it works for BOTH bits and ALL messages (8 cases all above wall). |
| G6 | a11y / mobile / motion / self-contained. | Selector + toggles = buttons (aria-pressed); success % in text + colour + word; band marks in text; stack <680px; gauge transition honours reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context (Creator standing request). | "What's a QRAC?" + "Why can't a classical bit do it?" primer cards after the lede. |
| G8 | Spec discoverability. | Cyan "◇ Full Spec Sheet" button in hero + Panel C + footer. |

## 5. Pre-dev structure
1. **Data kernel**: CASES {msg:{bit1,bit2}} + WALL 0.75 + LAW 0.8536 + POOLED 0.84893 + CLASSICAL 0.74818; assert all cases>wall, pooled in band.
2. Panel A: msg selector + bit toggle + classical toggle → gauge on band. 3. Panel B: static two-sided band chart.
4. Panel C: receipts + spec. 5. Chrome (museum.css, cyan; advantage=good, classical=amber). 6. Passes (labels overflow-proof).

## 6. Acceptance
Message selector + bit toggle drive the gauge to each case's p (0.843–0.857) inside the band; classical toggle → 0.75;
readout states retrieved % + beats-wall; Panel B shows wall+law+band+pooled+classical arm with σ; Panel C carries
enumerated-bound + two-sided-gate + both-laws/zero-2q and links spec; keyboard-operable, colour-not-alone, mobile-stack,
no external requests, theme-aware; NO SVG right-edge label overflow. Then: Playwright render (0 console, 0 external,
toggles vary readout, light+dark) → UI improvement pass.
