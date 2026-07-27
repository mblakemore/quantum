# ICO engine — what's left, and one genuinely new direction (Whisper C5011)

*Creator: other futuristic/out-of-the-box directions with the ICO engine? Honest method: read what we've
flown BEFORE inventing (7 rediscoveries this session — the campaign is thorough enough that most "new"
ideas are already built). This separates the completed arc from the thin genuine residue, then offers one
direction that is actually new because it fuses ICO with findings that postdate the C4527 roadmap.*

## The ICO arc is essentially COMPLETE (what's flown)
| Flown | Result |
|---|---|
| Switch witness | F73–F77 causally-separable ceiling beaten, Exp105 game WIN 216.8σ |
| Capacity activation N=2 | **F83** — 0.0436 bits/use through TWO zero-capacity depolarizing channels, 55.6σ (Ebler–Salek–Chiribella, on silicon) |
| Capacity activation N=3 | **F85** — 61.7σ, AND mapped the wall: ideal capacity grows with N but MEASURED capacity fell (depth cost > scaling gain) → **N=2 is this generation's optimum** |
| The engine | **F94** certified working resource (population inversion +10.6σ from two passive baths) → **F95** full thermodynamic cycle (intake·charge·power·exhaust, net 0.034 E/run, demon books audited) |
| Commute-compute | C4999 scout — the compiled switch computes COMMUTE(U,V) (Chiribella 2012) |

**So "bigger/deeper switch" is a dead end on this hardware** — F85 already proved the depth cost eats the
gain. New ICO directions must be depth-CHEAP or use the switch as an INSTRUMENT, not scale it.

## The "residue" is ALSO mostly flown (verified against the arc list, not name-grep)
My first draft called the C4527 T2 items "unflown." Checking the arc list (the same method that showed
F85 = the N=3 switch) corrects that:
- **T2.5 Causal tomography of the chip** → **F111** ("cloaking device") already read out the device's
  noise-correlation structure (dephasing dominantly memoryless + ~10–15% correlated tail, two ways).
- **T2.6 ICO noise-averaging / hidden gate-order** → **F96** already certified the two execution orders
  of nominally-parallel CZ gates are statistically indistinguishable (hidden ordering ≤ 0.0303 TVD).
- **T2.7 Game-wins as certified randomness** → covered by the **F115/F116/F117** randomness/steering arc.
So the T2 trio is largely flown too. (Method lesson, 8th of the session: verify "unflown" against the
F-arc list, never a keyword grep — the grep said "N=3: 0 files" moments before F85 disproved it.)

## The tempting new fusion — and the crisp reason it's a MIRAGE
**"Is the chip's OWN noise causally non-separable?"** (ICO witness × drift census) is the natural
out-of-box swing — and it does not work, for one clean reason worth stating because it is Star-Trek
interesting on its own:

**Non-Markovian ≠ causally non-separable.** Causal non-separability (OCB / the switch) requires a control
degree of freedom that *coherently superposes the ORDER* of operations. The device's native noise — even
coherent, even with revival {26,53,73} — is a **memoryful but DEFINITE-order** process: the
system–environment interactions still happen in a fixed temporal sequence; a TLS producing revival is
*memory*, not a superposition of orders. There is no coherent order-control in native decoherence, so
there is no free indefinite order in the chip's noise. This is the **no-free-ride rule again** — ICO is
something you *engineer with a control qubit*, not something thermal noise hands you.

**And we already looked, empirically:** **F96** tested the nearest real version — is there hidden order in
the chip's own operations? — and found NONE (orders indistinguishable ≤ 0.0303 TVD). So this is a
CONFIRMED boundary (concept + data), not a live lead. Naming *why* is the contribution; there is no scout
to run.

## Bottom line
The ICO engine is a near-finished masterpiece, not an open frontier. The honest answer to "what else can
we build with it" is: **surprisingly little that's new — we built the arc** (witness, N=2/N=3 capacity
activation, the full engine cycle, teleported indefiniteness, noise-structure readout, schedule-order
symmetry, randomness), and the one tempting extension is a named mirage (non-Markovian noise is not free
ICO; F96 already found no hidden order). The genuine open frontier is elsewhere — the two-copy/purity arc
just greenlit (steth + probes A/B), not more ICO. That is not a disappointing answer; it is what a
completed masterpiece looks like.
