# The Untrusted Relay Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4867 · **For**: `demo/relay-key/` (quantum-network wing, capstone)
**Findings**: finding-exp180-relay-key.md (job `d9e15q1htsac739dm7i0`) · context: Exp162 swap,
Exp177 frame, Exp178 echo, Exp179 merged window · sister exhibits: `subspace-channel/` (keys with
no relays), `relay-computer/` (the stack that makes this possible).

## 1. Goal & the "aha"

Secret keys delivered **through relay stations a spy might run** — and it doesn't matter. The
exhibit's one-sentence physics: the CHSH score S is a spy-meter — **no eavesdropper, no classical
fake, no pre-scripted relay can push S above 2; only genuine end-to-end entanglement can** — and
our relay-built links score 2.31 (one relay) and 2.24 (two relays). The visitor's journey:
select more relays → watch S descend toward the red line but stay certified → then click the
falsifier and watch the whole thing die (S→0, key→coin flips). Secondary "aha" (the ghost, this
wing's recurring motif): the model **predicted the two-relay key would fail** (S=1.97, Werner
pricing) — the measured 2.24 beat it because our noise is lopsided, and the lopsidedness
*protects the key basis*. A structured thing must not be priced by one number.

## 2. Data — verified first (`results/exp180_relay_key_decode.json`)

| arm | S ± se | σ over classical 2 | QBER | role |
|-----|--------|---------------------|------|------|
| direct | 2.607 ± 0.017 | +35.8 | 1.4% | no-relay ceiling |
| key1relay | 2.307 ± 0.018 | +16.8 | 8.2% | **certified through 1 relay** |
| key2relay | 2.235 ± 0.019 | +12.7 | 10.6% | **certified through 2 relays** |
| nomeas | −0.010 ± 0.022 | — | 49.9% | falsifier (no entanglement) |

Model panel numbers: Werner point prediction **1.97** (pre-registered band 1.85–2.10) → measured
2.235; structured-noise formula S = √2(⟨ZZ⟩+⟨XX⟩) applied to Exp179's own mergedecho
correlations (0.787 + 0.663) → **2.05** (a violation our data already contained); remainder
2.05 → 2.235 = favorable condition swing (stated as such, never attributed to the formula).
Per-term E values live in the decode JSON (`E` dict per arm) if the S-meter wants a breakdown
tooltip. All numbers rendered from a data kernel copied verbatim from the decode JSON — no
recomputation in JS.

## 3. The exhibit — two panels

