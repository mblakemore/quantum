#!/usr/bin/env python3
"""Exp-STETH-(a) TWIRLED re-fly — Pauli-twirled channel to fix the non-Pauli gate-FAIL (annex §3).

The first flight (job d9g0vq2neu4c739q6lag) FAILED the SPAM gate because the 10us idle channel is NOT
pure-Pauli (T1 amplitude damping) -> the two-copy Choi eigenvalue equals the single-copy eigenvalue
ONLY for a Pauli channel. FIX (this re-fly): PAULI-TWIRL the channel (randomized compiling) so the
effective channel IS Pauli, then the two arms should AGREE and the two-copy Z-control should return
to ~1.

TWIRL: around the system idle, insert a random Pauli P (before) and the SAME P (after). For the
ideal-identity idle, P.I.P = P^2 = I -> the logical operation is preserved, but the NOISE during the
idle is conjugated by P; averaging over random P twirls the channel into a Pauli channel. K random
twirls per configuration, averaged in decode.
Changes from the first flight: idle 10us -> 5us (ancilla survives better; T2*~4us measured last flight,
so 5us still gives measurable lambda_X<1); ancilla keeps the DD echo (T2 refocus). Residual ancilla
T1 (~2.5% over 5us) is accepted and shows in the Z-control if it dominates.

GATE (unchanged): two-copy ratio-corrected lambda_{P^n} must AGREE with conventional within CIs, AND
the two-copy Z-control must return to ~1. Pass -> SPAM cancellation validated on a Pauli channel.
Substrate: claude-fable-5, Whisper C4971.
"""
import os, sys, json, argparse
import numpy as np
from qiskit import QuantumCircuit, transpile

QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BACKEND = "ibm_marrakesh"
DELAY_NS = 5000            # 5 us idle (shorter than the failed flight's 10us -> ancilla survives)
NS = [1, 2]
K_TWIRL = 8               # random Pauli twirls per configuration (randomized compiling)
SHOTS = 4000
PAULIS = ["X", "Z"]       # X^n informative, Z^n ~1 control


def _pauli_gate(qc, q, p):
    if p == "X": qc.x(q)
    elif p == "Y": qc.y(q)
    elif p == "Z": qc.z(q)
    # I: nothing


def _basis(qc, qubits, pauli):
    for q in qubits:
        if pauli == "X": qc.h(q)
        elif pauli == "Y": qc.sdg(q); qc.h(q)


