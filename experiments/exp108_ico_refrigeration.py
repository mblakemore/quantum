#!/usr/bin/env python3
"""
Exp108 — ICO refrigeration resource: conditional temperature splitting from the
quantum switch of two fully-thermalizing channels (Whisper C4558).

Theory (Felce & Vedral, PRL 125, 070603 (2020)): a fully-thermalizing qubit channel
T(rho) = tau = diag(g, 1-g) outputs the reservoir state regardless of input, and so
does EVERY causally-separable composition of two of them -> the target is exactly tau,
UNCORRELATED with the control (discriminator below is EXACTLY 0 by channel algebra,
same structure as Exp106). In the quantum switch with control |+>, measuring the
control in X splits the target into a COLDER state (outcome +) and a HOTTER state
(outcome -): the resource that powers the Felce-Vedral refrigeration cycle.

Exact targets (derived C4558 by direct Kraus computation of the switch supermap;
the code below validates itself at g=1/2 against Exp106's independently-derived
targets P(+)=5/8, rho|+ = (rho+2I)/5, rho|- = (2I-rho)/3 — the constant-to-I/2
channel IS the completely depolarizing channel and the switch is Kraus-
decomposition-independent). For g = 0.75, input tau (cycle-relevant):
    P(control=+) = 0.71875
    p1|+  = 0.184783   (tau: 0.25  -> COLDER)
    p1|-  = 0.416667   (          -> HOTTER)
    Delta := p1|- - p1|+ = 0.231884 ; causal value = 0 EXACTLY
NOTE: conditional states are INPUT-DEPENDENT in general (a wrong recalled
closed-form (tau +/- tau^2)/(1 +/- Tr tau^2) was refuted by this computation);
we pool the input to tau, which is the physically-relevant cycle input.

Implementation: fully-thermalizing channel = SWAP with a fresh ancilla prepared
in tau. tau is a CLASSICAL mixture of basis states, so pooling the 8 basis-prep
circuits (t0,a10,a20) in {0,1}^3 with weights w(t0)w(a10)w(a20), w(0)=g, is the
EXACT channel + input mixture (switch supermap is linear in each channel slot;
Exp106 pooling logic; conditioning on pooled JOINT counts is valid because the
joint is linear in the input). The switch of the two SWAP-dilated channels is a
controlled permutation on (t, a1, a2):
    c=0 branch: SWAP(t,a1) then SWAP(t,a2)  = C3   (t->a1->a2->t)
    c=1 branch: reverse order               = C3^{-1} = C3^2
    U = (I_c (x) C3) . CC3      [check: c=0 -> C3 ; c=1 -> C3.C3 = C3^{-1}]
    CC3 = CSWAP(c;t,a1) . CSWAP(c;t,a2)   (two Fredkins), then bare C3.
Null arm: definite order only, control |+> spectator -> output exactly tau. BOTH
definite orders are run (C3 and C3^{-1}). C4529 LESSON RECURRED AND WAS CAUGHT
PRE-FREEZE AGAIN: a conditional discriminator STARVES on the null arm (spectator
control -> no c=- samples -> Delta_null = NaN in the first sim run); the null
gate is therefore on UNCONDITIONED quantities (p1 vs 1-g, thermalization
integrity) exactly as Exp106 redefined it, plus P(c=+) ~ 1 spectator-coherence.

Qubits: q0=control (X readout, clbit 0), q1=target (Z readout, clbit 1),
q2=a1, q3=a2 (unmeasured, traced).

Sentinels (same-skeleton, Exp107 Bridge-2 lesson — a shallow sentinel cannot
certify a deeper window):
  RETENTION: all-|0> prep -> fixed point of BOTH branches -> control re-interferes
    to |+>: ideal P(c=+, t=0) = 1. Direct same-depth window meter.
  DECOHERENCE-NULL: prep t=1, a1=a2=0 -> branch registers |010> vs |001>
    ORTHOGONAL -> control fully decoheres: ideal P(c=+) = 1/2 exactly, t=0 always.
    Certifies the apparatus cannot fake interference where none is allowed.

Modes: --sim (noiseless gates) | --fake (FakeMarrakesh feasibility) — both FREE.
"""
import argparse
import itertools
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

HERE = os.path.dirname(os.path.abspath(__file__))
G = 0.75
SHOTS_GAME = 1500
SHOTS_SENT = 2000
DELTA_WIN_FLOOR = 0.08     # frozen: WIN needs Delta_switch - 5SE > 0.08
THERM_BAND = 0.05          # frozen: |p1_null - (1-G)| + 5SE < 0.05 (each order) else NO-TEST
RETENTION_MIN = None       # set from --fake preview minus margin at prereg freeze