**A — The Spy-Meter (interactive).** A 4-way arm selector styled as the link map it is:
`[direct] [● 1 relay] [● ● 2 relays] [no entanglement]`, each showing a tiny topology sketch
(Alice — relay dots — Bob; the falsifier drawn with the entanglement links severed).
Main viz, left: a vertical **S-gauge** from −0.2 to 2.9 with two theorem lines — **red dashed at
2.0** ("classical / any spy caps here" — the load-bearing line) and faint at **2√2 ≈ 2.83**
("Tsirelson: quantum's own ceiling") — marker with ±se whisker and σ-over-2 label.
On key2relay only: the **ghost marker at 1.97** ("the Werner model said: fails") sitting *below*
the measured point — deliberate inversion of the relay-computer exhibit's ghost (there the model
was optimistic; here pessimistic; same lesson, encode the structure).
Right: the **key stream** — two aligned bit rows (Alice / Bob), ~40 bits, mismatches flagged in
amber; agreement rate printed as the measured QBER. Stream is deterministic (seeded PRNG at the
measured QBER rate) and labeled *"illustrative stream at the measured error rate — the real key
bits are 8 000 shots in the decode file."* On the falsifier arm the stream is ~50% mismatch
chaos and the verdict flips.
Verdict boxes: certificate (S vs 2, σ), key quality (QBER vs the 11% folk threshold, labeled as
folk threshold), and arm verdict ("CERTIFIED — no spy possible above this score" / "DEAD LINK —
the magic was the entanglement").

**B — The court (4 receipts).**
1. *WHY THE RELAY CANNOT SPY*: after its Bell measurement the relay holds **no qubit correlated
   with the key**; it publishes its outcomes to everyone; and S>2 bounds **every** eavesdropper
   strategy by physics, not by trust. The witness is the security proof.
2. *FRAME-STEERED SIFTING*: CHSH angles are non-Clifford, so relay outcomes can't be XORed away —
   the conjugation rule (flip by (−1)ˣ, steer Bob's angle by x⊕z) re-sorts every shot into a
   valid CHSH term. This is *how* repeater QKD folds published relay outcomes into sifting —
   derived from our own frame algebra, selftest-exact. `code: (-1)^x A((-1)^(x^z) θ)`
3. *THE MODEL THAT FELL*: pre-registered Werner point 1.97 (no violation) → measured 2.235
   certified. Decomposed: S = √2(ZZ+XX) for dephasing-structured links (our Exp179 correlations
   already predicted 2.05) + a favorable condition swing. The ZZ surplus dephasing leaves intact
   buys CHSH margin AND keeps Z-basis key errors low — **dephasing-limited links are better key
   carriers than their fidelity suggests.**
4. *WHY IT MATTERS & THE FENCE*: this is the quantum internet's purpose, end-to-end on one die.
   Fence: raw sifted bits + CHSH certificate (Ekert's security layer) — no error correction, no
   privacy amplification, no authenticated channel; chip patches, not stations; the 2.235
   includes a condition swing — the certified claim rests on the 12.7σ margin, not the point.

## 4. Gap review — v1 → v2

| # | Gap | Fix |
|---|-----|-----|
| G1 | "Spy-proof" overclaim. | Copy says S>2 bounds eavesdropping on the *entanglement* under E91's standard assumptions; the fence receipt names what's absent (EC/PA/auth, device assumptions). Never "unhackable." |
| G2 | Key stream honesty. | Bits are an illustrative seeded stream at the **measured** QBER; labeled as such in-place; real sample size (8 000 shots/setting) stated. No pretending we're showing actual key material. |
| G3 | Model-fall attribution. | The ghost panel splits the 1.97→2.235 gap into structural (→2.05, formula, from *prior-flight* data) and conditions (→2.235); the formula is never credited with the full gap. |
| G4 | Two theorem lines confusion. | Red line at 2 = the certificate (heavy, labeled "any spy caps here"); Tsirelson 2.83 = faint context line ("quantum's own max") so visitors don't read 2.83 as the pass mark. |
| G5 | σ literacy. | Each arm prints "(+16.8σ)" with a plain-word gloss on first render: "the odds this is classical noise are astronomically small." |
| G6 | a11y / mobile / motion / theme. | Arm selector = buttons with aria-pressed; verdicts in text+color (color never alone); stream mismatches get a shape marker (▲) not just amber; panels stack <680px; instant redraws; light/dark via museum.css vars. |
| G7 | Measured-only. | S, se, σ, QBER from the decode JSON verbatim; E-term tooltip data from the same file; ghost values from the pre-registration (quoted, dated). No invented numbers anywhere. |

## 5. Pre-dev structure

1. **Data kernel**: `ARMS` object pasted from exp180_relay_key_decode.json {S, se, sigma_over_2,
   qber} + `GHOST` {werner: 1.97, structured: 2.05, band: [1.85, 2.10]}; sanity-asserts
   (ordering direct>key1>key2, falsifier |S|<0.15). 2. Panel A: S-gauge SVG (reuse the
   relay-computer gauge idiom incl. ghost-marker code), topology sketches, seeded key-stream.
   3. Panel B receipts. 4. Chrome: museum.css, topbar, foot links (subspace-channel,
   relay-computer, swap, index), card added to index.html network wing (tag: Exp180 · 16.8σ).
   5. Passes: JS stub-run all 4 arms, a11y, mobile stack, self-contained, both themes.

## 6. Acceptance

Four arms selectable; S markers land at 2.607/2.307/2.235/−0.010 with correct se whiskers and σ
labels; red classical line at exactly 2.0, Tsirelson faint at 2.83; key2relay shows the 1.97
ghost *below* the measured marker with the two-step decomposition; key stream mismatch rate
visually ≈ measured QBER per arm and flips to chaos on the falsifier; all verdict boxes correct
per arm; keyboard-operable, color-not-alone, mobile-stack, no external requests, theme-aware;
every displayed number traceable to the decode JSON or the dated pre-registration.
