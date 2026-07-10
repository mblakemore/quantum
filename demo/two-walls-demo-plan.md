# Demo Plan v2 — "The Casebook of Detective Whisper" (playable detective game, ELI2 → engineer)

**Author**: Whisper (DC15W), C4538 (2026-07-10) — v2 after Creator feedback on v1
(git history has v1). **Changelog v1→v2**: grandma mail-story dropped ("hard sell" — agreed);
vehicle pivots to a **playable detective game**; the Gray Machines survive as the case's
*machinery* (they're now evidence-room censor machines — the metaphor-as-translation analysis
carries over unchanged); the F82 game is promoted from deep-layer exhibit to a **playable case**.

**Subject findings**: F82 (causal game, 216.8σ/201σ) and F83 (capacity activation, 55.6σ) —
now as two playable cases. Real hardware data is the game engine at the deepest difficulty.

---

## 1. The vehicle: a detective casebook with two playable cases

**Detective Whisper** — a small noir-lite cartoon detective (trench coat, big ears; name is a
double signal: a *whisper* is a signal barely above the noise, which is literally the physics,
and it ties the demo to the network that ran the experiments). The visitor is the detective's
new partner. Two cases, playable in either order, each with the age-dial drill-down from v1.

### Case 1 — "The Message That Couldn't Exist" (F83, investigation structure)

A message arrives at the precinct… through TWO censor machines, each of which provably turns
everything into gray static. The player *investigates*:

1. **Test the machines** (interactive): feed anything through censor A, censor B, A-then-B,
   B-then-A, coin-flip order — everything comes out identical gray static. The player exhausts
   the tricks personally (v1's core interaction loop, re-skinned).
2. **Interrogate the evidence**: the arrived "message" alone → static. The delivery stamp
   alone → static. Dead end… until the player **drags the two pieces of evidence together on
   the light table** → the message shimmers into view. *The clue was never IN either piece —
   it lives BETWEEN them.* (Torn-map trope = our measured D≈0 / correlation-carried MI,
   played straight as detective craft.)
3. **Crack the how**: flashback to the mail room — the routing lever stuck in the middle; the
   censors never decided who went first. Case closed screen: "Verdict: the order of events
   itself was never fixed. 0.044 bits escaped through two perfect censors. This really
   happened, on this machine →" [drill-down invitation]

### Case 2 — "The Interrogation You Cannot Win" (F82, game structure — the centerpiece)

The precinct's cold-case: pairs of suspect-machines. The tip-off promise: each pair is either
**Partners** (their stories agree no matter who talks first) or **Rivals** (their stories come
out exactly opposite depending on order). You may question each suspect **once**. Call it.

- **Round play (classical mode)**: pick an interrogation strategy from the detective's toolkit
  (ask both the same question / different questions / the "entangled case-file" kit — the
  optimal causal strategy). The engine computes honest outcome distributions from theory; the
  player's running success rate climbs… and flattens against a drawn red line:
  **"THE CEILING — no detective can ever beat 91%. Proven."** (class-balanced-uniform variant
  of the bound, 0.9098 — chosen over the optimal-q\* game's 0.869 because ½/½ priors make an
  honest, understandable game; the pre-computed bound for exactly this variant comes from our
  own solver run.) Losing to a theorem is the emotional payload — the ceiling is not a
  difficulty setting, and the game says so.
- **Quantum badge (unlocked after ~10 rounds)**: "There is one interrogation room where the
  order of questioning is never decided…" — switch mode ON. Rounds now resolve using the
  **real measured per-pair success rates from `exp105_hw_results.json`** (marrakesh) with a
  fez toggle (`exp105b`). The player's rate climbs THROUGH the red line to ~97%. End screen:
  "You just beat a mathematical theorem, using data from a real quantum computer.
  Job d9826lkqp3as739sd2lg. Here's how →" [drill-down]

## 2. The drill mechanism (unchanged from v1, now wrapped in the casebook)

Age dial `4 · 9 · 16 · undergrad · engineer`; one persistent scene per case that gains truth:

| Dial | Case 1 becomes | Case 2 becomes |
|---|---|---|
| 4 | picture-book: static… static… two pieces together → picture! (tap-through, ≤15 words/screen; no noir vocabulary, just "detective and the sneaky message") | watch-only: Whisper plays 3 rounds, wins with the sparkle lever |
| 9 | the playable investigation above | the playable game above (strategy menu simplified to 2) |
| 16 | why each piece alone MUST be blank (censor = perfect randomizer); the light-table as correlation | why 91% is a *theorem* not a difficulty setting; what "question each once" buys the quantum room |
| undergrad | depolarizing channels, Kraus picture, (ρ+2𝟙)/5 vs (2𝟙−ρ)/3 tint-math, MI meter 0.0489→0.0436 | the commute/anticommute promise, the causal-bound SDP (0.9098 for THIS game variant), DISC(φ) dial |
| engineer | padded 4-CZ skeleton, sentinel gates, per-pair table, job IDs, pre-reg links, Exp107 N=3 status | q\* table, bound-solver notebook link, per-pair measured distributions the game engine uses, frozen grade rules |

**Honesty ladder rule carries over verbatim**: every depth ends with 🔍 "what's really true
here"; each layer is a strict subset of the next layer's truth. Extra rule for game mode:
the engine must never fudge — classical mode uses true theory distributions (the player CAN
reach 91% with the best kit, and the game celebrates that as "perfect detective work"),
quantum mode uses only measured hardware numbers (including their imperfection — the player
tops out ~97%, not 100%, and the 🔍 note says why).

## 3. Build phases (revised)

- **P0-v2 (this doc)**: vehicle sign-off on the detective-game frame. ← WE ARE HERE
- **P1**: Case 2 classical-mode playable + the ceiling moment (the emotional core; build first),
  dial-9 register only. Static mock of quantum-badge screen.
- **P2**: Case 2 quantum mode wired to real exp105 data + fez toggle; dial-4 watch-mode.
- **P3**: Case 1 investigation loop + light-table interaction; dial-16.
- **P4**: undergrad/engineer depths (reuse φ-dial from the switch demo; inline JSON data);
  cross-link with /demo/; Pages deploy at /demo/casebook/.
- **P5 (stretch)**: 90-second auto-play "curator mode"; score-share card ("I beat a theorem").

Form factor unchanged: one self-contained HTML file per the switch-demo constraints
(no external deps, mobile-first, keyboard-accessible, muted-by-default sound).

## 4. Open questions v2

1. **Structure**: two cases as above, or Case-2-only for launch (game is the centerpiece;
   Case 1 could ship in a later update)? My lean: Case 2 first, ship, then add Case 1.
2. **Detective identity**: "Detective Whisper" (network nod) vs a neutral name vs Creator's pick.
   Species/mascot still open (v1's cat wears the trench coat well).
3. **Bound variant for the playable game**: class-balanced 0.9098 (clean ½/½ priors,
   recommended) vs optimal-q\* 0.869 (bigger margin, weirder priors to explain).
4. **Tone ceiling**: how noir is too noir at dial-4? (Current answer: dial-4 drops the noir
   entirely — same cases, picture-book art.)
5. **Score-share**: is the P5 share-card ("I beat a theorem — 97% vs the 91% ceiling")
   wanted, or off-brand?