def twocopy_circuit(n, pauli, apply_delay, twirl):
    """n Bell pairs; system idle Pauli-twirled by `twirl` (tuple of P per system qubit); ancilla DD."""
    qc = QuantumCircuit(2 * n, 2 * n)
    for i in range(n):
        qc.h(i); qc.cx(i, n + i)
    qc.barrier()
    if apply_delay:
        for i in range(n):
            _pauli_gate(qc, i, twirl[i])              # twirl P before idle (system)
            qc.delay(DELAY_NS, i, unit="ns")          # Lambda = idle on system
            _pauli_gate(qc, i, twirl[i])              # twirl P after (P^2=I logically)
            # ancilla DD echo (tau/2 - X - tau/2 - X, nets to I, refocuses T2)
            qc.delay(DELAY_NS // 2, n + i, unit="ns"); qc.x(n + i)
            qc.delay(DELAY_NS // 2, n + i, unit="ns"); qc.x(n + i)
    qc.barrier()
    _basis(qc, range(2 * n), pauli)
    qc.measure(range(2 * n), range(2 * n))
    return qc


def conventional_circuit(n, pauli, apply_delay, twirl):
    qc = QuantumCircuit(n, n)
    for q in range(n):
        if pauli == "X": qc.h(q)
        elif pauli == "Y": qc.h(q); qc.s(q)
    qc.barrier()
    if apply_delay:
        for q in range(n):
            _pauli_gate(qc, q, twirl[q])
            qc.delay(DELAY_NS, q, unit="ns")
            _pauli_gate(qc, q, twirl[q])
    qc.barrier()
    _basis(qc, range(n), pauli)
    qc.measure(range(n), range(n))
    return qc


def _parity(counts):
    tot = sum(counts.values()); acc = 0.0
    for k, v in counts.items():
        acc += v * (1 - 2 * (k.replace(" ", "").count("1") % 2))
    return acc / tot


def build_all(seed0=20260722):
    rng = np.random.default_rng(seed0)
    circuits, index = [], []
    for n in NS:
        for P in PAULIS:
            for arm, mk in (("twocopy", twocopy_circuit), ("conv", conventional_circuit)):
                for dly in (True, False):
                    for k in range(K_TWIRL):
                        tw = tuple(rng.choice(list("IXYZ")) for _ in range(n))
                        circuits.append(mk(n, P, dly, tw))
                        index.append({"n": n, "pauli": P, "arm": arm, "delay": dly, "twirl": "".join(tw)})
    return circuits, index


def local_sanity():
    """Noiseless: lambda=1 both arms across all twirls (P^2=I preserves logic). With a NON-PAULI sim
    channel (amplitude damping) the twirl should make the two arms agree better than the un-twirled
    (harder to show in Aer without per-twirl averaging; here we confirm noiseless correctness)."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); rng = np.random.default_rng(1)
    print("noiseless (expect lambda~1 both arms, all twirls):")
    for n in (1, 2):
        for arm, mk in (("twocopy", twocopy_circuit), ("conv", conventional_circuit)):
            num = den = 0.0
            for k in range(K_TWIRL):
                tw = tuple(rng.choice(list("IXYZ")) for _ in range(n))
                num += _parity(sim.run(transpile(mk(n, "X", True, tw), sim), shots=4000, seed_simulator=1).result().get_counts())
                den += _parity(sim.run(transpile(mk(n, "X", False, tw), sim), shots=4000, seed_simulator=1).result().get_counts())
            print(f"  n={n} {arm} lam_X (twirl-avg)={num/den:.3f}")


def submit():
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(BACKEND)
    circuits, index = build_all()
    tqc = transpile(circuits, backend=backend, optimization_level=1, seed_transpiler=3211)
    print(f"transpiled {len(tqc)} circuits on {BACKEND}; max depth {max(c.depth() for c in tqc)}")
    job = SamplerV2(mode=backend).run(tqc, shots=SHOTS)
    man = {"exp": "steth_a_twirled", "backend": BACKEND, "job_id": job.job_id(), "shots": SHOTS,
           "delay_ns": DELAY_NS, "k_twirl": K_TWIRL, "index": index,
           "note": "Pauli-twirled two-copy vs conventional lambda_{P^n} agreement (fix non-Pauli fail)"}
    out = os.path.join(QROOT, "results", "exp_steth_a_twirled_manifest.json")
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(tqc)} circuits) -> {os.path.relpath(out)}")


def decode():
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(QROOT, "results", "exp_steth_a_twirled_manifest.json")))
    res = _get_ibm_service().job(man["job_id"]).result(); idx = man["index"]; sh = man["shots"]

    def counts(i):
        d = res[i].data; return getattr(d, list(d.__dict__.keys())[0]).get_counts()

    # average parity over twirls per (n,P,arm,delay)
    agg = {}
    for i, r in enumerate(idx):
        key = (r["n"], r["pauli"], r["arm"], r["delay"])
        agg.setdefault(key, []).append(_parity(counts(i)))
    rows = []
    for n in NS:
        for P in PAULIS:
            lam = {}
            for arm in ("twocopy", "conv"):
                num = np.mean(agg[(n, P, arm, True)]); den = np.mean(agg[(n, P, arm, False)])
                lam[arm] = num / den if abs(den) > 1e-6 else float("nan")
            diff = abs(lam["twocopy"] - lam["conv"]); se = np.sqrt(2 / (sh * man["k_twirl"])) * 2
            rows.append({"n": n, "pauli": P, "lam_twocopy": round(float(lam["twocopy"]), 4),
                         "lam_conv": round(float(lam["conv"]), 4), "abs_diff": round(float(diff), 4),
                         "agree_within_2se": bool(diff < 2 * se), "approx_2se": round(float(2 * se), 4)})
            print(f"  n={n} {P}^n: twocopy={lam['twocopy']:.3f} conv={lam['conv']:.3f} "
                  f"|diff|={diff:.3f} (~2SE {2*se:.3f}) agree={rows[-1]['agree_within_2se']}")
    # Z-control diagnostic: two-copy Z should return to ~1 after twirling
    zctrl = [r["lam_twocopy"] for r in rows if r["pauli"] == "Z"]
    z_ok = all(abs(z - 1.0) < 0.10 for z in zctrl)
    xrows = [r for r in rows if r["pauli"] == "X"]
    gate = all(r["agree_within_2se"] for r in xrows) and z_ok
    out = {"card": "exp_steth_a_twirled_decoded", "job_id": man["job_id"], "backend": man["backend"],
           "substrate": "claude-fable-5", "cycle": "C4971", "delay_ns": man["delay_ns"],
           "k_twirl": man["k_twirl"], "rows": rows, "twocopy_Z_control": zctrl,
           "Z_control_returns_to_1": z_ok,
           "SPAM_GATE_twirled": "PASS" if gate else "FAIL",
           "note": ("Pauli-twirl fixed the non-Pauli fail: X^n arms agree within 2SE AND two-copy "
                    "Z-control ~1 -> SPAM cancellation validated on a Pauli channel" if gate else
                    "still failing: check Z-control (ancilla residual) vs X-agreement to localize")}
    op = os.path.join(QROOT, "results", "exp_steth_a_twirled_decoded.json")
    json.dump(out, open(op, "w"), indent=1)
    print(f"\nTWIRLED SPAM GATE: {out['SPAM_GATE_twirled']} (Z-control->1: {z_ok})")
    print(f"decoded -> {os.path.relpath(op)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a in ("sanity", "submit", "decode"):
        ap.add_argument(f"--{a}", action="store_true")
    args = ap.parse_args()
    if args.sanity: local_sanity()
    elif args.submit: submit()
    elif args.decode: decode()
    else: print("use --sanity | --submit | --decode")
