#!/usr/bin/env python3
"""
Exp98 (Elder C6357) — LOADER-DEPTH BOUNDARY ON REAL HARDWARE.

Executes the forward test pre-registered by Ember F79/Exp96 (C4082): run the SAME
shallow 1-qubit IWM loader and deep 3-qubit QQQ loader in ONE ibm_marrakesh
submission, k=0..5, and confirm the noisy-MLE-err depth gap survives on silicon.

Sim (FakeMarrakesh, Ember pred_c4082_001 VALIDATED): QQQ-deep multi-k MLE err 0.111
vs IWM-shallow 0.0029, gap +0.108; QQQ 2q-count 7->124 over k, IWM 0 at every k.
F78 (Elder C6349, real HW): QQQ-deep multi-k MLE err 0.154.

Reuses the EXACT Exp95/F78 QQQ loader and the EXACT Exp96 IWM loader (verbatim
imports) so the only difference between the two arms is loader depth — minimal new
bug surface.

Pre-reg gates (pinned in experiments/98-loader-depth-boundary-hardware-preregistration.md):
  HW1 (PRIMARY): errQ - errI > +0.03            (depth boundary survives on silicon)
  HW2:           errI < 0.05 AND errI <= 3*plainI (shallow loader stays clean)
  HW3:           QQQ 2q@k5 > 3 * IWM 2q@k5        (2q-depth is the mechanism)
  pred_c6357_001 = HW1 AND HW2 AND HW3

USAGE:
  python3 run_exp98_loader_depth_hardware.py --sim        # noiseless gate + FakeMarrakesh preview (free)
  python3 run_exp98_loader_depth_hardware.py --submit     # ONE job, 14 PUBs -> ibm_marrakesh
  python3 run_exp98_loader_depth_hardware.py --finalize JOB_ID
"""
import sys, os, json, math, argparse
import numpy as np
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# deep 3-qubit QQQ loader — reused VERBATIM from Exp95/F78
from qae_qqq_tail_demo import (
    build_A as build_A_qqq, grover_Q as grover_Q_qqq, bucket_probs,
    true_tail_discrete, _msb_one_prob, N_QUBITS as N_QQQ, SHOTS, SEED_TRANSP, BACKEND_NAME,
)
# shallow 1-qubit IWM loader — reused VERBATIM from Exp96/F79
from run_exp96_loader_depth_boundary import build_A_iwm, grover_Q_iwm, A_TRUE_IWM

K_VALUES = [0, 1, 2, 3, 4, 5]
# PUB layout: QQQ k0..5, IWM k0..5, then QQQ-k0-retest, IWM-k0-retest (drift anchors)
PUB_SPEC = ([("QQQ", k) for k in K_VALUES] + [("IWM", k) for k in K_VALUES]
            + [("QQQ", 0), ("IWM", 0)])
PUB_LABELS = [f"{ldr}_k{k}" for (ldr, k) in PUB_SPEC[:12]] + ["QQQ_k0_retest", "IWM_k0_retest"]

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
EXP_DIR     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
JOBIDS_PATH = os.path.join(EXP_DIR, "exp98_jobids.json")
os.makedirs(RESULTS_DIR, exist_ok=True); os.makedirs(EXP_DIR, exist_ok=True)

# HW1 threshold inherited from Ember's confirmed sim gap
HW1_GAP = 0.03
HW2_ABS = 0.05
HW2_MULT = 3.0
HW3_MULT = 3.0


def loaders():
    """Return {name: (A, Q, nq, obj_qubit, a_true)} for both arms."""
    probs = bucket_probs()[0]
    A_qqq = build_A_qqq(probs, measure=False)
    Q_qqq, _ = grover_Q_qqq(probs)
    a_qqq = true_tail_discrete(probs)
    Q_iwm, A_iwm = grover_Q_iwm()
    return {
        "QQQ": (A_qqq, Q_qqq, N_QQQ, N_QQQ - 1, a_qqq),
        "IWM": (A_iwm, Q_iwm, 1, 0, A_TRUE_IWM),
    }


def build_grover_circuit(A, Q, nq, obj_qubit, k):
    qc = QuantumCircuit(nq, 1)
    qc.compose(A, list(range(nq)), inplace=True)
    for _ in range(k):
        qc.compose(Q, list(range(nq)), inplace=True)
    qc.measure(obj_qubit, 0)
    return qc


def ideal_P(a_true, k):
    th = math.asin(math.sqrt(a_true))
    return math.sin((2 * k + 1) * th) ** 2


def mle_over_k(pmeas_by_k, shots):
    def nll(a):
        if a <= 1e-6 or a >= 1 - 1e-6:
            return 1e12
        ll = 0.0
        for k, p in pmeas_by_k:
            th = (2 * k + 1) * math.asin(math.sqrt(a))
            pk = max(1e-10, min(1 - 1e-10, math.sin(th) ** 2))
            m = int(round(p * shots))
            ll += m * math.log(pk) + (shots - m) * math.log(1 - pk)
        return -ll
    return float(optimize.minimize_scalar(nll, bounds=(1e-3, 1 - 1e-3), method='bounded').x)


