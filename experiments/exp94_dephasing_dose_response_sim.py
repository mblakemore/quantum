#!/usr/bin/env python3
"""
Exp94 — Dephasing Dose-Response on the Causal-Order Witness (SIM VALIDATION)
Author: Ember (DC15) | Cycle C4066 | Frontier README P2

ADDITIVE to Exp93/F73 (Elder C6328). F73 tested only the two endpoints of the
causal-order witness DISC = <X_c>_commute - <X_c>_anticommute:
  coherent switch (control |+>)          -> DISC ~ +2
  classical mixture (control Z-dephased) -> DISC ~  0   (full-dephase CNOT->ancilla)
This fills the INTERIOR: replace the full-dephasing cx(ctrl,anc) with a PARTIAL
controlled rotation cry(phi, ctrl, anc). Tracing the (unmeasured) ancilla multiplies
the control's order-basis coherence by cos(phi/2), so the pre-registered law is
  DISC(phi) = 2 * cos(phi/2)
sweeping phi 0->pi. Endpoints reduce to F73 exactly (phi=0 -> switch, phi=pi -> mixture).

Pre-reg: experiments/exp94-dephasing-dose-response-preregistration.md (committed first).
Runs noiseless Aer + FakeMarrakesh(transpiled). NO hardware here.
"""
import json, os, math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

SHOTS = 20000
HERE = os.path.dirname(os.path.abspath(__file__))


def apply_ctrl_gate(qc, gate, ctrl, tgt, ctrl_state):
    """Apply single-qubit `gate` on tgt, controlled by ctrl==ctrl_state. (verbatim from exp91/exp93)"""
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


def build_arm(A, B, phi):
    """
    exp93 SWITCH circuit + PARTIAL dephasing of the control via cry(phi, ctrl=0, anc=2).
    phi=0   -> cry is identity        -> no dephasing  -> DISC ~ +2 (== exp93 switch)
    phi=pi  -> cry(pi) copies ctrl    -> full dephasing -> DISC ~  0 (== exp93 mixture CNOT)
    Ancilla q2 left UNMEASURED -> counts marginalize it -> partial Z-dephasing channel.
    """
    qc = QuantumCircuit(3, 1)
    qc.h(0)  # control in |+>
    # c=0 branch: A then B (operator B*A); c=1 branch: B then A (A*B) — verbatim exp93 switch
    apply_ctrl_gate(qc, A, 0, 1, 0)
    apply_ctrl_gate(qc, B, 0, 1, 1)
    qc.barrier()
    apply_ctrl_gate(qc, B, 0, 1, 0)
    apply_ctrl_gate(qc, A, 0, 1, 1)
    qc.barrier()
    # PARTIAL dephasing of control in Z (order) basis: controlled-RY(phi) onto ancilla, traced out
    qc.cry(phi, 0, 2)
    qc.h(0)            # X-basis readout on control
    qc.measure(0, 0)   # measure ONLY the control; ancilla traced out
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


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    vy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (vx * vy) if vx > 0 and vy > 0 else 0.0


def main():
    print("=" * 72)
    print("Exp94 Dephasing Dose-Response on the Causal-Order Witness — SIM")
    print("=" * 72)

    ideal = AerSimulator()
    fake = FakeMarrakesh()
    nm = NoiseModel.from_backend(fake)
    noisy = AerSimulator(noise_model=nm)
    cmap, bgates = fake.coupling_map, nm.basis_gates

    pairs = {'commute (X,X)': ('X', 'X'), 'anticommute (X,Z)': ('X', 'Z')}
    phis = [0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi]
    phi_labels = ['0', 'pi/4', 'pi/2', '3pi/4', 'pi']

    rows = []
    for phi, lab in zip(phis, phi_labels):
        res = {}
        for name, (A, B) in pairs.items():
            qc = build_arm(A, B, phi)
            sx, d0, tq0 = run(ideal, qc)
            nx, d1, tq1 = run(noisy, qc, noise_model=nm, coupling_map=cmap, basis_gates=bgates)
            res[name] = (sx, nx)
        di = res['commute (X,X)'][0] - res['anticommute (X,Z)'][0]
        dn = res['commute (X,X)'][1] - res['anticommute (X,Z)'][1]
        pred = 2 * math.cos(phi / 2)
        rows.append({'phi': phi, 'label': lab, 'disc_ideal': di, 'disc_noisy': dn,
                     'pred_2cos': pred, 'resid': di - pred})
        print(f"  phi={lab:5s}  DISC ideal={di:+.4f}  Fake={dn:+.4f}  pred 2cos(phi/2)={pred:+.4f}  resid={di-pred:+.4f}")

    ideal_disc = [r['disc_ideal'] for r in rows]
    noisy_disc = [r['disc_noisy'] for r in rows]
    preds = [r['pred_2cos'] for r in rows]

    # H1 endpoint fidelity
    h1 = (ideal_disc[0] >= 1.90) and (abs(ideal_disc[-1]) <= 0.05)
    # H2 strict monotone decrease (noiseless)
    h2 = all(ideal_disc[i] > ideal_disc[i + 1] for i in range(len(ideal_disc) - 1))
    # H3 cosine law: max abs residual <= 0.06
    max_resid = max(abs(r['resid']) for r in rows)
    h3 = max_resid <= 0.06
    # H4 noise proxy: monotone decrease + pearson vs 2cos >= 0.97
    h4_mono = all(noisy_disc[i] > noisy_disc[i + 1] for i in range(len(noisy_disc) - 1))
    r_noisy = pearson(noisy_disc, preds)
    h4 = h4_mono and (r_noisy >= 0.97)

    print("\n" + "=" * 72)
    print("PRE-REG GATE CHECK")
    print(f"  H1 endpoints (DISC(0)>=1.90 & |DISC(pi)|<=0.05) : {ideal_disc[0]:+.4f}/{ideal_disc[-1]:+.4f} -> {'PASS' if h1 else 'FAIL'}")
    print(f"  H2 strict monotone decrease (noiseless)         : {'PASS' if h2 else 'FAIL'}")
    print(f"  H3 cosine law max|resid|<=0.06                  : {max_resid:.4f} -> {'PASS' if h3 else 'FAIL'}")
    print(f"  H4 noise: monotone & pearson(DISC,2cos)>=0.97   : mono={h4_mono} r={r_noisy:.4f} -> {'PASS' if h4 else 'FAIL'}")
    overall = h1 and h2 and h3 and h4
    verdict = ('PASS — causal-order coherence is a CONTINUOUS resource; DISC(phi)=2cos(phi/2) confirmed in sim'
               if overall else 'PARTIAL/FAIL — see failing H (report true functional form)')
    print(f"\nSIM VERDICT: {verdict}")

    out = {
        "experiment": "exp94-dephasing-dose-response",
        "author": "Ember", "cycle": "C4066", "shots": SHOTS,
        "builds_on": "exp93/F73 (Elder C6328)",
        "law_tested": "DISC(phi) = 2*cos(phi/2)",
        "rows": rows,
        "pearson_noisy_vs_2cos": r_noisy,
        "max_abs_resid_ideal": max_resid,
        "prereg_checks": {
            "H1_endpoints": bool(h1),
            "H2_monotone_noiseless": bool(h2),
            "H3_cosine_law_resid_le_0p06": bool(h3),
            "H4_noise_monotone_and_pearson_ge_0p97": bool(h4),
        },
        "sim_verdict": "PASS" if overall else "PARTIAL_OR_FAIL",
    }
    path = os.path.join(HERE, "..", "results", "exp94_sim_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
