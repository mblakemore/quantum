#!/usr/bin/env python3
"""Exp140 sim-tier KILL-GATE (Whisper C4744, advisor-corrected non-circular version).

Question it answers (assumes NOTHING about the stack working):
  Does the 3-body OLE observable O = Z52 Z59 Z72 survive above the shot-noise floor
  through the real tracker circuit at Heron-realistic depolarizing p?
    - dies to ~1e-9  -> HONEST KILL (no rescaling recovers it, stack irrelevant), save QPU.
    - lands ~>=floor -> the stack question is LIVE, hardware flight justified.

Method (advisor): back-propagate the observable's SUPPORT through the CZ graph (Heisenberg,
Clifford support-growth; single-qubit rotations branch coefficients but do NOT grow support).
Attenuation under a depolarizing Pauli channel: A ~ (1-p)^{N_eff}, N_eff = #CZ gates that
act on the evolving support (each such gate shrinks a nonidentity Pauli's coefficient by ~(1-p)).
Two bounds:
  worst-case  : every CZ touches support  -> A_wc = (1-p)^{N_cz_total}   (min signal)
  lightcone   : only CZ in O's backward lightcone -> A_lc = (1-p)^{N_eff} (realistic)
No stack Delta-lambda is used here by design; this gate is stack-agnostic.
"""
import re, sys

QASM = sys.argv[1] if len(sys.argv) > 1 else "ole49.qasm"
OBS = [int(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else "52,59,72".split(","))]

# --- parse the transpiled QASM into an ordered gate list -----------------------
gates = []  # (name, [qubits])
qline = re.compile(r'^\s*([a-z]+)(?:\([^)]*\))?\s+((?:q\[\d+\]\s*,?\s*)+);')
ncz = 0
with open(QASM) as f:
    for line in f:
        m = qline.match(line)
        if not m:
            continue
        name = m.group(1)
        qs = [int(x) for x in re.findall(r'q\[(\d+)\]', m.group(2))]
        if name in ('rz','rx','sx','sxdg','x','h','s','sdg','sdag','cz','cx','ecr'):
            gates.append((name, qs))
            if name in ('cz','cx','ecr'):
                ncz += 1

print(f"parsed {len(gates)} gates, {ncz} two-qubit gates; observable qubits {OBS}")

# --- backward lightcone of the observable qubits -------------------------------
# propagate support from the END of the circuit backward; a 2q gate that touches
# the current support pulls BOTH its qubits into the support (Clifford max-spread).
support = set(OBS)
n_eff = 0                 # 2q gates that act on the support (attenuating events)
max_support = len(support)
growth = []
for name, qs in reversed(gates):
    if name in ('cz','cx','ecr'):
        if support & set(qs):        # gate touches support -> attenuates + may spread
            n_eff += 1
            support |= set(qs)
            if len(support) > max_support:
                max_support = len(support)
                growth.append((n_eff, len(support)))
    # single-qubit gates: branch coefficients, do NOT grow support -> ignored for support/N_eff
print(f"backward-lightcone: N_eff (2q gates acting on support) = {n_eff} / {ncz}")
print(f"final support size = {len(support)} qubits (max reached {max_support})")

# --- attenuation + shot-floor comparison ---------------------------------------
import math
def atten(p, N): return (1.0 - p) ** N

# Heron ibm_marrakesh-class 2q *Pauli/depolarizing* error range (median ~ few e-3;
# effective per-gate Pauli error typically 3-8e-3). Grid spans optimistic->pessimistic.
P_GRID = [2e-3, 3e-3, 5e-3, 8e-3]

# ground truth magnitude at alpha=0: cos(2*delta)^k, delta=0.15 -> cos(0.3)^k in {1,.955,.913,.872}
# take a representative truth ~0.9 (k~1-2); we report signal = truth * A.
TRUTH = 1.00  # DERIVED EXACT: alpha=0 echo, O disjoint+commuting with rz(0.3) perturbation, U=I => f=Tr(O^2)/2^n = 1

# shot floor: OLE estimator averages N_init random |z> each with S shots.
# SE(f) ~ 1/sqrt(N_init * S) (per-z variance <= 1, conservative). Resolvable if signal > 3*SE.
def shot_se(n_init, shots): return 1.0 / math.sqrt(n_init * shots)

print("\n p(2q)  A_worstcase(all CZ)   A_lightcone(N_eff)   signal=truth*A_lc")
for p in P_GRID:
    a_wc = atten(p, ncz); a_lc = atten(p, n_eff)
    print(f" {p:.0e}   {a_wc:.3e}            {a_lc:.3e}          {TRUTH*a_lc:.3e}")

print("\nshot-noise floor (3*SE) for candidate budgets:")
for n_init, shots in [(12,4000),(24,4000),(30,8000)]:
    se = shot_se(n_init, shots)
    print(f"  N_init={n_init:>2} x {shots} shots  -> 3*SE = {3*se:.4e}")

print("\nVERDICT LOGIC: signal(=truth*A_lightcone) vs 3*SE across the p grid.")
for p in P_GRID:
    sig = TRUTH*atten(p, n_eff); se3 = 3*shot_se(24,4000)
    verdict = "LIVE (>floor)" if sig > se3 else ("MARGINAL" if sig > se3/3 else "KILL (<floor)")
    print(f"  p={p:.0e}: signal={sig:.3e}  vs 3SE(24x4000)={se3:.3e}  -> {verdict}")
