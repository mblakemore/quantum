#!/usr/bin/env python3
"""
Exp94b — F74 HARDWARE arm: DISC(phi)=2*cos(phi/2) on a real IBM backend (Ember, C4069).

Hardware confirmation of the F74 continuous-resource law (sim-validated Exp94/C4066).
Reuses build_arm() VERBATIM from experiments/exp94_dephasing_dose_response_sim.py, so the
hardware measures exactly the circuit the sim modeled. Pre-reg: experiments/exp94b-hw-preregistration.md

10 PUBs (5 phi x {commute(X,X), anticommute(X,Z)}), ONE job, ONE window.
Backend default ibm_kingston (least-busy; NOT fez/marrakesh where Exp91 queues -> no collision).

Usage:
  python3 run_exp94_hw.py --scan               # FREE: build+transpile all 10, report depth/2q, no QPU
  python3 run_exp94_hw.py --submit             # QPU: one 10-PUB job on ibm_kingston
  python3 run_exp94_hw.py --grade              # grade (same cycle if done, else next)
"""
import sys, os, math, json, time, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RESULTS_DIR = os.path.join(HERE, "..", "results")
JOBID_PATH = os.path.join(RESULTS_DIR, "exp94_hw_jobids.json")

from qiskit import QuantumCircuit, transpile

PHIS = [0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi]
PHI_LABELS = ["0", "pi/4", "pi/2", "3pi/4", "pi"]
PAIRS = [("commute", "X", "X"), ("anticommute", "X", "Z")]  # DISC = commute - anticommute


# ---- circuit (verbatim from exp94 sim) --------------------------------------
def apply_ctrl_gate(qc, gate, ctrl, tgt, ctrl_state):
    if ctrl_state == 0:
        qc.x(ctrl)
    if gate == "X":
        qc.cx(ctrl, tgt)
    elif gate == "Z":
        qc.cz(ctrl, tgt)
    elif gate == "Y":
        qc.cy(ctrl, tgt)
    else:
        raise ValueError(gate)
    if ctrl_state == 0:
        qc.x(ctrl)


def build_arm(A, B, phi):
    qc = QuantumCircuit(3, 1)
    qc.h(0)
    apply_ctrl_gate(qc, A, 0, 1, 0)
    apply_ctrl_gate(qc, B, 0, 1, 1)
    qc.barrier()
    apply_ctrl_gate(qc, B, 0, 1, 0)
    apply_ctrl_gate(qc, A, 0, 1, 1)
    qc.barrier()
    qc.cry(phi, 0, 2)      # partial Z-dephasing of control; ancilla q2 traced out
    qc.h(0)                # X-basis readout on control
    qc.measure(0, 0)
    return qc


def exp_x_control(counts):
    p0 = p1 = 0
    for bitstr, n in counts.items():
        b = bitstr.replace(" ", "")[-1]
        if b == "0":
            p0 += n
        else:
            p1 += n
    tot = p0 + p1
    return (p0 - p1) / tot if tot else 0.0


def _meta():
    m = []
    for phi, lab in zip(PHIS, PHI_LABELS):
        for name, A, B in PAIRS:
            m.append({"phi": phi, "phi_label": lab, "arm": name, "A": A, "B": B})
    return m


def _build_pubs(backend):
    """Build + transpile the 10 circuits to the backend. Returns (pubs, meta, ok)."""
    pubs, meta = [], _meta()
    depths, twoqs = [], []
    for phi, lab in zip(PHIS, PHI_LABELS):
        for name, A, B in PAIRS:
            qc = build_arm(A, B, phi)
            tqc = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=42)
            ops = tqc.count_ops()
            tq = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
            depths.append(tqc.depth())
            twoqs.append(tq)
            pubs.append(tqc)
    for mrow, d, t in zip(meta, depths, twoqs):
        mrow["depth"] = d
        mrow["twoq"] = t
    ok = len(pubs) == 10
    return pubs, meta, ok


