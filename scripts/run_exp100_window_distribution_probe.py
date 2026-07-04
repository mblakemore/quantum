#!/usr/bin/env python3
"""
Exp100 — Calibration-window distribution probe (F81 follow-up, Elder C6378).

PURPOSE: F81 showed identical deep circuits on identical qubits swing blind-MLE err
0.154 -> 0.0003 across an 11h gap, and the published calibration data did NOT predict
it (predicts 3% k5-contrast difference, observed 3x). This probe accumulates cheap
(window_quality, time_since_calibration) samples to test the one residual hypothesis
and to measure the good-window base rate.

PROBE = 4 PUBs @ 4096 shots (~5-6 quantum-seconds):
    QQQ_k0  (deep 3q loader, plain read     — 7 2q gates)
    QQQ_k3  (mid amplification              — ~76 2q gates)
    QQQ_k5  (deep amplification             — 124 2q gates)
    IWM_k0  (shallow 1q sentinel/control    — 0 2q gates)
Qubits PINNED to [54,53,55] (virtual 0,1,2) / [0] to hold F78/F81's controlled variable.

WINDOW-QUALITY METRIC (pre-registered): R5 = |P_meas(k5)-0.5| / |P_ideal(k5)-0.5|,
clipped to [0,1.3]. Sign guard: if sign(P_meas-0.5) != sign(P_ideal-0.5), R5 := 0.
GOOD >= 0.8, BAD <= 0.5, else MID. Anchors: Exp98 R5=0.99 GOOD, Exp95 R5=0.33 BAD.

HYPOTHESIS H-TSC (pre-registered, experiments/100-window-distribution-probe-preregistration.md):
window quality declines with time since the last calibration update.
Grade at N>=8 probes with tsc spread >=3h: Spearman rho(tsc_minutes, R5).
SUPPORTED: rho <= -0.5 AND permutation p < 0.05. Else NULL/REFUTED per pre-reg.

USAGE:
  python3 run_exp100_window_distribution_probe.py --sim         # noiseless correctness gate
  python3 run_exp100_window_distribution_probe.py --submit      # submit one probe job
  python3 run_exp100_window_distribution_probe.py --pending     # finalize any DONE probes
  python3 run_exp100_window_distribution_probe.py --finalize JID
  python3 run_exp100_window_distribution_probe.py --analyze     # scatter + H-TSC grade when N allows
"""
import argparse
import json
import math
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from qae_qqq_tail_demo import (
    build_A as build_A_qqq, grover_Q as grover_Q_qqq, bucket_probs,
    true_tail_discrete, N_QUBITS as N_QQQ, SHOTS, SEED_TRANSP, BACKEND_NAME,
)
from run_exp96_loader_depth_boundary import build_A_iwm, grover_Q_iwm, A_TRUE_IWM

HERE = os.path.dirname(os.path.abspath(__file__))
JOBIDS = os.path.join(HERE, "..", "experiments", "exp100_probe_jobids.jsonl")
ROWS = os.path.join(HERE, "..", "results", "exp100_window_probes.jsonl")

PROBE_SPEC = [("QQQ", 0), ("QQQ", 3), ("QQQ", 5), ("IWM", 0)]
# virtual->physical pins reproducing Exp95/Exp98's layout ([54,53,55]; IWM on q0)
PIN_QQQ = [54, 53, 55]
PIN_IWM = [0]
EXPECTED_2Q = {("QQQ", 0): 10, ("QQQ", 3): 82, ("QQQ", 5): 130}  # pinned-layout values (anchors: 7/76/124, see pre-reg A1)

R5_GOOD, R5_BAD = 0.8, 0.5
H_TSC_RHO, H_TSC_P, H_TSC_MIN_N, H_TSC_MIN_SPREAD_MIN = -0.5, 0.05, 8, 180


def loaders():
    probs = bucket_probs()[0]
    A_qqq = build_A_qqq(probs, measure=False)
    Q_qqq, _ = grover_Q_qqq(probs)
    a_qqq = true_tail_discrete(probs)
    Q_iwm, A_iwm = grover_Q_iwm()
    return {"QQQ": (A_qqq, Q_qqq, N_QQQ, N_QQQ - 1, a_qqq),
            "IWM": (A_iwm, Q_iwm, 1, 0, A_TRUE_IWM)}


def build_circ(A, Q, nq, obj, k):
    qc = QuantumCircuit(nq, 1)
    qc.compose(A, list(range(nq)), inplace=True)
    for _ in range(k):
        qc.compose(Q, list(range(nq)), inplace=True)
    qc.measure(obj, 0)
    return qc


def ideal_P(a_true, k):
    th = math.asin(math.sqrt(a_true))
    return math.sin((2 * k + 1) * th) ** 2


