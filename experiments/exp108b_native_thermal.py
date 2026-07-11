#!/usr/bin/env python3
"""
Exp108b — NATIVE-noise ICO thermal splitting: the chip's own T1 decay as the
working fluid (Whisper C4562, roadmap T2.4 delivered on the Exp108 harness).

WHAT CHANGES vs Exp108: the reservoir ancillas are no longer classically pooled
over basis preps — each ancilla is prepared |1> and then IDLES for a per-qubit
T1-calibrated delay, so its mixedness is produced by GENUINE system-environment
entanglement (the chip's amplitude damping), not by pseudorandom prep. The switch
itself (controlled 3-cycle on (t,a1,a2), 22-CZ class) is unchanged: SWAP with a
decayed ancilla IS a fully-thermalizing channel to that ancilla's state, so gamma=1
always — the native part is WHERE the entropy comes from. Demon-honesty upgrade:
in Exp108 we knew each shot's ancilla state (a demon could exploit the record);
here only the environment does.

WHY NOT "idle decay in the switch" directly: two idle delays on the SAME qubit
commute trivially (time cannot be routed) — no order signature. The SWAP-dilation
routing is what makes two copies of native decay orderable.

ASYMMETRIC RESERVOIRS: per-qubit T1 differs (a1=q6 201us, a2=q8 155us at design
time), so tau_A != tau_B in general — the true two-reservoir refrigeration setting.
Frozen PROCEDURE (not frozen numbers): theory targets are computed from the
MEASURED reservoir populations p_A, p_B (calibration arms: X + delay + SWAP into
target + measure target — same readout path as the payload observable), via the
same direct Kraus computation as Exp108, self-validating at the symmetric point.

Circuit schedule (all arms identical wall-time exposure):
  [X a1, X a2 (payload/calib only)] -> [delay(t_A,a1), delay(t_B,a2)] -> barrier
  -> [target prep, H control] -> switch / definite-order / calib SWAP -> measure.
  Control and target sit in |0> (Z eigenstates, T1-stable) during the delay, so
  added decoherence exposure vs Exp108 is negligible; depth class stays 22 CZ.

Modes: --sim (noiseless, basis-POOLED equivalent — exactly equal statistics by
switch linearity, validates circuit+estimator) | --fake (FakeMarrakesh, REAL
delay circuits against its T1 noise model — validates the native prep end-to-end).
"""
import argparse
import itertools
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
from exp108_ico_refrigeration import self_validate as validate_108_fixed_point

G_INPUT = 0.75            # frozen nominal input pooling weight (ground)
P_TARGET = 0.25           # design excited population for the delay calibration
SHOTS_GAME = 1500
SHOTS_SENT = 2000
DELTA_WIN_FLOOR = 0.06    # frozen absolute floor (theory Delta ~0.19-0.24 over p in band)
CALIB_BAND = (0.12, 0.40)  # frozen: measured p_A,p_B must land here, else NO-TEST
THERM_BAND = 0.06         # frozen: |p1_null - p_hat(last reservoir)| + 5SE < 0.06
# (0.05 was IMPOSSIBLE at draft shot counts: 5SE alone = 0.069 with zero real
#  deviation — caught by the FakeMarrakesh tier pre-freeze. 0.06 + raised shots
#  (calib 6000 / null 2500) gives 5SE ~ 0.042, leaving ~1.8pp for real breakage;
#  the gate guards gross channel failure, not sub-pp effects.)
SHOTS_NULL = 2500
SHOTS_CALIB = 6000
SHOTS_SWITCH = 3000


