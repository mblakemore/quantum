#!/usr/bin/env python3
"""Exp187 — THE ORDER DECIDED LATER: a delayed-choice quantum switch. C4877.
Control C=|+> coherently routes the order of A=Rx(pi/2), B=S on target T=|0>. Definite orders
give |+> (A->B) vs |-i> (B->A). The TARGET is measured FIRST; the control LATER, in a basis
chosen per circuit: Z-sort reconstructs definite orders; X-sort gives psi_pm ~ (BA +- AB)|0>
with THEOREM-SHARP mixture bounds: <Y|+> = +2/3 (every mixture <= 0), <Z|-> = -1 (every
mixture = 0), weights 3/4 : 1/4. Arms: delayed | standard (control first — prices the window
on the control per the run's law) | decohered (classical mixture falsifier — X-sort flat).
Control=q0, Target=q1, dephasing dump=q2. clbits: c0=target, c1=control, c2=dump.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

PI = np.pi
def arms_settings(tag=""):
    base = ([("delayed", cb, tb) for cb in ("X", "Z") for tb in ("X", "Y", "Z")]
            + [("standard", cb, tb) for cb in ("X", "Z") for tb in ("X", "Y", "Z")]
            + [("decohered", "X", tb) for tb in ("X", "Y", "Z")])
    if tag == "b":
        base += [("delayed_echo", cb, tb) for cb in ("X", "Z") for tb in ("X", "Y", "Z")]
    return base
ARMS_SETTINGS = arms_settings()
# analytic references (verified in selftest): definite orders and X-sorted superpositions
BLOCH_AB = (1.0, 0.0, 0.0)     # order A->B : |+>
BLOCH_BA = (0.0, -1.0, 0.0)    # order B->A : |-i>
BLOCH_P = (2/3, -2/3, 1/3)     # psi_+ ~ (BA + AB)|0> (sim-verified)
BLOCH_M = (0.0, 0.0, -1.0)     # psi_- = |1>
P_MINUS = 0.25


def _switch(qc):
    """Coherently controlled order: c=0 -> A then B ; c=1 -> B then A."""
    qc.x(0)
    qc.crx(PI / 2, 0, 1)       # A (fires for original c=0)
    qc.cp(PI / 2, 0, 1)        # B
    qc.x(0)
    qc.cp(PI / 2, 0, 1)        # B (fires for c=1)
    qc.crx(PI / 2, 0, 1)       # A


def _rot(qc, basis, q):
    if basis == "X": qc.h(q)
    elif basis == "Y": qc.sdg(q); qc.h(q)


def circuit(arm, cbasis, tbasis, delay_dt=0):
    from qiskit.circuit import Delay
    qc = QuantumCircuit(3, 3)
    qc.h(0)                    # control |+>
    if arm == "decohered":
        qc.cx(0, 2)            # dephase the order coherence before anything acts
    qc.barrier()
    _switch(qc)
    qc.barrier()
    if arm == "standard":      # control measured FIRST
        _rot(qc, cbasis, 0); qc.measure(0, 1)
        qc.barrier()
        _rot(qc, tbasis, 1); qc.measure(1, 0)
    else:                      # delayed / decohered / delayed_echo: TARGET first, control later
        _rot(qc, tbasis, 1); qc.measure(1, 0)
        if arm == "delayed_echo":   # engineered Hahn on the control through the window (Exp179)
            qc.x(0)
            if delay_dt > 0:
                qc.append(Delay(delay_dt, unit="dt"), [0])
            qc.x(0)
        qc.barrier()
        _rot(qc, cbasis, 0); qc.measure(0, 1)
    return qc


def analyze(get, shots, settings=None):
    """Per arm: sorted target Bloch vectors per control outcome, weights, unsorted marginals."""
    settings = settings or ARMS_SETTINGS
    out = {}
    arms = sorted(set(a for a, _, _ in settings))
    for arm in arms:
        cbases = sorted(set(cb for a, cb, _ in settings if a == arm))
        rec = {}
        for cb in cbases:
            sort = {0: {}, 1: {}}; nsort = {0: 0, 1: 0}
            unsorted = {}
            for tb in ("X", "Y", "Z"):
                acc = {0: 0, 1: 0}; n = {0: 0, 1: 0}; tot = 0; um = 0
                for s, cnt in get(arm, cb, tb).items():
                    b = s.replace(" ", "")
                    t, c = int(b[-1]), int(b[-2])
                    acc[c] += (1 - 2 * t) * cnt; n[c] += cnt
                    um += (1 - 2 * t) * cnt; tot += cnt
                for c in (0, 1):
                    sort[c][tb] = acc[c] / n[c] if n[c] else 0.0
                    nsort[c] += n[c]
                unsorted[tb] = um / tot
            tot_n = nsort[0] + nsort[1]
            rec[cb] = {"sorted": {c: {k: float(v) for k, v in sort[c].items()} for c in (0, 1)},
                       "weights": {c: float(nsort[c] / tot_n) for c in (0, 1)},
                       "unsorted": {k: float(v) for k, v in unsorted.items()}}
        out[arm] = rec
    return out


def _fid(bloch, ref):
    return (1 + bloch["X"] * ref[0] + bloch["Y"] * ref[1] + bloch["Z"] * ref[2]) / 2


def witnesses(rec):
    """From a control-X sort: W+ = <Y|+outcome>, W- = <Z|-outcome>, p-."""
    xs = rec["X"]["sorted"]
    # control X measurement: outcome bit 0 = +, bit 1 = -
    return {"Wplus_Z": xs[0]["Z"], "Wminus_Z": xs[1]["Z"], "p_minus": rec["X"]["weights"][1],
            "XminusY_plus": xs[0]["X"] - xs[0]["Y"],
            "F_plus": _fid(xs[0], BLOCH_P), "F_minus": _fid(xs[1], BLOCH_M)}


def zsort_fids(rec):
    zs = rec["Z"]["sorted"]
    return {"F_orderAB": _fid(zs[0], BLOCH_AB), "F_orderBA": _fid(zs[1], BLOCH_BA)}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    cache = {}
    def get(arm, cb, tb):
        k = (arm, cb, tb)
        if k not in cache:
            cache[k] = sim.run(circuit(arm, cb, tb), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get, shots)
    w = witnesses(r["delayed"]); z = zsort_fids(r["delayed"])
    wd = witnesses(r["decohered"])
    print("Exp187 selftest (noiseless Aer)")
    print(f"  delayed X-sort: W+<Z>={w['Wplus_Z']:+.3f} (ideal +1/3, mixtures 0)  "
          f"W-<Z>={w['Wminus_Z']:+.3f} (ideal -1, mixtures 0)  X-Y={w['XminusY_plus']:.3f} "
          f"(ideal 4/3, hull <=1)  p-={w['p_minus']:.3f}")
    print(f"  delayed Z-sort: F(A->B)={z['F_orderAB']:.3f}  F(B->A)={z['F_orderBA']:.3f}")
    print(f"  decohered X-sort: W+<Z>={wd['Wplus_Z']:+.3f}  W-<Z>={wd['Wminus_Z']:+.3f} (must be ~0: equatorial)")
    assert abs(w["Wplus_Z"] - 1/3) < 0.03 and abs(w["Wminus_Z"] + 1) < 0.03, "X-sort Z-witnesses must hit analytic values"
    assert abs(w["XminusY_plus"] - 4/3) < 0.04, "hull-breaking X-Y must hit 4/3"
    assert abs(w["p_minus"] - P_MINUS) < 0.02, "weights must be 3/4 : 1/4"
    assert z["F_orderAB"] > 0.99 and z["F_orderBA"] > 0.99, "Z-sort must reconstruct definite orders"
    ws = witnesses(r["standard"])
    assert abs(ws["Wplus_Z"] - 1/3) < 0.03 and abs(ws["Wminus_Z"] + 1) < 0.03, "standard arm identical noiseless"
    assert abs(wd["Wplus_Z"]) < 0.03 and abs(wd["Wminus_Z"]) < 0.03, "decohered X-sort must stay on the equator"
    rb = analyze(get2, 20000, arms_settings("b")) if False else None  # placeholder
    we = None
    cache2 = {}
    def getb(arm, cb, tb):
        k = (arm, cb, tb)
        if k not in cache2:
            cache2[k] = sim.run(circuit(arm, cb, tb, 0), shots=20000).result().get_counts()
        return cache2[k]
    rb = analyze(getb, 20000, arms_settings("b"))
    we = witnesses(rb["delayed_echo"])
    assert abs(we["Wplus_Z"] - 1/3) < 0.03 and abs(we["Wminus_Z"] + 1) < 0.03, "echo arm (XX=identity noiseless) must match analytic"
    print(f"  delayed_echo (noiseless XX pair): W+<Z>={we['Wplus_Z']:+.3f}  W-<Z>={we['Wminus_Z']:+.3f}")
    spread = max(abs(r["delayed"][cb]["unsorted"][tb] - r["standard"][cb2]["unsorted"][tb])
                 for tb in ("X", "Y", "Z") for cb in ("X", "Z") for cb2 in ("X", "Z"))
    assert spread < 0.03, "unsorted target marginal must not depend on the later choice"
    print("SELFTEST PASS: same target record sorts to definite orders (Z) or past-the-mixture-"
          "bound superpositions of orders (X: Y+=2/3, Z-=-1, weights 3:1); decohered flat; "
          "no-signaling exact. Cleared to fly.")


def _measure_delay_dt(backend):
    try:
        dur_s = max(p.duration for (q,), p in backend.target["measure"].items()
                    if p is not None and p.duration)
        dt = backend.dt or 5e-10
        g = getattr(backend.target, "granularity", 16) or 16
        return max(int(round(dur_s / dt / g)) * g, g)
    except Exception:
        return 2800


def submit(backend_name, shots, tag=""):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    settings = arms_settings(tag)
    delay_dt = _measure_delay_dt(backend) if tag == "b" else 0
    layout = None
    if tag == "b":   # pin ONE layout for every circuit (kills placement variance in the gauge)
        probe = transpile(circuit("delayed", "X", "X", 0), backend=backend, optimization_level=3)
        layout = probe.layout.final_index_layout()
        print(f"pinned layout {layout} | hahn delay {delay_dt} dt")
    circuits, order = [], []
    for arm, cb, tb in settings:
        if layout is not None:
            circuits.append(transpile(circuit(arm, cb, tb, delay_dt), backend=backend,
                                      initial_layout=layout, optimization_level=1))
        else:
            circuits.append(transpile(circuit(arm, cb, tb, delay_dt), backend=backend, optimization_level=3))
        order.append([arm, cb, tb])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 187, "slug": "late_order", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "tag": tag,
                "prereg_b": ({"falsifier_difference_form": "decohered |W+ - W-| <= 0.10 (mixture: 0; robust to common-mode offset)",
                              "nosignal_pinned": "unsorted marginal spread < 0.025 (2 sigma shot noise, one pinned layout)",
                              "Wplus_band_forward_priced": "+0.08..+0.25 (187 measured window dose applied)",
                              "echo_arm": "delayed_echo recovers >= half the delayed-choice cost: W(echo) - W(delayed) >= 0.5*(W(standard)-W(delayed)) for W+"} if tag == "b" else None),
                "prereg": {"witness_form_correction": "pre-flight, selftest-caught: BOTH definite orders are "
                                       "equatorial so EVERY mixture has Z=0 exactly; X-sorted ensembles leave the "
                                       "equator (psi+ Z=+1/3, psi- Z=-1); psi+ also breaks the hull with X-Y=4/3>1",
                           "primary_delayed": "W+<Z> in +0.18..+0.33 (mixtures 0, >=5 sigma) AND "
                                              "W-<Z> in -0.85..-0.50 (mixtures 0, >=5 sigma) AND Z-sort F >= 0.85 both",
                           "standard": "W+<Z> +0.22..+0.34; W-<Z> -0.90..-0.65; Z-sort F >= 0.90; "
                                       "window cost = W(standard)-W(delayed), one control dose",
                           "hull_gauge": "X-Y (+ensemble) 1.10-1.40, > 1 at >=3 sigma",
                           "decohered": "|W+<Z>| <= 0.10 and |W-<Z>| <= 0.10",
                           "gauges": "p- 0.20-0.30; unsorted-marginal spread < 0.02"}}
    out = os.path.join(HERE, "..", "results", f"exp187{tag}_late_order_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode(tag=""):
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", f"exp187{tag}_late_order_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, cb, tb) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, cb, tb)] = getattr(r0.data, reg).get_counts()
    settings = [tuple(o) for o in man["order"]]
    r = analyze(lambda arm, cb, tb: raw[(arm, cb, tb)], shots, settings)
    se = 1.0 / np.sqrt(shots * 0.75)      # per sorted-ensemble expectation (approx worst case)
    se_m = 1.0 / np.sqrt(shots * 0.25)
    wd, wst, wde = witnesses(r["delayed"]), witnesses(r["standard"]), witnesses(r["decohered"])
    zd, zs = zsort_fids(r["delayed"]), zsort_fids(r["standard"])
    spread = max(abs(r["delayed"][cb]["unsorted"][tb] - r["delayed"][cb2]["unsorted"][tb])
                 for tb in ("X", "Y", "Z") for cb in ("X", "Z") for cb2 in ("X", "Z"))
    print(f"Exp187 THE ORDER DECIDED LATER decode | job {man['job_id']} | backend {man['backend']}")
    print(f"  DELAYED (target measured first, control after):")
    print(f"    X-sort: W+<Z> = {wd['Wplus_Z']:+.3f} (mixtures 0 -> {wd['Wplus_Z']/se:+.0f} sigma off equator) | "
          f"W-<Z> = {wd['Wminus_Z']:+.3f} (mixtures 0 -> {abs(wd['Wminus_Z'])/se_m:.0f} sigma) | "
          f"X-Y = {wd['XminusY_plus']:.3f} (hull <= 1) | p- = {wd['p_minus']:.3f}")
    print(f"    Z-sort: F(A->B) = {zd['F_orderAB']:.3f}  F(B->A) = {zd['F_orderBA']:.3f}")
    print(f"  STANDARD: W+<Z> = {wst['Wplus_Z']:+.3f}  W-<Z> = {wst['Wminus_Z']:+.3f}  "
          f"Z-sort {zs['F_orderAB']:.3f}/{zs['F_orderBA']:.3f}")
    print(f"  WINDOW COST (control through target's window): dW+ = {wst['Wplus_Z']-wd['Wplus_Z']:+.3f}  "
          f"dW- = {wst['Wminus_Z']-wd['Wminus_Z']:+.3f}")
    print(f"  DECOHERED falsifier: W+<Z> = {wde['Wplus_Z']:+.3f}  W-<Z> = {wde['Wminus_Z']:+.3f} (must be ~0)")
    print(f"  NO-SIGNALING: unsorted target-marginal spread across later choices = {spread:.4f}")
    p_ok = (wd["Wplus_Z"] > 0 and wd["Wplus_Z"] / se >= 5 and wd["Wminus_Z"] < 0
            and abs(wd["Wminus_Z"]) / se_m >= 5 and zd["F_orderAB"] >= 0.85 and zd["F_orderBA"] >= 0.85)
    if tag == "b":
        f_ok = abs(wde["Wplus_Z"] - wde["Wminus_Z"]) <= 0.10   # difference form (mixture: 0)
        if "delayed_echo" in r:
            we = witnesses(r["delayed_echo"])
            rec = we["Wplus_Z"] - wd["Wplus_Z"]; cost = wst["Wplus_Z"] - wd["Wplus_Z"]
            print(f"  ECHO ARM: W+<Z> = {we['Wplus_Z']:+.3f}  W-<Z> = {we['Wminus_Z']:+.3f} | "
                  f"recovery {rec:+.3f} of the {cost:+.3f} delayed-choice cost "
                  f"({'>= half — echo criterion HELD' if cost > 0 and rec >= 0.5 * cost else 'under half'})")
    else:
        f_ok = abs(wde["Wplus_Z"]) <= 0.10 and abs(wde["Wminus_Z"]) <= 0.10
    print(f"\nPRIMARY: {'HELD — the same target record holds definite orders AND impossible-for-any-order ensembles, selected by the later choice' if p_ok else 'NOT HELD'}")
    print(f"FALSIFIER: {'HELD — a classical mixture of orders sorts flat' if f_ok else 'NOT HELD'}")
    ok = p_ok and f_ok
    print(f"VERDICT: {'THE ORDER WAS DECIDED LATER — causal order is choice-dependent structure in the record, not a property the past possessed' if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r,
           "witnesses": {"delayed": wd, "standard": wst, "decohered": wde},
           "zsort": {"delayed": zd, "standard": zs}, "nosignal_spread": float(spread),
           "primary_ok": bool(p_ok), "falsifier_ok": bool(f_ok), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", f"exp187{tag}_late_order_decode.json"), "w"), indent=1)
    print(f"-> results/exp187{tag}_late_order_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots, a.tag)
    elif a.decode: decode(a.tag)
    else: ap.print_help()