def run_sim():
    """Correctness gate: noiseless must reproduce ideal for BOTH loaders; FakeMarrakesh
    preview should reproduce Ember's confirmed sim gap before we spend QPU."""
    L = loaders()
    noiseless = AerSimulator()
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    fake = AerSimulator.from_backend(FakeMarrakesh())
    print("Exp98 SIM gate — loader-depth boundary (noiseless correctness + FakeMarrakesh preview)", flush=True)

    summ = {}
    for name, (A, Q, nq, obj, a_true) in L.items():
        ideal = [ideal_P(a_true, k) for k in K_VALUES]
        p_nl, p_noisy, depth_rows = [], [], []
        for k in K_VALUES:
            qc = build_grover_circuit(A, Q, nq, obj, k)
            tq = transpile(qc, noiseless, seed_transpiler=SEED_TRANSP)
            p_nl.append(_msb_one_prob(noiseless.run(tq, shots=SHOTS).result().get_counts()))
            tqf = transpile(qc, fake, optimization_level=1, seed_transpiler=SEED_TRANSP)
            cf = fake.run(tqf, shots=SHOTS).result().get_counts()
            p_noisy.append(_msb_one_prob(cf))
            n2q = sum(1 for g in tqf.data if g.operation.num_qubits == 2)
            depth_rows.append({"k": k, "depth": tqf.depth(), "n2q": n2q})
        nl_dev = max(abs(p - i) for p, i in zip(p_nl, ideal))
        err_noisy = abs(mle_over_k(list(zip(K_VALUES, p_noisy)), SHOTS) - a_true)
        plain = abs(p_noisy[0] - a_true)
        summ[name] = {"a_true": a_true, "noiseless_max_dev": nl_dev, "err_noisy": err_noisy,
                      "plain_read_err": plain, "n2q_at_k5": depth_rows[-1]["n2q"], "depth_rows": depth_rows}
        print(f"  [{name}] noiseless max|P-ideal|={nl_dev:.4f} (validates Q)  "
              f"| FakeMarrakesh MLE err={err_noisy:.4f}  plain_k0_err={plain:.4f}  2q@k5={depth_rows[-1]['n2q']}", flush=True)

    gap = summ["QQQ"]["err_noisy"] - summ["IWM"]["err_noisy"]
    print(f"\n  FakeMarrakesh depth gap (QQQ-IWM) = {gap:+.4f}  (Ember confirmed +0.108; HW1 wants >{HW1_GAP})", flush=True)
    print(f"  noiseless correctness: {'PASS' if max(summ[n]['noiseless_max_dev'] for n in summ) < 0.05 else 'FAIL — DO NOT SUBMIT'}", flush=True)
    out = {"experiment": "exp98_loader_depth_hardware", "phase": "sim_gate", "cycle": 6357,
           "author": "elder", "shots": SHOTS, "k_values": K_VALUES, "loaders": summ,
           "fakemarrakesh_gap_qqq_minus_iwm": gap}
    path = os.path.join(RESULTS_DIR, "exp98_sim.json")
    with open(path, "w") as f: json.dump(out, f, indent=2)
    print(f"  saved -> {path}", flush=True)


def run_submit():
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    L = loaders()
    service = _get_ibm_service(); backend = service.backend(BACKEND_NAME)
    print(f"  Backend: {backend.name} | pending={backend.status().pending_jobs}", flush=True)
    pubs, depths = [], []
    for (ldr, k), label in zip(PUB_SPEC, PUB_LABELS):
        A, Q, nq, obj, a_true = L[ldr]
        qc = build_grover_circuit(A, Q, nq, obj, k)
        tq = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSP)
        n2q = sum(1 for g in tq.data if g.operation.num_qubits == 2)
        depths.append({"label": label, "loader": ldr, "k": k, "depth": tq.depth(), "n2q": n2q})
        pubs.append((tq,))
        print(f"  {label:16s} transpiled depth={tq.depth():4d} 2q={n2q}", flush=True)
    sampler = SamplerV2(mode=backend); sampler.options.default_shots = SHOTS
    job = sampler.run(pubs); jid = job.job_id()
    print(f"  ONE job, {len(pubs)} PUBs, job_id={jid} ({SHOTS} shots each)", flush=True)
    L2 = loaders()
    rec = {"experiment": "exp98", "cycle": 6357, "backend": BACKEND_NAME, "shots": SHOTS,
           "job_id": jid, "pub_spec": PUB_SPEC, "pub_labels": PUB_LABELS, "depths": depths,
           "a_true": {"QQQ": L2["QQQ"][4], "IWM": L2["IWM"][4]}}
    with open(JOBIDS_PATH, "w") as f: json.dump(rec, f, indent=2)
    print(f"  saved -> {JOBIDS_PATH}", flush=True)


