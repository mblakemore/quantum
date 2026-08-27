# Turbine step 1 — the chip's natural thermal head, gauged $0 (Whisper C5086, board #143)

The turbine (a thermodynamic engine on qubits) needs a hot-cold GRADIENT to drive it. Step 1: gauge
how much thermal head ibm_fez provides NATURALLY — idle-heating (qubits drift to a hot steady state)
vs reset-cold (active reset drives them to ground). $0, from device properties, no flight.

## Method ($0)
From ibm_fez.properties() (156 qubits): T1, and prob_meas1_prep0 as the idle excited-state population
proxy (a qubit prepped |0> and read |1> is thermal excitation OR readout misclassification). Reset-cold
target ~0. Natural head = idle_pop - reset_pop.

## Result
- T1 median 134 us.
- Idle excited-state population (prep0->meas1): median **0.0076** (0.76%), min 0.0005, max 0.366.
- Natural thermal head ~ **0.76% on the median qubit** (idle-hot minus reset-cold).

## The honest caveat (this is an UPPER BOUND, not the thermal head itself)
prob_meas1_prep0 CONFLATES thermal excitation with readout error (prep0->meas1 = p_thermal + epsilon_10,
inseparable without a readout characterization). So 0.76% BOUNDS the natural thermal head ABOVE; the true
idle-heating population is smaller, readout-corrected. The max 0.366 is a bad-readout qubit, not a hot one.

## What it means for the turbine
The chip's NATURAL thermal head is SMALL (<= ~0.76%). Idle-heating alone gives the turbine almost no
gradient to work with. This points the design toward a MANUFACTURED gradient — reset-cold on one side,
deliberate excitation on the other — consistent with the manufactured-bath direction (counterflow Flight B),
rather than harvesting the chip's tiny natural head. A turbine on the natural head would be running on <1%
population difference; a driven gradient is the only way to a usable head.

## Next (owed, GO-gated)
A clean readout-CORRECTED idle-vs-reset MEASUREMENT (prepare idle-drifted vs actively-reset, read with a
bare-qubit readout cal) is the hardware confirm of the true natural head — that needs a QPU flight and a
Creator GO. This $0 gauge gives the upper bound and the design steer; the measurement pins the number.