# ---------------------------------------------------------------- exact theory
def exact_targets_2tau(p_a, p_b, rho_in):
    """Switch of constant-to-tau_A and constant-to-tau_B channels (direct Kraus).
    tau_X = diag(1-p_X, p_X). Returns conditional P/p1 per control outcome + Delta.
    Self-validates at the symmetric point against Exp108's hardware-anchored code."""
    ket = [np.array([[1.0], [0.0]]), np.array([[0.0], [1.0]])]

    def kraus(p):
        w = [1 - p, p]
        return {(k, j): np.sqrt(w[k]) * (ket[k] @ ket[j].T)
                for k in range(2) for j in range(2)}

    KA, KB = kraus(p_a), kraus(p_b)
    P0, P1 = np.diag([1.0, 0.0]), np.diag([0.0, 1.0])
    plus = np.array([[1.0], [1.0]]) / np.sqrt(2)
    rho_tot = np.kron(rho_in, plus @ plus.T)
    out = np.zeros((4, 4), dtype=complex)
    for a in KA.values():
        for b in KB.values():
            W = np.kron(a @ b, P0) + np.kron(b @ a, P1)
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
    """(1) Exp108 fixed-point chain still passes (anchors to Exp106 hardware numbers).
    (2) Symmetric point of the 2-tau code reproduces Exp108's frozen targets."""
    assert validate_108_fixed_point()
    t = exact_targets_2tau(0.25, 0.25, np.diag([0.75, 0.25]).astype(complex))
    assert abs(t["+"]["P"] - 0.71875) < 1e-12, t
    assert abs(t["+"]["p1"] - 0.1847826086956522) < 1e-9, t
    assert abs(t["-"]["p1"] - 0.4166666666666667) < 1e-9, t
    return True


# ---------------------------------------------------------------- circuits
def build_circuit_native(t0, arm, delay_a_s, delay_b_s, thermal=True):
    """arm in {'switch','null_fwd','null_rev','calib_a','calib_b','retention','deco'}.
    thermal=True flips ancillas |1> before the delay (payload/calib);
    retention/deco keep ancillas |0>/deco-prep through the SAME delays."""
    qc = QuantumCircuit(4, 2)
    if thermal and arm not in ("retention", "deco"):
        qc.x(2)
        qc.x(3)
    qc.delay(delay_a_s, 2, unit="s")
    qc.delay(delay_b_s, 3, unit="s")
    qc.barrier()
    if arm == "deco":
        qc.x(1)                       # t=1, ancillas |0> -> orthogonal branches
    elif arm not in ("retention", "calib_a", "calib_b") and t0:
        qc.x(1)
    qc.h(0)
    qc.barrier()
    if arm == "switch" or arm in ("retention", "deco"):
        qc.cswap(0, 1, 2)
        qc.cswap(0, 1, 3)
        qc.barrier()
        qc.swap(1, 2)
        qc.swap(1, 3)
    elif arm == "null_fwd":
        qc.swap(1, 2)
        qc.swap(1, 3)
    elif arm == "null_rev":
        qc.swap(1, 3)
        qc.swap(1, 2)
    elif arm == "calib_a":
        qc.swap(1, 2)                 # reservoir A read through the payload path
    elif arm == "calib_b":
        qc.swap(1, 3)
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc


def pooled_input(counts_by_t0, g=G_INPUT, conditional=True):
    """Pool the 2 input labels with frozen weights (g, 1-g). Same estimator
    algebra as Exp108's pooled_stats, reduced to the input axis."""
    joint = np.zeros((2, 2))
    var = np.zeros((2, 2))
    for t0, counts in counts_by_t0.items():
        n = sum(counts.values())
        wgt = g if t0 == 0 else 1 - g
        for key, c in counts.items():
            cbit, tbit = int(key[-1]), int(key[-2])
            joint[cbit][tbit] += wgt * c / n
        for cbit in range(2):
            for tbit in range(2):
                p = sum(c for k, c in counts.items()
                        if int(k[-1]) == cbit and int(k[-2]) == tbit) / n
                var[cbit][tbit] += (wgt ** 2) * p * (1 - p) / n
    if not conditional:
        return {"p1": joint[:, 1].sum(), "p1_se": float(np.sqrt(var[:, 1].sum())),
                "P+": joint[0].sum()}
    out = {}
    for cbit, name in [(0, "+"), (1, "-")]:
        pc = joint[cbit].sum()
        p1 = joint[cbit][1] / pc
        v1, v0 = var[cbit][1], var[cbit][0]
        se = np.sqrt(joint[cbit][0] ** 2 * v1 + joint[cbit][1] ** 2 * v0) / pc ** 2
        out[name] = {"P": pc, "p1": p1, "se": se}
    out["Delta"] = out["-"]["p1"] - out["+"]["p1"]
    out["Delta_se"] = float(np.hypot(out["+"]["se"], out["-"]["se"]))
    return out


