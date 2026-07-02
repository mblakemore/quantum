#!/usr/bin/env python3
"""
Exp93 — Classical-Mixture Control for the Causal-Order Witness (SIM VALIDATION)
Author: Elder (DC15) | Cycle C6328 | Frontier README P2

Closes the loophole Exp91 leaves open: Exp91's only causally-separable control is a
PURE definite order. The sharper adversary is a CLASSICAL 50/50 MIXTURE of the two
definite orders (== fully Z-dephased quantum switch, the standard causally-separable
object). A genuine causal-nonseparability witness must vanish on it.

Three arms (2-qubit control q0 + target q1; control |+>, read in X basis):
  SWITCH           : Exp91 coherent switch                          -> DISC ~ +2
  DEFINITE         : Exp91 spectator control, fixed order           -> DISC ~  0
  CLASSICAL MIXTURE: SWITCH but control dephased in Z (order) basis -> DISC ~  0   [NEW]
        realized by CNOT(control->ancilla q2) then LEAVE ANCILLA UNMEASURED so the
        counts marginalize (trace) it out == exact Z-dephasing channel on the control.

Witnesses:
  W1 = DISC_switch - DISC_definite   (Exp91)
  W2 = DISC_switch - DISC_mixture    (NEW: switch vs classical mixture of definite orders)

Pre-reg (exp93-classical-mixture-control-preregistration.md):
  H1 DISC_switch >= +1.90 | H2 |DISC_mixture| <= 0.05 | H3 W2 > 0.07 | H4 mechanism isolation.

Runs noiseless Aer + FakeMarrakesh(transpiled). NO hardware here.
"""
import json, os
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

SHOTS = 20000
HERE = os.path.dirname(os.path.abspath(__file__))


def apply_ctrl_gate(qc, gate, ctrl, tgt, ctrl_state):
    """Apply single-qubit `gate` on tgt, controlled by ctrl==ctrl_state. (verbatim from exp91)"""
    if ctrl_state == 0:
        qc.x(ctrl)
    if gate == 'X':
        qc.cx(ctrl, tgt)
    elif gate == 'Z':
        qc.cz(ctrl, tgt)
    elif gate == 'Y':
        qc.cy(ctrl, tgt)
    else:
        raise ValueError(gate)
    if ctrl_state == 0:
        qc.x(ctrl)


def build_arm(A, B, mode):
    """
    mode in {'switch','definite','mixture'}.
    switch/definite reproduce exp91 exactly. mixture == switch + Z-dephasing of control
    (CNOT to ancilla q2, ancilla left unmeasured -> traced out -> classical mixture of orders).
    """
    n_anc = 1 if mode == 'mixture' else 0
    qc = QuantumCircuit(2 + n_anc, 1)
    qc.h(0)  # control in |+>
    if mode in ('switch', 'mixture'):
        # c=0 branch: A first then B (operator B*A); c=1 branch: B first then A (A*B)
        apply_ctrl_gate(qc, A, 0, 1, 0)
        apply_ctrl_gate(qc, B, 0, 1, 1)
        qc.barrier()
        apply_ctrl_gate(qc, B, 0, 1, 0)
        apply_ctrl_gate(qc, A, 0, 1, 1)
    elif mode == 'definite':
        # fixed order A then B on target, control a pure spectator
        for g in (A, B):
            if g == 'X': qc.x(1)
            elif g == 'Z': qc.z(1)
            elif g == 'Y': qc.y(1)
    else:
        raise ValueError(mode)
    qc.barrier()
    if mode == 'mixture':
        # dephase control in Z (order) basis: copy onto ancilla, trace it out (unmeasured)
        qc.cx(0, 2)
    qc.h(0)            # X-basis readout on control
    qc.measure(0, 0)   # measure ONLY the control; ancilla (if any) traced out
    return qc


def exp_x_control(counts, shots):
    """<X_c> from control-only counts after H (P0 - P1). Robust to ancilla-marginalized keys."""
    p0 = p1 = 0
    for bitstr, n in counts.items():
        b = bitstr.replace(" ", "")[-1]  # control is classical bit 0
        if b == '0':
            p0 += n
        else:
            p1 += n
    tot = p0 + p1
    return (p0 - p1) / tot


def run(backend, qc, noise_model=None, coupling_map=None, basis_gates=None):
    tqc = transpile(qc, backend=backend if noise_model is None else None,
                    coupling_map=coupling_map, basis_gates=basis_gates,
                    optimization_level=1, seed_transpiler=42)
    counts = backend.run(tqc, shots=SHOTS).result().get_counts()
    ops = tqc.count_ops()
    twoq = ops.get('cz', 0) + ops.get('ecr', 0) + ops.get('cx', 0)
    return exp_x_control(counts, SHOTS), tqc.depth(), twoq


