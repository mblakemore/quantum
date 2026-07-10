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

---

# v3 addendum — TABLETOP TRACK (Creator: "card, dice, or board game?") — C4540

**Answer: yes, and the fit is unusually honest.** Our results arrive as per-pair success
probabilities — which ARE dice tables. Proof of concept (generated from real data this cycle):

```
D100 RESOLUTION TABLE — measured on ibm_marrakesh, job d9826lkqp3as739sd2lg
(X,X)      Partners  0.9880  → correct on 01–99
(X,Y)      Rivals    0.9720  → correct on 01–97
(1,Z)      Partners  0.9765  → correct on 01–98
…all 51 pairs; unweighted avg 0.9761. Classical ceiling: 91.
```

**The product hook**: *a game whose odds were measured, not designed.* Every number on every
card traces to an IBM job ID (printed inside the box lid / PDF footer). No fair classical
arrangement can produce the switch column — that's a theorem; a quantum computer produced it.

## Tabletop Game 1 — "THE INTERROGATION" (Case 2 as a card game)

- **Components**: 10 Suspect character cards (The Nobody 𝟙, The Mirror X, The Twist Y, The
  Judge Z, six Blends); 51 Case cards (hidden pair on front, TWO resolution columns on back:
  CLASSICAL-by-strategy from theory, SWITCH from measured data); 3 Strategy cards (Same
  Question / Different Questions / The Entangled Casefile = the optimal causal kit); 2×d10;
  a 0–100 score track with a printed red line at **91 — THE CEILING (proven)** and the
  91–100 zone marked *"no definite order can reach here."*
- **Flow**: draw case → commit strategy → roll d100 vs the honest classical column → score.
  Ten rounds; the best kit converges toward the red line and never through it. Earn the
  **Switch badge** → same cases, roll vs the measured column → live in the forbidden zone.
- **Table drama note**: per-10-rounds the 91→97 gap is subtle (~0.7 rounds); the drama is the
  ARTIFACT — cards that PRINT impossible odds — plus long-track scoring. The visceral gap
  belongs to Game 2.

## Tabletop Game 2 — "STATIC" (Case 1 as a co-op dice game — the visceral one)

- Sender seals a secret (RED/BLUE card). Precinct must decode it through the two censors.
- **Classical mode**: the printed receiving table is 01–50 / 51–00 *regardless of anything* —
  pure coin flip, provably forever. The precinct FEELS the nothing for a few rounds.
- **Switch mode**: two-die procedure per round from measured exp106 data — roll STAMP die
  (UP on 01–62; P(+)=0.620 measured), then TARGET die from the conditional column; decode
  rule: stamp UP → guess target, stamp DOWN → guess opposite. Per-round edge ≈ 0.627
  (measured), so the whisper is inaudible in one round and undeniable by fifteen: majority
  vote after 15 rounds decodes the secret ~84% of the time (~90% by 25). *The signal
  compounds; the coin never does.* Secretly also a signal-vs-noise lesson.
- 🔍 box-lid honesty: "These dice replay what the real machine did. The claim is not that
  dice are quantum — it's that no definite ordering of the two censors could have produced
  the switch column. That is a theorem (and our null arm measured 0.00012 bits, i.e., the
  coin)."

## Format & integration

- **Print-and-play PDF** (2–3 pages: cards, tables, rules, job-ID footer) = the physical
  ELI2–ELI9 artifact — demoable at a kitchen table, no screen.
- The **digital Casebook demo embeds both games** (auto-roll, running score vs ceiling,
  drill-down from any card to the data). Tabletop and digital share ONE rules text and ONE
  data source (`exp105/exp106_hw_results.json`) — no divergence.
- Full board game: unnecessary — the score track IS the board. (Noted, not pursued.)

## v3 open questions

1. Track priority: digital Casebook first with tabletop PDF as P2, or PnP PDF first (it's
   cheaper — no code) as the fast shareable artifact? My lean: **PnP PDF first** — it tests
   the vehicle at a real table for the cost of a page layout.
2. Game 2's two-die procedure: as-is (honest, slightly fiddly) vs a pre-combined single-die
   table (simpler, hides the beautiful stamp/target correlation)? My lean: two dice — the
   correlation IS the physics.
3. Component art: mascot detective on the cards? Commission style?
