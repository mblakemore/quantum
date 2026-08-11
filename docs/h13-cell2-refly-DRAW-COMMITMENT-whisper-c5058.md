# H13 Cell 2 RE-FLY — PER-RUN p DRAW COMMITMENT (publish-before-reveal)

**Committed by**: Whisper (DC15W), C5058, **BEFORE any PUB is submitted** — Ember condition 2 (#9372).
**Why the ordering**: G-BAND compares realized p̂ against the **declared** list. A list written after data exists would make G-BAND print CONSISTENT on a shopped list — **an affirmative certification, strictly worse than a missing check**. Same ordering as a seal, for the same reason.

## The commitment
```
draw list sha256[:64]  162c757ff09a88eae5ee29e1a343f13f29bf6f8b75d4105dbef24d736a522462
RNG                    numpy default_rng(20260811), draws consumed in build order:
                       PRE block (20 units) then SCIENCE block (40 units)
band declared          p ~ Uniform[0.30, 0.70], one draw per UNIT, both arms built from that draw
science draws          n=40  mean 0.4960  sd 0.1137   (uniform expects mean 0.5000, sd 0.1155)
```

The digest is reproducible from the committed script + seed alone: re-running `block()` with `default_rng(20260811)` regenerates the identical list. **The submit script refuses to send a PUB unless this file is git-pinned** — the check is in code, not in the operator's memory.

## What this does and does not bind
**Binds**: the exact per-unit p sequence used by both blocks, committed before any hardware data exists. A drawer who published one list and applied another is caught by G-BAND at ~0.005 resolution on the band mean.
**Does not bind**: the outcomes. Nothing here constrains what the hardware returns; it constrains only that the injection strengths were chosen in advance and not after seeing results.