def main():
    print("=" * 72)
    print("Exp93 Classical-Mixture Control for the Causal-Order Witness — SIM")
    print("=" * 72)

    ideal = AerSimulator()
    fake = FakeMarrakesh()
    nm = NoiseModel.from_backend(fake)
    noisy = AerSimulator(noise_model=nm)
    cmap, bgates = fake.coupling_map, nm.basis_gates

    pairs = {'commute (X,X)': ('X', 'X'), 'anticommute (X,Z)': ('X', 'Z')}
    disc = {}
    for mode in ('switch', 'definite', 'mixture'):
        print(f"\n--- {mode.upper()} ---")
        res = {}
        for name, (A, B) in pairs.items():
            qc = build_arm(A, B, mode)
            sx, d0, tq0 = run(ideal, qc)
            nx, d1, tq1 = run(noisy, qc, noise_model=nm, coupling_map=cmap, basis_gates=bgates)
            res[name] = (sx, nx)
            print(f"  {name:22s} <X_c> ideal={sx:+.4f}  Fake={nx:+.4f}  (depth {d1}, 2q={tq1})")
        di = res['commute (X,X)'][0] - res['anticommute (X,Z)'][0]
        dn = res['commute (X,X)'][1] - res['anticommute (X,Z)'][1]
        disc[mode] = {'ideal': di, 'noisy': dn}
        print(f"  DISC({mode}) ideal={di:+.4f}  Fake={dn:+.4f}")

    ds_i, ds_n = disc['switch']['ideal'], disc['switch']['noisy']
    dd_i, dd_n = disc['definite']['ideal'], disc['definite']['noisy']
    dm_i, dm_n = disc['mixture']['ideal'], disc['mixture']['noisy']
    W1_i, W1_n = ds_i - dd_i, ds_n - dd_n
    W2_i, W2_n = ds_i - dm_i, ds_n - dm_n

    print("\n" + "=" * 72)
    print("WITNESSES")
    print(f"  W1 = DISC_switch - DISC_definite (Exp91):  ideal={W1_i:+.4f}  Fake={W1_n:+.4f}")
    print(f"  W2 = DISC_switch - DISC_mixture  (NEW):    ideal={W2_i:+.4f}  Fake={W2_n:+.4f}")

    # Pre-registered gate checks (noiseless tolerances per exp93 pre-reg)
    h1 = ds_i >= 1.90
    h2 = abs(dm_i) <= 0.05
    h3 = W2_i > 0.07
    # FakeMarrakesh proxy (looser): mixture stays inert, W2 survives noise
    h2_fake = abs(dm_n) <= 0.20
    h3_fake = W2_n > 0.07
    print("\nPRE-REG GATE CHECK (noiseless):")
    print(f"  H1 DISC_switch >= +1.90     : {ds_i:+.4f}  -> {'PASS' if h1 else 'FAIL'}")
    print(f"  H2 |DISC_mixture| <= 0.05   : {abs(dm_i):.4f}   -> {'PASS' if h2 else 'FAIL'}")
    print(f"  H3 W2 > 0.07                : {W2_i:+.4f}  -> {'PASS' if h3 else 'FAIL'}")
    print("FakeMarrakesh proxy:")
    print(f"  H2' |DISC_mixture_noisy| <= 0.20 : {abs(dm_n):.4f} -> {'PASS' if h2_fake else 'FAIL'}")
    print(f"  H3' W2_noisy > 0.07              : {W2_n:+.4f} -> {'PASS' if h3_fake else 'FAIL'}")
    overall = h1 and h2 and h3 and h2_fake and h3_fake
    print(f"\nSIM VERDICT: {'PASS — classical-mixture loophole closed in sim; ready for hardware arm' if overall else 'FAIL — see failing H'}")

    out = {
        "experiment": "exp93-classical-mixture-control",
        "cycle": "C6328", "shots": SHOTS,
        "disc": disc,
        "W1_switch_vs_definite": {"ideal": W1_i, "noisy": W1_n},
        "W2_switch_vs_mixture": {"ideal": W2_i, "noisy": W2_n},
        "prereg_checks": {
            "H1_disc_switch_ge_1p90": bool(h1),
            "H2_abs_disc_mixture_le_0p05": bool(h2),
            "H3_W2_gt_0p07": bool(h3),
            "H2fake_abs_disc_mixture_noisy_le_0p20": bool(h2_fake),
            "H3fake_W2_noisy_gt_0p07": bool(h3_fake),
        },
        "sim_verdict": "PASS" if overall else "FAIL",
    }
    path = os.path.join(HERE, "..", "results", "exp93_sim_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {os.path.relpath(path, HERE)}")


if __name__ == '__main__':
    main()