def probe_circuits():
    L = loaders()
    out = []
    for ldr, k in PROBE_SPEC:
        A, Q, nq, obj, at = L[ldr]
        out.append((f"{ldr}_k{k}", ldr, k, build_circ(A, Q, nq, obj, k), at))
    return out


def r5_metric(p_meas, a_true):
    pi = ideal_P(a_true, 5)
    num, den = p_meas - 0.5, pi - 0.5
    if den == 0:
        return None
    if num * den < 0:
        return 0.0
    return max(0.0, min(1.3, abs(num) / abs(den)))


def run_sim():
    noiseless = AerSimulator()
    print("Exp100 SIM gate (noiseless correctness — measured must track ideal to shot noise)")
    ok = True
    for label, ldr, k, qc, at in probe_circuits():
        tq = transpile(qc, noiseless, seed_transpiler=SEED_TRANSP)
        res = noiseless.run(tq, shots=SHOTS).result()
        c = res.get_counts()
        p = c.get("1", 0) / SHOTS
        pi = ideal_P(at, k)
        d = abs(p - pi)
        se3 = 3 * math.sqrt(pi * (1 - pi) / SHOTS)
        flag = "PASS" if d <= max(se3, 0.02) else "FAIL"
        ok &= (flag == "PASS")
        print(f"  {label:8s} P={p:.4f} ideal={pi:.4f} |d|={d:.4f} (3se={se3:.4f}) {flag}")
    print("SIM GATE:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def run_submit():
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service()
    backend = svc.backend(BACKEND_NAME)
    print(f"Backend {backend.name} pending={backend.status().pending_jobs}", flush=True)
    pubs, meta = [], []
    for label, ldr, k, qc, at in probe_circuits():
        pin = PIN_QQQ if ldr == "QQQ" else PIN_IWM
        tq = transpile(qc, backend=backend, optimization_level=1,
                       seed_transpiler=SEED_TRANSP, initial_layout=pin)
        n2q = sum(1 for inst in tq.data if len(inst.qubits) == 2)
        exp = EXPECTED_2Q.get((ldr, k))
        tag = ""
        if exp is not None and n2q != exp:
            tag = f"  << WARNING expected {exp} (layout/routing drift — record, still comparable across probes)"
        print(f"  {label:8s} depth={tq.depth():4d} 2q={n2q}{tag}", flush=True)
        pubs.append(tq)
        meta.append({"label": label, "loader": ldr, "k": k, "n2q": n2q, "a_true": at})
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    job = sampler.run(pubs)
    rec = {"job_id": job.job_id(), "submitted_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "backend": BACKEND_NAME, "shots": SHOTS, "pubs": meta, "status": "submitted"}
    with open(JOBIDS, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"SUBMITTED probe job {job.job_id()} -> {os.path.relpath(JOBIDS, HERE)}")
    return 0


def _load_jobids():
    if not os.path.exists(JOBIDS):
        return []
    return [json.loads(l) for l in open(JOBIDS) if l.strip()]


def _finalized_ids():
    if not os.path.exists(ROWS):
        return set()
    return {json.loads(l)["job_id"] for l in open(ROWS) if l.strip()}


def run_finalize(jid):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    job = svc.job(jid)
    status = str(job.status())
    print(f"job {jid} status={status}")
    if "DONE" not in status.upper():
        return 3
    recs = {r["job_id"]: r for r in _load_jobids()}
    meta = recs.get(jid, {}).get("pubs")
    if meta is None:
        meta = [{"label": f"{l}_k{k}", "loader": l, "k": k,
                 "a_true": None} for l, k in PROBE_SPEC]
    res = job.result()
    mtr = job.metrics()
    exec_utc = mtr.get("timestamps", {}).get("running")
    L = loaders()
    row = {"job_id": jid, "backend": BACKEND_NAME, "shots": SHOTS,
           "executed_utc": exec_utc, "qsec": mtr.get("usage", {}).get("quantum_seconds"),
           "pubs": []}
    p_by = {}
    for i, m in enumerate(meta):
        bits = res[i].data.c.get_counts() if hasattr(res[i].data, "c") else res[i].data.meas.get_counts()
        p = bits.get("1", 0) / SHOTS
        at = m.get("a_true") or L[m["loader"]][4]
        row["pubs"].append({**m, "p": p, "ideal": ideal_P(at, m["k"])})
        p_by[(m["loader"], m["k"])] = (p, at)
        print(f"  {m['label']:8s} P={p:.4f} ideal={ideal_P(at, m['k']):.4f}")
    pq5, atq = p_by[("QQQ", 5)]
    r5 = r5_metric(pq5, atq)
    pq0, _ = p_by[("QQQ", 0)]
    piw, ati = p_by[("IWM", 0)]
    row["R5"] = r5
    row["k0_err"] = abs(pq0 - atq)
    row["iwm_err"] = abs(piw - ati)
    row["window_class"] = "GOOD" if r5 >= R5_GOOD else ("BAD" if r5 <= R5_BAD else "MID")
    # time since calibration at execution
    try:
        be = svc.backend(BACKEND_NAME)
        dt = datetime.datetime.fromisoformat(exec_utc.replace("Z", "+00:00"))
        props = be.properties(datetime=dt)
        cal = props.last_update_date
        row["calibration_last_update"] = cal.isoformat()
        row["tsc_minutes"] = round((dt - cal).total_seconds() / 60.0, 1)
    except Exception as e:
        row["calibration_last_update"] = None
        row["tsc_minutes"] = None
        row["tsc_error"] = f"{type(e).__name__}: {e}"
    os.makedirs(os.path.dirname(ROWS), exist_ok=True)
    with open(ROWS, "a") as f:
        f.write(json.dumps(row) + "\n")
    print(f"ROW: R5={r5:.3f} class={row['window_class']} tsc={row['tsc_minutes']}min "
          f"k0_err={row['k0_err']:.4f} iwm_err={row['iwm_err']:.4f} -> {os.path.relpath(ROWS, HERE)}")
    return 0


def run_pending():
    done = _finalized_ids()
    rc = 0
    todo = [r for r in _load_jobids() if r["job_id"] not in done]
    if not todo:
        print("No unfinalized probe jobs.")
        return 0
    for r in todo:
        rc = max(rc, run_finalize(r["job_id"]))
    return rc


def _spearman_perm(xs, ys, n_perm=20000, seed=100):
    import random
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for t in range(i, j + 1):
                rk[order[t]] = avg
            i = j + 1
        return rk

    def rho(a, b):
        ra, rb = rank(a), rank(b)
        ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
        num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
        da = math.sqrt(sum((x - ma) ** 2 for x in ra))
        db = math.sqrt(sum((y - mb) ** 2 for y in rb))
        return num / (da * db) if da * db else 0.0

    obs = rho(xs, ys)
    rnd = random.Random(seed)
    ys2 = list(ys)
    hits = 0
    for _ in range(n_perm):
        rnd.shuffle(ys2)
        if rho(xs, ys2) <= obs:  # one-sided: H-TSC predicts NEGATIVE rho
            hits += 1
    return obs, hits / n_perm


def run_analyze():
    rows = [json.loads(l) for l in open(ROWS)] if os.path.exists(ROWS) else []
    # seed anchors from F78/F81 (pre-registered as includable: same circuits/qubits/backend)
    anchors = [
        {"job_id": "d93s1fkql68s73c8oong", "R5": 0.33, "tsc_minutes": 79.0, "window_class": "BAD", "anchor": "Exp95/F78"},
        {"job_id": "d93vso6vtlqs73ftmqhg", "R5": 0.99, "tsc_minutes": 38.0, "window_class": "GOOD", "anchor": "Exp98/F81"},
    ]
    seen = {r["job_id"] for r in rows}
    all_rows = rows + [a for a in anchors if a["job_id"] not in seen]
    usable = [r for r in all_rows if r.get("tsc_minutes") is not None and r.get("R5") is not None]
    usable.sort(key=lambda r: r["tsc_minutes"])
    print(f"Exp100 window-distribution probes: N={len(usable)} usable "
          f"({len(rows)} probe rows + {len(all_rows)-len(rows)} F78/F81 anchors)")
    for r in usable:
        src = r.get("anchor", "probe")
        print(f"  tsc={r['tsc_minutes']:7.1f}min R5={r['R5']:.3f} {r['window_class']:4s} [{src}] {r['job_id']}")
    good = sum(1 for r in usable if r["window_class"] == "GOOD")
    print(f"good-window base rate so far: {good}/{len(usable)}")
    xs = [r["tsc_minutes"] for r in usable]
    ys = [r["R5"] for r in usable]
    spread_ok = (max(xs) - min(xs)) >= H_TSC_MIN_SPREAD_MIN if xs else False
    if len(usable) >= H_TSC_MIN_N and spread_ok:
        obs, p = _spearman_perm(xs, ys)
        verdict = "SUPPORTED" if (obs <= H_TSC_RHO and p < H_TSC_P) else "NULL"
        print(f"H-TSC GRADE (pre-registered): rho={obs:.3f} perm_p={p:.4f} -> {verdict}")
    else:
        print(f"H-TSC: not gradeable yet (need N>={H_TSC_MIN_N} and tsc spread >={H_TSC_MIN_SPREAD_MIN}min; "
              f"have N={len(usable)}, spread={max(xs)-min(xs):.0f}min)" if xs else "H-TSC: no data")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--finalize", metavar="JID")
    ap.add_argument("--pending", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.sim:
        sys.exit(run_sim())
    if a.submit:
        sys.exit(run_submit())
    if a.finalize:
        sys.exit(run_finalize(a.finalize))
    if a.pending:
        sys.exit(run_pending())
    if a.analyze:
        sys.exit(run_analyze())
    ap.print_help()