# ---------------------------------------------------------------- exact theory
def exact_targets(g, rho_in):
    """Direct Kraus computation of the 2-switch of constant-to-tau channels."""
    w = [g, 1 - g]
    ket = [np.array([[1.0], [0.0]]), np.array([[0.0], [1.0]])]
    kraus = {(k, j): np.sqrt(w[k]) * (ket[k] @ ket[j].T) for k in range(2) for j in range(2)}
    P0, P1 = np.diag([1.0, 0.0]), np.diag([0.0, 1.0])
    plus = np.array([[1.0], [1.0]]) / np.sqrt(2)
    rho_tot = np.kron(rho_in, plus @ plus.T)
    out = np.zeros((4, 4), dtype=complex)
    labels = list(kraus)
    for a in labels:
        for b in labels:
            W = np.kron(kraus[a] @ kraus[b], P0) + np.kron(kraus[b] @ kraus[a], P1)
            out += W @ rho_tot @ W.conj().T
    res = {}
    for sign, name in [(+1, "+"), (-1, "-")]:
        v = np.array([[1.0], [sign]]) / np.sqrt(2)
        Pc = np.kron(np.eye(2), v @ v.T)
        sub = Pc @ out @ Pc.conj().T
        p = float(np.real(np.trace(sub)))
        rho_t = np.array([[sub[2 * i, 2 * j] + sub[2 * i + 1, 2 * j + 1]
                           for j in range(2)] for i in range(2)]) / p
        res[name] = {"P": p, "p1": float(np.real(rho_t[1, 1]))}
    res["Delta"] = res["-"]["p1"] - res["+"]["p1"]
    return res


def self_validate():
    """g=1/2 must reproduce Exp106's independently-derived targets."""
    t0 = exact_targets(0.5, np.diag([1.0, 0.0]).astype(complex))
    assert abs(t0["+"]["P"] - 0.625) < 1e-12, t0
    assert abs(t0["+"]["p1"] - 0.4) < 1e-12, t0          # (rho+2I)/5 for |0>
    assert abs(t0["-"]["p1"] - 2 / 3) < 1e-12, t0        # (2I-rho)/3 for |0>
    return True


# ---------------------------------------------------------------- circuits
def build_circuit(t0, a10, a20, arm):
    """arm in {'switch','null_fwd','null_rev'}. Preps are basis states; pooling makes tau."""
    qc = QuantumCircuit(4, 2)
    if t0:
        qc.x(1)
    if a10:
        qc.x(2)
    if a20:
        qc.x(3)
    qc.h(0)
    qc.barrier()
    if arm == "switch":
        qc.cswap(0, 1, 2)   # CC3 part 1
        qc.cswap(0, 1, 3)   # CC3 part 2
        qc.barrier()
    if arm == "null_rev":
        qc.swap(1, 3)       # C3^{-1}: reverse definite order
        qc.swap(1, 2)
    else:
        qc.swap(1, 2)       # bare C3 (switch: completes U; null_fwd: definite order)
        qc.swap(1, 3)
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)        # control, X basis
    qc.measure(1, 1)        # target, Z basis
    return qc


def weight(t0, a10, a20, g=G):
    w = [g, 1 - g]
    return w[t0] * w[a10] * w[a20]


def pooled_stats(counts_by_label, g=G, conditional=True):
    """Weighted joint P(c,t). conditional=True (switch arm): Delta, p1|+-, P(+),
    delta-method SEs. conditional=False (null arms): UNCONDITIONED p1 + P(c=+)
    (C4529/Exp106 lesson: conditionals starve on a spectator control)."""
    joint = np.zeros((2, 2))            # [c][t]
    var = np.zeros((2, 2))
    for (t0, a10, a20), counts in counts_by_label.items():
        n = sum(counts.values())
        wgt = weight(t0, a10, a20, g)
        for key, c in counts.items():
            cbit, tbit = int(key[-1]), int(key[-2])   # clbit0 rightmost
            joint[cbit][tbit] += wgt * c / n
        for cbit in range(2):
            for tbit in range(2):
                p = sum(c for k, c in counts.items()
                        if int(k[-1]) == cbit and int(k[-2]) == tbit) / n
                var[cbit][tbit] += (wgt ** 2) * p * (1 - p) / n
    if not conditional:
        p1 = joint[:, 1].sum()
        return {"p1": p1, "p1_se": float(np.sqrt(var[:, 1].sum())),
                "P+": joint[0].sum()}
    out = {}
    for cbit, name in [(0, "+"), (1, "-")]:
        pc = joint[cbit].sum()
        p1 = joint[cbit][1] / pc
        # delta method for ratio joint[c][1]/pc
        v1, v0 = var[cbit][1], var[cbit][0]
        se = np.sqrt((joint[cbit][0] ** 2 * v1 + joint[cbit][1] ** 2 * v0)) / pc ** 2
        out[name] = {"P": pc, "p1": p1, "se": se}
    out["Delta"] = out["-"]["p1"] - out["+"]["p1"]
    out["Delta_se"] = float(np.hypot(out["+"]["se"], out["-"]["se"]))
    return out