def grade_from_counts(all_counts, floors=True):
    """Frozen grading procedure. all_counts keys:
    ('switch',t0)/('null_fwd',t0)/('null_rev',t0) payload; 'calib_a','calib_b';
    'retention_start/mid/end'; 'deco'. Returns full report dict."""
    def p1_of(c):
        n = sum(c.values())
        return sum(v for k, v in c.items() if k[-2] == "1") / n, n

    p_a, n_a = p1_of(all_counts["calib_a"])
    p_b, n_b = p1_of(all_counts["calib_b"])
    th = exact_targets_2tau(p_a, p_b, np.diag([G_INPUT, 1 - G_INPUT]).astype(complex))
    sw = pooled_input({t0: all_counts[("switch", t0)] for t0 in (0, 1)})
    nf = pooled_input({t0: all_counts[("null_fwd", t0)] for t0 in (0, 1)}, conditional=False)
    nr = pooled_input({t0: all_counts[("null_rev", t0)] for t0 in (0, 1)}, conditional=False)
    rets = {k: all_counts[k].get("00", 0) / sum(all_counts[k].values())
            for k in all_counts if str(k).startswith("retention")}
    deco = all_counts["deco"]
    n_d = sum(deco.values())
    deco_pplus = sum(v for k, v in deco.items() if k[-1] == "0") / n_d

    se_a = np.sqrt(p_a * (1 - p_a) / n_a)
    se_b = np.sqrt(p_b * (1 - p_b) / n_b)
    g_cal = CALIB_BAND[0] < p_a < CALIB_BAND[1] and CALIB_BAND[0] < p_b < CALIB_BAND[1]
    g_ret = min(rets.values()) >= 0.80
    # definite fwd = A then B -> target carries tau_B; rev -> tau_A
    g_thm = (abs(nf["p1"] - p_b) + 5 * np.hypot(nf["p1_se"], se_b) < THERM_BAND and
             abs(nr["p1"] - p_a) + 5 * np.hypot(nr["p1_se"], se_a) < THERM_BAND)
    win = (sw["Delta"] - 5 * sw["Delta_se"] > DELTA_WIN_FLOOR and
           sw["+"]["p1"] + 5 * sw["+"]["se"] < min(p_a, p_b))   # colder than the COLDEST reservoir
    loss = sw["Delta"] + 5 * sw["Delta_se"] < DELTA_WIN_FLOOR
    if not (g_cal and g_ret and g_thm):
        verdict = "NO-TEST"
    else:
        verdict = "WIN" if win else ("LOSS" if loss else "AMBIGUOUS")
    return {"p_a": p_a, "p_b": p_b, "theory": th, "switch": sw,
            "null_fwd": nf, "null_rev": nr, "retention": rets,
            "deco_pplus": deco_pplus, "gates": {"calib": g_cal, "retention": g_ret,
                                                "therm": g_thm},
            "verdict": verdict,
            "sigma_vs_causal": sw["Delta"] / sw["Delta_se"]}


def run_tier(backend, transpile_kw, t1_a, t1_b, use_delays, shots=SHOTS_GAME, seed=None):
    """use_delays=False -> noiseless-equivalent tier: basis-pool the ancillas at
    p=P_TARGET via Exp108 machinery-equivalent circuits (delay is a no-op there)."""
    d_a, d_b = t1_a * np.log(1 / P_TARGET), t1_b * np.log(1 / P_TARGET)
    all_counts = {}

    def run_qc(qc, n):
        tqc = transpile(qc, backend=backend, seed_transpiler=4562, **transpile_kw)
        return backend.run(tqc, shots=n, seed_simulator=seed).result().get_counts(), tqc

    if use_delays:
        for arm in ("switch", "null_fwd", "null_rev"):
            n = SHOTS_SWITCH if arm == "switch" else SHOTS_NULL
            for t0 in (0, 1):
                c, _ = run_qc(build_circuit_native(t0, arm, d_a, d_b), n)
                all_counts[(arm, t0)] = c
        for arm in ("calib_a", "calib_b"):
            c, _ = run_qc(build_circuit_native(0, arm, d_a, d_b), SHOTS_CALIB)
            all_counts[arm] = c
    else:
        # basis-pooled equivalent (exact by linearity): ancilla labels weighted
        from exp108_ico_refrigeration import build_circuit as build_108
        for arm108, arm in (("switch", "switch"), ("null_fwd", "null_fwd"),
                            ("null_rev", "null_rev")):
            for t0 in (0, 1):
                pooled = {}
                for a1, a2 in itertools.product((0, 1), repeat=2):
                    qc = build_108(t0, a1, a2, arm=arm108)
                    c, _ = run_qc(qc, shots)
                    w = ((1 - P_TARGET) if a1 == 0 else P_TARGET) * \
                        ((1 - P_TARGET) if a2 == 0 else P_TARGET)
                    for k, v in c.items():
                        pooled[k] = pooled.get(k, 0) + w * v
                all_counts[(arm, t0)] = {k: int(round(v)) for k, v in pooled.items()}
        # calib arms in the pooled tier are exact by construction
        n = shots
        all_counts["calib_a"] = {"010": int(n * P_TARGET), "000": n - int(n * P_TARGET)}
        all_counts["calib_b"] = {"010": int(n * P_TARGET), "000": n - int(n * P_TARGET)}
        # fix key width (2 clbits)
        all_counts["calib_a"] = {"10": int(n * P_TARGET), "00": n - int(n * P_TARGET)}
        all_counts["calib_b"] = {"10": int(n * P_TARGET), "00": n - int(n * P_TARGET)}
    for rep in ("start", "mid", "end"):
        c, tqc = run_qc(build_circuit_native(0, "retention", d_a, d_b), SHOTS_SENT)
        all_counts[f"retention_{rep}"] = c
    c, _ = run_qc(build_circuit_native(0, "deco", d_a, d_b), SHOTS_SENT)
    all_counts["deco"] = c
    n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
             and inst.operation.name != "barrier")
    return all_counts, n2


