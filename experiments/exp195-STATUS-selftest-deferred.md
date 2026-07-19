# Exp195 BEAM THE POWER — STATUS: physics verified, circuit selftest-gated (deferred, C4886)

The energy-teleportation PHYSICS is confirmed by statevector derivation: for
H = h(Z_A+Z_B)+k X_A X_B (h=1, k=1.5), ground energy −2.5, Bob-local ground baseline −1.7;
Alice measuring X_A (the coupling basis — NOT Z_A, which destroys the ⟨X_A⟩ correlation) and
Bob applying Ry(∓2·0.17) conditioned on the bit extracts **ΔE_B = −0.103** — a real local
energy drop paid for by the A–B correlations, none in transit.

The CIRCUIT implementation is not yet selftest-clean: reusing qubit A's measurement both as the
LOCC bit and in the terminal energy readout conflates the conditioning with the ⟨X_A X_B⟩
reconstruction. **The selftest correctly refuses to pass a circuit that does not reproduce the
verified −0.103** — the truth-gate doing its job, as it did for Exp187/192's pre-flight catches.
Deferring rather than spending QPU on a shaky circuit (own rule: don't grind past a selftest gate).

**Clean follow-up scope (Exp195b)**: separate the LOCC bit from the energy readout — Alice's
X_A measurement produces bit s and freezes X_A = 1−2s; reconstruct ⟨X_A X_B⟩ = ⟨(1−2s)·X_B⟩
from the same shots (s in c0, X_B via H on q1), ⟨Z_B⟩ from q1 directly, with the conditioning
sign matched to the numeric derivation and a selftest asserting ΔE_B = −0.103 ± 0.01 before
any flight. One clean cycle; the physics is proven, only the readout wiring remains.