# ---- modes ------------------------------------------------------------------
def scan(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)
    pubs, meta, ok = _build_pubs(backend)
    for m in meta:
        print(f"  phi={m['phi_label']:5s} {m['arm']:12s} depth={m['depth']:3d} 2q={m['twoq']}", flush=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp94_hw_scan.json"), "w") as f:
        json.dump({"backend": backend_name, "meta": meta, "n_pubs": len(pubs)}, f, indent=2)
    print(f"\nSaved results/exp94_hw_scan.json | {len(pubs)} PUBs | "
          f"{'READY for --submit' if ok else 'ABORT'}", flush=True)
    return ok


def submit(backend_name, shots=2000):
    from qiskit_ibm_runtime import SamplerV2
    from run_exp66_qpu_partb import _get_ibm_service
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)
    pubs, meta, ok = _build_pubs(backend)
    if not ok:
        print("\nABORT: build/verify failed; not spending QPU.", flush=True)
        return None
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = shots
    job = sampler.run(pubs)
    jid = job.job_id()
    print(f"\nSubmitted ONE job with {len(pubs)} PUBs -> job_id={jid}", flush=True)
    manifest = {"experiment": "exp94b-f74-hardware", "author": "Ember", "cycle": "C4069",
                "backend": backend_name, "shots": shots, "job_id": jid, "pub_meta": meta,
                "law_tested": "DISC(phi)=2*cos(phi/2)",
                "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(JOBID_PATH, "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"Manifest saved: {JOBID_PATH} (grade this cycle if done, else next)", flush=True)
    return manifest


def _spearman(xs, ys):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, i in enumerate(s):
            r[i] = pos
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1 - 6 * d2 / (n * (n * n - 1))


def _pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    vy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (vx * vy) if vx > 0 and vy > 0 else 0.0


def grade():
    from run_exp66_qpu_partb import _get_ibm_service
    with open(JOBID_PATH) as fh:
        man = json.load(fh)
    service = _get_ibm_service()
    job = service.job(man["job_id"])
    st = job.status()
    print(f"Job {man['job_id']} status={st}", flush=True)
    if str(st) not in ("DONE", "JobStatus.DONE"):
        print("Not DONE yet — grade next cycle.", flush=True)
        return None
    res = job.result()
    meta = man["pub_meta"]
    # recover <X_c> per PUB
    xc = []
    for i, m in enumerate(meta):
        counts = res[i].data.c.get_counts() if hasattr(res[i].data, "c") else \
            list(res[i].data.__dict__.values())[0].get_counts()
        xc.append(exp_x_control(counts))
    rows = []
    for k, (phi, lab) in enumerate(zip(PHIS, PHI_LABELS)):
        com = xc[2 * k]      # commute
        anti = xc[2 * k + 1]  # anticommute
        disc = com - anti
        pred = 2 * math.cos(phi / 2)
        rows.append({"phi": phi, "label": lab, "xc_commute": com, "xc_anti": anti,
                     "disc_hw": disc, "pred_2cos": pred, "resid": disc - pred})
        print(f"  phi={lab:5s} DISC_hw={disc:+.4f} pred={pred:+.4f} resid={disc-pred:+.4f}", flush=True)
    disc_hw = [r["disc_hw"] for r in rows]
    preds = [r["pred_2cos"] for r in rows]
    h1 = (disc_hw[0] >= 1.20) and (abs(disc_hw[-1]) <= 0.40)
    spear = _spearman(list(range(len(PHIS))), disc_hw)
    h2 = spear <= -0.90
    pear = _pearson(disc_hw, preds)
    h3 = pear >= 0.95
    if h3 and h2:
        branch = "A_CONFIRMED"
    elif pear >= 0.85:
        branch = "B_SHAPE_PARTIAL"
    else:
        branch = "C_REFUTED"
    print("\nPRE-REG GATE CHECK", flush=True)
    print(f"  HW-H1 endpoints DISC(0)>=1.20 & |DISC(pi)|<=0.40 : {disc_hw[0]:+.3f}/{disc_hw[-1]:+.3f} -> {'PASS' if h1 else 'FAIL'}")
    print(f"  HW-H2 spearman(phi,DISC)<=-0.90                  : {spear:+.3f} -> {'PASS' if h2 else 'FAIL'}")
    print(f"  HW-H3 pearson(DISC_hw,2cos)>=0.95 (PRIMARY)      : {pear:+.4f} -> {'PASS' if h3 else 'FAIL'}")
    print(f"\nBRANCH: {branch}", flush=True)
    out = {"experiment": "exp94b-f74-hardware", "author": "Ember", "cycle_submitted": man.get("cycle"),
           "backend": man["backend"], "job_id": man["job_id"], "rows": rows,
           "HW_H1": bool(h1), "HW_H2_spearman": spear, "HW_H3_pearson": pear,
           "branch": branch}
    with open(os.path.join(RESULTS_DIR, "exp94_hw_graded.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("wrote results/exp94_hw_graded.json", flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("--backend", default="ibm_kingston")
    ap.add_argument("--shots", type=int, default=2000)
    a = ap.parse_args()
    if a.scan:
        scan(a.backend)
    elif a.submit:
        submit(a.backend, a.shots)
    elif a.grade:
        grade()
    else:
        ap.print_help()
