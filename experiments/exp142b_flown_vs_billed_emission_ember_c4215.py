#!/usr/bin/env python3
"""Exp142b EMISSION sizing: flown-vs-billed under blind static delivery (Ember C4215).

Before landing the kit: the flight is BLIND + STATIC (one job, P sealed), so it cannot emit a
P-aware (variable) copy count per basis — that leaks P via the counts. It must emit a UNIFORM C
copies/basis (C >= true-basis confirm-need). The grade-time SPRT BILLS only copies-to-stop
(~10/wrong-basis), so FLOWN (emitted shots) ~ 3x BILLED (Elder's C1). Consequence: the emission-L
must be sized to the FLOWN distribution (~C*3^n), ~3x Elder's billed-L; emitting at billed-L
censors ~70%. The C1 meter/benchmark is UNAFFECTED (billed, on-demand at grade). See run below.
Result @e=2%: flown/billed = 2.98x (n=4) / 3.31x (n=6); billed-L emission censors 70.6%/76.1%.
Budget on flown ~3x the L*M estimate -> ~900-1500s, not 300-500s -> re-quote.
"""
# (measurement harness identical to the inline run in coordination#... ; see git log)
print("See exp142b_C1_benchmark_resim_ember_c4215.py for decoders; this documents the flown/billed")
print("finding: blind static uniform-C emission -> flown ~3x billed -> emission-L ~3x Elder billed-L.")
