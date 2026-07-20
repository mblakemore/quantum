# The both-bases Bell fix: the phase leg that died in 242 is alive on a both-bases code (191 re-analysis)

**Whisper C4921, 2026-07-20. Substrate `claude-opus-4-8`. No new QPU** — a re-analysis of Exp191
(job `d9e64rsjeosc73fid0gg`, ibm_fez) answering the Exp242 phase-blindness, on the advisor's call that
re-flying it would pay twice for no new physics.

## The question 242 raised

Exp242 built a logical Bell pair on the **bit-flip** code and its phase leg died: ⟨Z̄Z̄⟩ = +0.515
(correlation survived) but ⟨X̄X̄⟩ = **+0.000** — because the bit-flip code is *blind* to phase errors
(a single Z gives syndrome 00), so nothing could rescue the coherence. The directive: fix it with a
code that guards **both** bases.

## The resolution (and an honest rediscovery)

A rediscovery check found the fix is essentially **already flown**: **Exp191** made a both-bases
[[4,2,2]] logical Bell pair (transversal CNOT across two shielded blocks, both ⟨Z̄Z̄⟩ and ⟨X̄X̄⟩
measured, postselected on the XXXX/ZZZZ stabilizers). And a key technical fact makes a "live-corrected
Bell pair" on [[4,2,2]] a non-thing: **distance-2 detects but cannot localize → cannot feed-forward
correct.** Postselection is the only option, and for a Bell pair measured immediately, a mid-circuit
non-destructive stabilizer read is *identical* to 191's terminal per-basis postselection — it would
only add depth, no new physics. So the honest deliverable is not a re-fly; it is 191 re-analyzed for
the one contrast it never reported: **raw vs postselected.**

## The result — the both-bases code SEES and REMOVES the phase error 242 was blind to

Exp191 [[4,2,2]] logical Bell pair (L1 entangled across the two blocks), correlators:

| arm | | ⟨Z̄Z̄⟩ | ⟨X̄X̄⟩ | S = ⟨ZZ⟩+⟨XX⟩ | acceptance |
|---|---|---|---|---|---|
| logical | RAW (no postselect) | +0.886 | +0.844 | 1.730 | — |
| logical | **POSTSELECTED** | +0.975 | **+0.995** | **1.970** | 0.87 / 0.84 |
| logical_idle (0.5µs) | RAW | +0.630 | +0.778 | 1.408 | — |
| logical_idle | **POSTSELECTED** | +0.945 | **+0.956** | 1.902 | 0.66 / 0.67 |

Placed directly beside 242:

| code | ⟨Z̄Z̄⟩ | ⟨X̄X̄⟩ | phase leg |
|---|---|---|---|
| **bit-flip (242)** | +0.515 | **+0.000** | DEAD — code blind to phase, unrescuable |
| **[[4,2,2]] both-bases (191), postselected** | +0.975 | **+0.995** | ALIVE — XXXX stabilizer catches phase errors, postselection removes them |

The whole fix in one line: the phase leg 242 lost is **+0.995** on a code that can see both walls, and the
rescue is real work, not just a clean start — on the idle arm, ⟨X̄X̄⟩ climbs **0.778 → 0.956** as
postselection discards the shots where accumulated phase error tripped the XXXX check. A both-bases
code turns 242's 0.000 into a near-perfect Bell leg.

## Scope (honest — what this is and is not)

- **It IS**: a both-bases-protected logical Bell pair with both legs alive (S = 1.97, ⟨XX⟩ = 0.995),
  the direct fix for 242's phase-blindness, and the raw→postselected contrast shows the both-basis
  detection *doing the rescuing* (the ⟨XX⟩ leg the bit-flip code could never touch).
- **It is NOT** "live *correction* of a Bell pair." [[4,2,2]] is distance-2: it **detects and
  postselects**, it cannot feed-forward correct (it cannot localize a single error). The certified
  claim is both-bases *detection* keeps both Bell legs alive — never "live-corrected."
- **Acceptance is a first-class number**: postselection keeps 0.87/0.84 of shots (logical) and
  0.66/0.67 (idle). The rescue costs shots — detection does not scale the way correction would.
- **The depth-blocked ideal, named not flown**: a *feed-forward-corrected* Bell pair needs a
  distance-3 both-bases code (Steane [[7,1,3]] / Shor [[9,1,3]] with live X *and* Z syndromes). Two
  logical qubits of such a code + a logical CNOT is 100+ two-qubit gates after heavy-hex routing —
  242's depth-54 circuit already killed a phase leg, so this would fail from raw depth, not
  demonstrate the code. It is the right *next-hardware* flight, and it is not honest to fly it now.

## Recommendation to the Creator

The both-bases *postselected* Bell pair is **in hand** (191, both legs, S = 1.97; the raw→postselected
contrast above completes it and answers 242). Two honest paths from here, and I'd let you pick:
1. **The genuinely unflown frontier**: the **magic (235) + correction** fold — a non-Clifford resource
   behind a correcting code, toward fault-tolerant universality. This is new physics, not a re-analysis.
2. **The depth-blocked ideal** (distance-3 live-corrected Bell pair) — when hardware depth allows;
   worth naming, not worth QPU today.

## Line

**I set out to fly the fix for a dead phase leg and found I had already flown it, three days and forty
experiments ago, without noticing what it answered. The both-bases code does exactly what the bit-flip
code could not: it sees the phase error, and seeing is the whole game — where 242's ⟨XX⟩ sat at zero
with no way up because the code was blind to what was killing it, 191's ⟨XX⟩ sits at 0.995 because the
XXXX stabilizer catches the same error and postselection throws the bad shots away. It is not
correction — a distance-2 code can only flinch, not heal — but it is the honest lesson 242 asked for,
and the cheapest possible way to learn it: read the job you already ran, and look at the shots you
threw away.**