def report(rep, n2, tag):
    print(f"\n=== {tag} ===")
    print(f"calib: p_A={rep['p_a']:.4f} p_B={rep['p_b']:.4f}  (band {CALIB_BAND})")
    th = rep["theory"]
    print(f"theory@(p_A,p_B): P(+)={th['+']['P']:.4f} p1|+={th['+']['p1']:.4f} "
          f"p1|-={th['-']['p1']:.4f} Delta={th['Delta']:.4f} (causal 0 exactly)")
    sw = rep["switch"]
    print(f"switch: P(+)={sw['+']['P']:.4f} p1|+={sw['+']['p1']:.4f}(±{sw['+']['se']:.4f}) "
          f"p1|-={sw['-']['p1']:.4f}(±{sw['-']['se']:.4f}) Delta={sw['Delta']:.4f}(±{sw['Delta_se']:.4f})")
    print(f"null_fwd p1={rep['null_fwd']['p1']:.4f} (tau_B={rep['p_b']:.4f}) | "
          f"null_rev p1={rep['null_rev']['p1']:.4f} (tau_A={rep['p_a']:.4f})")
    print(f"retention {rep['retention']} | deco P(c=+)={rep['deco_pplus']:.4f} | payload 2q={n2}")
    print(f"gates {rep['gates']} -> VERDICT {rep['verdict']} "
          f"({rep['sigma_vs_causal']:.1f} sigma vs causal 0)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--fake", action="store_true")
    args = ap.parse_args()
    assert self_validate()
    print("self-validation (Exp108 fixed-point chain + symmetric-point identity): PASS")
    out = {}
    if args.sim:
        counts, n2 = run_tier(AerSimulator(), {"optimization_level": 1},
                              200e-6, 155e-6, use_delays=False, shots=20000, seed=4562)
        rep = grade_from_counts(counts)
        report(rep, n2, "NOISELESS (basis-pooled equivalent, p=0.25)")
        out["sim"] = rep
    if args.fake:
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
        fb = FakeMarrakesh()
        # use the fake backend's own T1s for the delay calibration (as submit will)
        t1s = {q: fb.qubit_properties(q).t1 for q in (6, 8)}
        print(f"FakeMarrakesh T1: a1(q6)={t1s[6]*1e6:.0f}us a2(q8)={t1s[8]*1e6:.0f}us")
        counts, n2 = run_tier(AerSimulator.from_backend(fb),
                              {"optimization_level": 3, "initial_layout": [5, 7, 6, 8]},
                              t1s[6], t1s[8], use_delays=True, seed=4562)
        rep = grade_from_counts(counts)
        report(rep, n2, "FakeMarrakesh (REAL delay circuits, native T1 decay)")
        out["fake"] = rep
    if out:
        path = os.path.join(HERE, "..", "results", "exp108b_feasibility.json")
        with open(path, "w") as f:
            json.dump(out, f, indent=2, default=float)
        print(f"\nwrote {os.path.abspath(path)}")
