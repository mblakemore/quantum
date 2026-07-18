#!/usr/bin/env python3
"""Exp179 — THE MERGED WINDOW: window-count as architecture + engineered Hahn. C4866.
With Pauli-frame tracking the 2nd swap's gates never wait on the 1st swap's outcomes, so both
Bell-basis rotations can run first and ALL FOUR middle measurements merge into ONE simultaneous
window (2 -> 1 windows; middles never idle through a window). The single window is then echoed
with an ENGINEERED Hahn: X(ends) -> delay(~measure duration) -> X(ends) after the window, so the
ends' window phase cancels against the matched delay (coherence proven by Exp178).
Arms (all frame-tracked): seq (Exp177 deferred replica) | seqecho (Exp178 defecho replica) |
merged | mergedecho | direct. Frame algebra unchanged: x=c3^c1, z=c2^c0 on D.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import fidelity

ARMS = ("seq", "seqecho", "merged", "mergedecho", "direct")
SETTINGS = ("ZZ", "XX", "YY")
WITNESS = 0.5


def _verify_rot(qc, setting, qubits):
    for q in qubits:
        if setting == "XX": qc.h(q)
        elif setting == "YY": qc.sdg(q); qc.h(q)


def chain_circuit(arm, setting, delay_dt=0):
    """A=q0,B1=q1,B2=q2,C1=q3,C2=q4,D=q5. c0,c1 stage1; c2,c3 stage2; c4=A, c5=D.
    delay_dt: engineered-Hahn delay for mergedecho (in dt units; 0 in selftest)."""
    qc = QuantumCircuit(6, 6)
    if arm == "direct":
        qc.h(0); qc.cx(0, 1)
        _verify_rot(qc, setting, (0, 1))
        qc.measure(0, 4); qc.measure(1, 5)
        return qc
    qc.h(0); qc.cx(0, 1)          # Bell(A,B1)
    qc.h(2); qc.cx(2, 3)          # Bell(B2,C1)
    qc.h(4); qc.cx(4, 5)          # Bell(C2,D)
    qc.barrier()
    if arm in ("seq", "seqecho"):
        qc.cx(1, 2); qc.h(1)                       # stage-1 window
        qc.measure(1, 0); qc.measure(2, 1)
        if arm == "seqecho":
            qc.barrier()
            qc.x(0); qc.x(5)                       # Exp178 midpoint echo
        qc.barrier()
        qc.cx(3, 4); qc.h(3)                       # stage-2 window
        qc.measure(3, 2); qc.measure(4, 3)
    else:  # merged / mergedecho — both rotations first, ONE simultaneous window
        qc.cx(1, 2); qc.h(1)
        qc.cx(3, 4); qc.h(3)
        qc.barrier()
        qc.measure(1, 0); qc.measure(2, 1)         # the single merged window
        qc.measure(3, 2); qc.measure(4, 3)
        if arm == "mergedecho":
            qc.barrier()
            qc.x(0); qc.x(5)                       # engineered Hahn: X - delay(~w) - X
            if delay_dt > 0:
                qc.append(Delay(delay_dt, unit="dt"), [0]); qc.append(Delay(delay_dt, unit="dt"), [5])
            qc.x(0); qc.x(5)
    qc.barrier()
    _verify_rot(qc, setting, (0, 5))
    qc.measure(0, 4); qc.measure(5, 5)
    return qc


def _parity(counts, shots, setting):
    """<A D> from c4,c5 with per-shot Pauli-frame correction (all chain arms are frame-tracked)."""
    acc = 0
    for b, n in counts.items():
        b = b.replace(" ", "")
        a = int(b[-5]); d = int(b[-6])
        c0, c1, c2, c3 = int(b[-1]), int(b[-2]), int(b[-3]), int(b[-4])
        if setting == "ZZ": d ^= c3 ^ c1
        elif setting == "XX": d ^= c2 ^ c0
        else: d ^= c0 ^ c1 ^ c2 ^ c3
        acc += (1 - 2 * a) * (1 - 2 * d) * n
    return acc / shots


def _parity_direct(counts, shots):
    acc = 0
    for b, n in counts.items():
        b = b.replace(" ", "")
        acc += (1 - 2 * int(b[-5])) * (1 - 2 * int(b[-6])) * n
    return acc / shots


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        if arm == "direct":
            par = {s: _parity_direct(get(arm, s), shots) for s in SETTINGS}
        else:
            par = {s: _parity(get(arm, s), shots, s) for s in SETTINGS}
        out[arm] = {"F": float(fidelity(par)), **{k: float(v) for k, v in par.items()}}
    return out


def verdicts(r, shots):
    se_F = 0.75 / np.sqrt(shots); se_d = float(np.sqrt(2) * se_F)
    d_arch = r["merged"]["F"] - r["seq"]["F"]
    d_stack = r["mergedecho"]["F"] - r["seqecho"]["F"]
    d_hahn = r["mergedecho"]["F"] - r["merged"]["F"]
    d_mid = r["merged"]["F"] - r["seqecho"]["F"]
    return {"arch_gain": float(d_arch), "arch_sigma": float(d_arch / se_d),
            "stack_gain": float(d_stack), "stack_sigma": float(d_stack / se_d),
            "hahn_gain": float(d_hahn), "hahn_sigma": float(d_hahn / se_d),
            "merged_vs_seqecho": float(d_mid), "merged_vs_seqecho_sigma": float(d_mid / se_d),
            "se_delta": se_d}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, s):
        if (arm, s) not in cache:
            cache[(arm, s)] = sim.run(chain_circuit(arm, s), shots=shots).result().get_counts()
        return cache[(arm, s)]
    r = analyze(get, shots)
    print("Exp179 selftest (noiseless Aer)")
    for arm in ARMS:
        print(f"  {arm:>10}: ZZ={r[arm]['ZZ']:+.2f} XX={r[arm]['XX']:+.2f} YY={r[arm]['YY']:+.2f} "
              f"-> F={r[arm]['F']:.3f}")
        assert r[arm]["F"] > 0.99, f"{arm} must be exact (merged-window equivalence + frame + echo identities)"
    print("SELFTEST PASS: merging both Bell measurements into one window is statistically exact "
          "(deferred-measurement principle), frame algebra unchanged, echo identities hold. Cleared to fly.")


def _measure_delay_dt(backend):
    """Engineered-Hahn delay ~ one measurement duration, granularity-rounded, in dt."""
    try:
        dur_s = max(p.duration for (q,), p in backend.target["measure"].items()
                    if p is not None and p.duration)
        dt = backend.dt or 5e-10
        g = getattr(backend.target, "granularity", 16) or 16
        ddt = int(round(dur_s / dt / g)) * g
        return max(ddt, g)
    except Exception as e:
        print(f"  (measure-duration query failed: {e}; falling back to 2800 dt)")
        return 2800


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    delay_dt = _measure_delay_dt(backend)
    print(f"engineered-Hahn delay: {delay_dt} dt (~{delay_dt * (backend.dt or 5e-10) * 1e6:.2f} us)")
    circuits, order = [], []
    for arm in ARMS:
        for s in SETTINGS:
            circuits.append(transpile(chain_circuit(arm, s, delay_dt), backend=backend,
                                      optimization_level=3))
            order.append([arm, s])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 179, "slug": "merged_window", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "delay_dt": int(delay_dt),
                "prereg": {"primary": "F(merged)-F(seq) > 0 at >=3 sigma (window-count architecture pays)",
                           "secondary": "F(mergedecho)-F(seqecho) > 0 at >=3 sigma (new best stack)",
                           "band": "seq 0.50-0.62; seqecho 0.70-0.82; merged 0.68-0.82; "
                                   "mergedecho 0.75-0.88; direct 0.95-0.99; ceiling ref 0.885",
                           "open": "merged vs seqecho pre-registered as genuinely open (locates residual: middles vs ends)",
                           "risk": "if mergedecho ~ merged, suspect delay placement first (Exp178 proved coherence)"}}
    out = os.path.join(HERE, "..", "results", "exp179_merged_window_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp179_merged_window_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, s)], shots)
    v = verdicts(r, shots)
    print(f"Exp179 MERGED WINDOW decode | job {man['job_id']} | backend {man['backend']} | "
          f"hahn delay {man['delay_dt']} dt")
    for arm in ARMS:
        print(f"  {arm:>10}: ZZ={r[arm]['ZZ']:+.3f} XX={r[arm]['XX']:+.3f} YY={r[arm]['YY']:+.3f} "
              f"-> F = {r[arm]['F']:.3f}")
    print(f"\nARCHITECTURE (merged - seq):        {v['arch_gain']:+.3f} ({v['arch_sigma']:+.1f} sigma)")
    print(f"NEW STACK (mergedecho - seqecho):   {v['stack_gain']:+.3f} ({v['stack_sigma']:+.1f} sigma)")
    print(f"ENGINEERED HAHN (mergedecho-merged): {v['hahn_gain']:+.3f} ({v['hahn_sigma']:+.1f} sigma)")
    print(f"RESIDUAL LOCATOR (merged - seqecho): {v['merged_vs_seqecho']:+.3f} "
          f"({v['merged_vs_seqecho_sigma']:+.1f} sigma) [pre-registered open]")
    print(f"CEILING: Exp177 endmeasure 0.885 | best tonight: "
          f"{max(ARMS[:-1], key=lambda a: r[a]['F'])} {max(r[a]['F'] for a in ARMS[:-1]):.3f}")
    p_ok = v["arch_gain"] > 0 and v["arch_sigma"] >= 3
    s_ok = v["stack_gain"] > 0 and v["stack_sigma"] >= 3
    print(f"PRIMARY: {'HELD — merging the windows pays' if p_ok else 'NOT HELD (honest accounting above)'}")
    print(f"SECONDARY: {'HELD — new best stack' if s_ok else 'NOT HELD'}")
    out = {"job_id": man["job_id"], "results": r, "verdicts": v,
           "primary_ok": bool(p_ok), "secondary_ok": bool(s_ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp179_merged_window_decode.json"), "w"), indent=1)
    print("-> results/exp179_merged_window_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