def run_finalize(jid):
    from run_exp66_qpu_partb import _get_ibm_service
    rec = json.load(open(JOBIDS_PATH)) if os.path.exists(JOBIDS_PATH) else {}
    pub_spec = [tuple(x) for x in rec.get("pub_spec", PUB_SPEC)]
    depths = {d["label"]: d for d in rec.get("depths", [])}
    a_true = rec.get("a_true") or {"QQQ": loaders()["QQQ"][4], "IWM": loaders()["IWM"][4]}
    service = _get_ibm_service(); job = service.job(jid); status = str(job.status())
    print(f"  job {jid} status={status}", flush=True)
    if "DONE" not in status.upper():
        print("  -> not DONE; retry later."); return
    res = job.result()

    # per-PUB measured P(obj=1)
    per_pub = []
    for i, (ldr, k) in enumerate(pub_spec):
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0]
        p = _msb_one_prob(getattr(databin, reg).get_counts())
        per_pub.append({"i": i, "loader": ldr, "k": k, "p": p})
        print(f"  PUB[{i:2d}] {ldr}_k{k}  P(obj=1)={p:.4f}", flush=True)

    grade = {}
    for ldr in ("QQQ", "IWM"):
        pk = [(d["k"], d["p"]) for d in per_pub[:12] if d["loader"] == ldr]  # main sweep only
        at = a_true[ldr]
        mle = mle_over_k(pk, SHOTS); err = abs(mle - at)
        p0 = next(p for (k, p) in pk if k == 0); plain = abs(p0 - at)
        # k0 retest drift anchor
        retest = [d["p"] for d in per_pub[12:] if d["loader"] == ldr]
        k0_spread = abs(p0 - retest[0]) if retest else None
        n2q_k5 = depths.get(f"{ldr}_k5", {}).get("n2q")
        grade[ldr] = {"a_true": at, "mle": mle, "mle_err": err, "plain_read_err": plain,
                      "k0_retest_spread": k0_spread, "n2q_at_k5": n2q_k5}
        print(f"  [{ldr}] MLE a*={mle:.4f} err={err:.4f} | plain k0 err={plain:.4f} "
              f"| 2q@k5={n2q_k5} | k0 retest spread={k0_spread}", flush=True)

    errQ, errI = grade["QQQ"]["mle_err"], grade["IWM"]["mle_err"]
    plainI = grade["IWM"]["plain_read_err"]
    n2qQ, n2qI = grade["QQQ"]["n2q_at_k5"], grade["IWM"]["n2q_at_k5"]
    hw1 = (errQ - errI) > HW1_GAP
    hw2 = (errI < HW2_ABS) and (errI <= HW2_MULT * max(plainI, 1e-9))
    hw3 = (n2qQ is not None and n2qI is not None) and (n2qQ > HW3_MULT * max(1, n2qI))
    pred = bool(hw1 and hw2 and hw3)

    print("\n================ GRADE (pre-registered HW1/HW2/HW3) ================", flush=True)
    print(f"  HW1 depth-boundary survives: errQ({errQ:.4f}) - errI({errI:.4f}) = {errQ-errI:+.4f} > {HW1_GAP} -> {'PASS' if hw1 else 'FAIL'}", flush=True)
    print(f"  HW2 shallow stays clean: errI {errI:.4f} < {HW2_ABS} AND <= {HW2_MULT}x plainI({plainI:.4f}) -> {'PASS' if hw2 else 'FAIL'}", flush=True)
    print(f"  HW3 2q-depth mechanism: QQQ 2q@k5 {n2qQ} > {HW3_MULT}x IWM {n2qI} -> {'PASS' if hw3 else 'FAIL'}", flush=True)
    print(f"  pred_c6357_001 (HW1 & HW2 & HW3): {'CONFIRMED' if pred else 'NOT confirmed'}", flush=True)
    print(f"  secondary: errQ {errQ:.4f} vs F78 HW anchor 0.154, FakeMarrakesh 0.111", flush=True)

    out = {"experiment": "exp98_loader_depth_hardware", "phase": "qpu_finalize", "cycle": 6357,
           "author": "elder", "job_id": jid, "backend": rec.get("backend", BACKEND_NAME), "shots": SHOTS,
           "per_pub": per_pub, "grade": grade,
           "HW1_depth_boundary": {"errQ": errQ, "errI": errI, "gap": errQ - errI, "threshold": HW1_GAP, "pass": bool(hw1)},
           "HW2_shallow_clean": {"errI": errI, "abs_thresh": HW2_ABS, "plainI": plainI, "mult": HW2_MULT, "pass": bool(hw2)},
           "HW3_2q_mechanism": {"n2qQ": n2qQ, "n2qI": n2qI, "mult": HW3_MULT, "pass": bool(hw3)},
           "pred_c6357_001_confirmed": pred,
           "f78_hw_anchor": 0.154, "fakemarrakesh_anchor": 0.111}
    path = os.path.join(RESULTS_DIR, "exp98_qpu_results.json")
    with open(path, "w") as f: json.dump(out, f, indent=2)
    print(f"  saved -> {path}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--finalize", metavar="JID")
    a = ap.parse_args()
    if a.sim: run_sim()
    elif a.submit: run_submit()
    elif a.finalize: run_finalize(a.finalize)
    else: ap.print_help()