def run(backend, transpile_kw, shots=SHOTS_GAME, seed=None):
    labels = list(itertools.product([0, 1], repeat=3))
    results = {}
    for arm in ["switch", "null_fwd", "null_rev"]:
        counts_by_label = {}
        for lab in labels:
            qc = build_circuit(*lab, arm=arm)
            tqc = transpile(qc, backend=backend, seed_transpiler=4558, **transpile_kw)
            counts_by_label[lab] = backend.run(tqc, shots=shots, seed_simulator=seed).result().get_counts()
        results[arm] = pooled_stats(counts_by_label, conditional=(arm == "switch"))
    # sentinels
    for name, lab, arm in [("retention", (0, 0, 0), "switch"),
                           ("deco_null", (1, 0, 0), "switch")]:
        qc = build_circuit(*lab, arm=arm)
        tqc = transpile(qc, backend=backend, seed_transpiler=4558, **transpile_kw)
        counts = backend.run(tqc, shots=SHOTS_SENT, seed_simulator=seed).result().get_counts()
        n = sum(counts.values())
        results[name] = {k: v / n for k, v in counts.items()}
        results[name + "_2q"] = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2)
    return results


def report(res, tag):
    th = exact_targets(G, np.diag([G, 1 - G]).astype(complex))
    print(f"\n=== {tag} (g={G}) ===")
    print(f"theory: P(+)={th['+']['P']:.4f}  p1|+={th['+']['p1']:.4f}  "
          f"p1|-={th['-']['p1']:.4f}  Delta={th['Delta']:.4f}  (causal: 0 exactly)")
    r = res["switch"]
    print(f"switch : P(+)={r['+']['P']:.4f}  p1|+={r['+']['p1']:.4f}(±{r['+']['se']:.4f})  "
          f"p1|-={r['-']['p1']:.4f}(±{r['-']['se']:.4f})  Delta={r['Delta']:.4f}(±{r['Delta_se']:.4f})")
    for arm in ["null_fwd", "null_rev"]:
        n = res[arm]
        print(f"{arm}: p1={n['p1']:.4f}(±{n['p1_se']:.4f})  [tau: {1 - G:.4f}]  "
              f"P(c=+)={n['P+']:.4f} (spectator, ideal 1)")
    ret = res["retention"].get("00", 0.0)
    dec = res["deco_null"]
    dec_pplus = sum(v for k, v in dec.items() if k[-1] == "0")
    print(f"sentinel retention P(c=+,t=0) = {ret:.4f} (ideal 1)   [2q count {res['retention_2q']}]")
    print(f"sentinel deco-null P(c=+) = {dec_pplus:.4f} (ideal 0.5)  P(t=0) = "
          f"{sum(v for k, v in dec.items() if k[-2] == '0'):.4f} (ideal 1)")
    # gates
    t_ok = all(abs(res[a]["p1"] - (1 - G)) + 5 * res[a]["p1_se"] < THERM_BAND
               for a in ["null_fwd", "null_rev"])
    win = res["switch"]["Delta"] - 5 * res["switch"]["Delta_se"] > DELTA_WIN_FLOOR
    cool = res["switch"]["+"]["p1"] + 5 * res["switch"]["+"]["se"] < (1 - G)
    print(f"gates: therm-null {'PASS' if t_ok else 'FAIL'} | "
          f"Delta-WIN {'PASS' if win else 'FAIL'} | cooling-direction {'PASS' if cool else 'FAIL'}")
    return {"therm_ok": bool(t_ok), "win": bool(win), "cool": bool(cool),
            "switch": res["switch"], "null_fwd": res["null_fwd"], "null_rev": res["null_rev"],
            "retention": ret, "deco_pplus": dec_pplus, "payload_2q": res["retention_2q"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--fake", action="store_true")
    args = ap.parse_args()
    assert self_validate()
    print("self-validation vs Exp106 g=1/2 targets: PASS")
    out = {}
    if args.sim:
        res = run(AerSimulator(), {"optimization_level": 1}, shots=20000, seed=4558)
        out["sim"] = report(res, "NOISELESS (AerSimulator)")
    if args.fake:
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
        res = run(AerSimulator.from_backend(FakeMarrakesh()), {"optimization_level": 3},
                  shots=SHOTS_GAME, seed=4558)
        out["fake"] = report(res, "FakeMarrakesh")
    if out:
        path = os.path.join(HERE, "..", "results", "exp108_feasibility.json")
        with open(path, "w") as f:
            json.dump(out, f, indent=2, default=float)
        print(f"\nwrote {os.path.abspath(path)}")
