#!/usr/bin/env python3
"""Exp-STETH-(a) ZZ-AWARE re-fly — PIN the same physical system qubits in both arms (annex §3).

The twirled re-fly PASSED at n=1 but n=2 showed a coherent 2-qubit systematic (two-copy X-parity
consistently ~-0.55 vs clean ref +0.93). Diagnosis refined: the two-copy (4-qubit) and conventional
(2-qubit) circuits were routed by the transpiler to DIFFERENT physical qubits -> different s0-s1 ZZ
crosstalk -> the two arms measured different effective channels. FIX (this re-fly): PIN THE SAME
PHYSICAL SYSTEM QUBITS in both arms (initial_layout), so both experience the identical system-system
ZZ; the single-qubit Pauli twirl then Pauli-izes that ZZ IDENTICALLY in both arms -> they should
AGREE (even if the resulting Pauli eigenvalue is negative, both should recover the same value).
Keeps the twirl (randomized compiling) + ancilla DD (refocuses ancilla T2 + system-ancilla ZZ).

Same system pair as the URB gate + Ember §3(b): SYS=[88,89] (low-CZ), ANC=[91,90].
Substrate: claude-fable-5, Whisper C4971.
"""
import os, sys, json, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qiskit import transpile
from exp_steth_a_twirled import (twocopy_circuit, conventional_circuit, _parity,
                                 DELAY_NS, K_TWIRL, PAULIS)

QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BACKEND = "ibm_marrakesh"
SYS = [88, 89]            # pinned system qubits (SAME for both arms)
ANC = [91, 90]            # ancilla partners (two-copy only)
NS = [1, 2]
SHOTS = 4000


def build_arm(mk, n, is_twocopy, seed0):
    """Build K twirled circuits for one arm at fixed n; return (circuits, index, layout)."""
    rng = np.random.default_rng(seed0)
    circs, idx = [], []
    for P in PAULIS:
        for dly in (True, False):
            for k in range(K_TWIRL):
                tw = tuple(rng.choice(list("IXYZ")) for _ in range(n))
                circs.append(mk(n, P, dly, tw))
                idx.append({"n": n, "pauli": P, "arm": "twocopy" if is_twocopy else "conv",
                            "delay": dly, "twirl": "".join(tw)})
    layout = (SYS[:n] + ANC[:n]) if is_twocopy else SYS[:n]
    return circs, idx, layout


def submit():
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(BACKEND)
    all_tqc, index = [], []
    for n in NS:
        for mk, is2c in ((twocopy_circuit, True), (conventional_circuit, False)):
            circs, idx, layout = build_arm(mk, n, is2c, seed0=20260722 + n * 10 + int(is2c))
            tqc = transpile(circs, backend=backend, optimization_level=1,
                            initial_layout=layout, seed_transpiler=3211)  # PINNED same system qubits
            all_tqc += list(tqc); index += idx
    print(f"transpiled {len(all_tqc)} circuits on {BACKEND}; pinned SYS={SYS} ANC={ANC}; "
          f"max depth {max(c.depth() for c in all_tqc)}")
    job = SamplerV2(mode=backend).run(all_tqc, shots=SHOTS)
    man = {"exp": "steth_a_zzaware", "backend": BACKEND, "job_id": job.job_id(), "shots": SHOTS,
           "delay_ns": DELAY_NS, "k_twirl": K_TWIRL, "sys": SYS, "anc": ANC, "index": index,
           "note": "PINNED same system qubits both arms + twirl + ancilla DD (fix n=2 placement/ZZ)"}
    out = os.path.join(QROOT, "results", "exp_steth_a_zzaware_manifest.json")
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(all_tqc)} circuits) -> {os.path.relpath(out)}")


def decode():
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(QROOT, "results", "exp_steth_a_zzaware_manifest.json")))
    res = _get_ibm_service().job(man["job_id"]).result(); idx = man["index"]; sh = man["shots"]

    def cnt(i):
        d = res[i].data; return getattr(d, list(d.__dict__.keys())[0]).get_counts()

    agg = {}
    for i, r in enumerate(idx):
        agg.setdefault((r["n"], r["pauli"], r["arm"], r["delay"]), []).append(_parity(cnt(i)))
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
    xrows = [r for r in rows if r["pauli"] == "X"]
    gate = all(r["agree_within_2se"] for r in xrows)
    out = {"card": "exp_steth_a_zzaware_decoded", "job_id": man["job_id"], "backend": man["backend"],
           "substrate": "claude-fable-5", "cycle": "C4971", "pinned_sys": man["sys"],
           "rows": rows, "SPAM_GATE_pinned": "PASS" if gate else "FAIL",
           "note": ("pinning the same system qubits + twirl -> both arms measure the same channel and "
                    "AGREE at all small n (incl n=2) -> SPAM cancellation validated on a Pauli channel"
                    if gate else "still failing at some n -> the n=2 residual is not just placement; "
                    "investigate the specific disagreeing (n,P)")}
    op = os.path.join(QROOT, "results", "exp_steth_a_zzaware_decoded.json")
    json.dump(out, open(op, "w"), indent=1)
    print(f"\nZZ-AWARE (pinned) SPAM GATE: {out['SPAM_GATE_pinned']}")
    print(f"decoded -> {os.path.relpath(op)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a in ("submit", "decode"):
        ap.add_argument(f"--{a}", action="store_true")
    args = ap.parse_args()
    if args.submit: submit()
    elif args.decode: decode()
    else: print("use --submit | --decode")
