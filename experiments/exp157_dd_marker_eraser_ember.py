#!/usr/bin/env python3
"""Exp157 — Dynamical decoupling on the marker qubit in the delayed-choice eraser (Ember, C4198).
Creator directive: "fly dd marker!" — the forward lever Elder named on Exp154 and I flagged on Exp155.

THE QUESTION. Exp155's DYNAMIC delayed-choice arm lost fringe visibility (erase V=0.797) vs the STATIC
arm (0.946) because the marker qubit M idles through S's mid-circuit measurement, the coin's
measurement, and the feed-forward latency, dephasing in the X basis it is later read in. Does a
dynamical-decoupling (DD) echo on M across that idle window RECOVER the visibility toward the ceiling?

DESIGN. Three arms, all 8-phase, ONE job (within-job comparison — device drift would confound a
2-job A/B):
  A) STATIC erase        : the ceiling reference (no marker idle). Exp155 measured ~0.946.
  B) DYNAMIC no-DD       : Exp155's dynamic delayed-choice arm, re-flown (baseline ~0.797).
  C) DYNAMIC + DD        : identical to B plus an X-X (Hahn) echo on M straddling the two slow
                           measurements. Net XX = I (logical no-op), so the erase physics is
                           unchanged; the echo refocuses quasi-static dephasing accumulated during
                           the idle. Applied BEFORE the conditional erase-H so the erase basis is intact.

THE NUMBER. V_dd_erase - V_nodd_erase (coin=1 branch). Positive = DD recovers the delayed-choice
fringe toward the static ceiling. NULL (<=0) is a FIRST-CLASS result: it would say the feed-forward
idle error is NOT quasi-static dephasing DD can refocus at these timescales (measurement crosstalk /
leakage / T1), which is itself a sharp statement about the idle-error class (Exp143/144/154/155).

LOAD-BEARING VERIFICATION (the C4196 axis-match discipline). optimization_level=3 will CANCEL an X-X
pair on an otherwise-idle qubit (XX=I) and silently delete the DD. So (1) barriers pin each DD pulse,
and (2) submit ASSERTS the transpiled DD arm carries MORE physical X/echo gates on the marker than the
no-DD arm — DD that gets optimized away is exactly "the control didn't pay the cost."

HONESTY FENCE. The noiseless truth-gate CANNOT predict whether DD helps — noiselessly XX=I so arms B
and C are identical (both V=1). DD's benefit is a hardware-noise effect only. So this is a
hardware-only hypothesis, my worst-calibrated situation (C3869): confidence capped low, null on the
table. No-signaling (flat marginal) must still hold for every arm.

Usage:
  python3 exp157_dd_marker_eraser_ember.py --selftest
  python3 exp157_dd_marker_eraser_ember.py --submit [--backend ibm_fez --shots 4000]
  python3 exp157_dd_marker_eraser_ember.py --decode --manifest ../results/exp157_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

N_PHI = 8
PHASES = [2.0 * np.pi * k / N_PHI for k in range(N_PHI)]


def _bit(key, i):
    return key.replace(" ", "")[-1 - i]


def static_erase_circuit(phi):
    """Ceiling reference: erase arm, both qubits measured at end (no marker idle)."""
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1); qc.rz(phi, 0); qc.h(0)
    qc.barrier(); qc.h(1)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def dynamic_circuit(phi, dd):
    """q0=S, q1=M, q2=coin. Measure S, flip a quantum coin r AFTER S, conditionally erase M iff r==1.
    dd=True inserts a HAHN echo on M that SUBDIVIDES the idle: the two X pulses straddle S's readout
    ONLY, so M is flipped during measure(0) and normal during measure(2) -> the two equal-duration
    readouts refocus to first order (advisor C4198: bracketing both readouts does NOT refocus; the
    flip must sit at the midpoint of the balanced idle). XX=I closes before the erase-H (basis intact).
    Barriers pin the pulses so opt-level-3 cannot cancel the pair. The post-pulse2 feed-forward-latency
    idle stays unbalanced (cannot DD across the if_test) -- acknowledged, not chased."""
    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1); qc.rz(phi, 0); qc.h(0)
    if dd:
        qc.barrier(); qc.x(1); qc.barrier()      # DD pulse 1 (before S readout)
    qc.measure(0, 0)                              # S recorded -- the past (M flipped through THIS readout)
    qc.barrier()
    if dd:
        qc.barrier(); qc.x(1); qc.barrier()      # DD pulse 2 -> midpoint: closes XX=I echo over S's readout
    qc.h(2); qc.measure(2, 2)                     # quantum coin r, AFTER S (M normal through THIS readout)
    with qc.if_test((qc.clbits[2], 1)):
        qc.h(1)                                   # r=1 erase / r=0 keep
    qc.measure(1, 1)
    return qc


def _cond_fringe(counts_by_phi, select):
    """Returns cond P(S=0|M=0) and marginal P(S=0) per phase, plus the conditional (numerator,
    denominator) per phase for binomial bootstrapping."""
    cond, marg, cnum, cden = [], [], [], []
    for counts in counts_by_phi:
        s0_m0 = s_all_m0 = s0_all = tot = 0
        for key, c in counts.items():
            if select is not None and not select(key):
                continue
            s0 = _bit(key, 0) == "0"; m0 = _bit(key, 1) == "0"
            tot += c
            if s0: s0_all += c
            if m0:
                s_all_m0 += c
                if s0: s0_m0 += c
        cond.append(s0_m0 / s_all_m0 if s_all_m0 else 0.5)
        marg.append(s0_all / tot if tot else 0.5)
        cnum.append(s0_m0); cden.append(s_all_m0)
    return cond, marg, cnum, cden


def _visibility(p):
    """Simple (max-min)/(max+min) — used for the marginal flatness check."""
    p = np.asarray(p, float); hi, lo = p.max(), p.min()
    return (hi - lo) / (hi + lo) if (hi + lo) > 1e-9 else 0.0


def _fit_visibility(cond, phases=PHASES):
    """Linear LS fit P = A + B cos(phi) + C sin(phi); visibility = amplitude/offset = hypot(B,C)/A.
    Less biased than (max-min)/(max+min) and drift/phase-robust (advisor C4198). Ideal erase
    P=(1+cos)/2 -> A=0.5,B=0.5,C=0 -> V=1; flat -> V=0."""
    ph = np.asarray(phases, float)
    M = np.column_stack([np.ones_like(ph), np.cos(ph), np.sin(ph)])
    A, B, C = np.linalg.lstsq(M, np.asarray(cond, float), rcond=None)[0]
    return float(np.hypot(B, C) / A) if abs(A) > 1e-9 else 0.0


def _bootstrap_vis_se(cnum, cden, nboot=800, seed=20260718):
    """Binomial-resample the conditional counts per phase, refit visibility, return SE (std)."""
    rng = np.random.default_rng(seed)
    cnum = np.asarray(cnum, float); cden = np.asarray(cden, float)
    vs = []
    for _ in range(nboot):
        p = []
        for n, d in zip(cnum, cden):
            dd = int(d) if d >= 1 else 1
            phat = n / d if d > 0 else 0.5
            p.append(rng.binomial(dd, min(max(phat, 0.0), 1.0)) / dd)
        vs.append(_fit_visibility(p))
    return float(np.std(vs))


def _run_sim(circuits, shots=30000):
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    return [sim.run(qc, shots=shots).result().get_counts() for qc in circuits]


def selftest():
    """Noiseless truth-gate. XX=I so the DD and no-DD dynamic arms are IDENTICAL noiselessly (both
    erase V=1, keep V=0). Static erase V=1. Marginal flat. This gate proves the DD is a logical no-op
    (erase physics intact) and the no-signaling fence holds; it CANNOT and does NOT claim DD helps on
    hardware -- that is the hardware-only hypothesis."""
    st = _run_sim([static_erase_circuit(p) for p in PHASES])
    nod = _run_sim([dynamic_circuit(p, dd=False) for p in PHASES])
    ddd = _run_sim([dynamic_circuit(p, dd=True) for p in PHASES])

    cs, ms, _, _ = _cond_fringe(st, None)
    n1, mn1, _, _ = _cond_fringe(nod, lambda k: _bit(k, 2) == "1")
    n0, _, _, _ = _cond_fringe(nod, lambda k: _bit(k, 2) == "0")
    d1, md1, _, _ = _cond_fringe(ddd, lambda k: _bit(k, 2) == "1")
    d0, _, _, _ = _cond_fringe(ddd, lambda k: _bit(k, 2) == "0")

    Vs, Vn1, Vd1 = map(_fit_visibility, (cs, n1, d1))
    Vn0, Vd0 = map(_fit_visibility, (n0, d0))
    Vmarg = max(_visibility(ms), _visibility(mn1), _visibility(md1))
    print("Exp157 selftest (noiseless Aer)")
    print(f"  STATIC erase          V={Vs:.3f}   (ceiling ref)")
    print(f"  DYNAMIC no-DD  erase   V={Vn1:.3f}   keep V={Vn0:.3f}")
    print(f"  DYNAMIC +DD    erase   V={Vd1:.3f}   keep V={Vd0:.3f}   (XX=I -> identical noiselessly)")
    print(f"  NO-SIGNALING marginal V_marg={Vmarg:.3f}")
    assert Vs > 0.98 and Vn1 > 0.98 and Vd1 > 0.98, "erase arms must show full fringe"
    assert Vn0 < 0.08 and Vd0 < 0.08, "keep branches must be flat"
    assert Vmarg < 0.05, "no-signaling: marginal must stay flat"
    assert abs(Vd1 - Vn1) < 0.03, "DD must be a logical no-op noiselessly (erase physics unchanged)"
    print("SELFTEST PASS: DD is a noiseless no-op (erase intact), fences hold. Whether DD RECOVERS "
          "visibility is a HARDWARE-only question this gate cannot answer.")


def _marker_echo_gate_count(tqc):
    """Count physical single-qubit X/echo (sx-heavy) ops — proxy for DD surviving transpile."""
    ops = tqc.count_ops()
    return ops.get("x", 0) + ops.get("sx", 0) + ops.get("rx", 0) + ops.get("y", 0)


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []

    # transpile with a verification that DD survives (load-bearing axis check)
    t_nod = [transpile(dynamic_circuit(p, dd=False), backend=backend, optimization_level=3) for p in PHASES]
    t_ddd = [transpile(dynamic_circuit(p, dd=True), backend=backend, optimization_level=3) for p in PHASES]
    avg_nod = np.mean([_marker_echo_gate_count(t) for t in t_nod])
    avg_ddd = np.mean([_marker_echo_gate_count(t) for t in t_ddd])
    print(f"transpiled 1q(x/sx/rx/y) gate count: no-DD avg {avg_nod:.1f} vs +DD avg {avg_ddd:.1f}")
    assert avg_ddd > avg_nod + 1.0, ("DD did not survive transpilation (X-X cancelled) — the arms are "
                                     "identical, no test. Add stronger barriers or lower opt level.")
    print("LOAD-BEARING CHECK PASS: the +DD arm carries strictly more echo gates on hardware.")

    for i, p in enumerate(PHASES):
        circuits.append(transpile(static_erase_circuit(p), backend=backend, optimization_level=3))
        order.append(["static_erase", i])
    for i in range(N_PHI):
        circuits.append(t_nod[i]); order.append(["dynamic_nodd", i])
    for i in range(N_PHI):
        circuits.append(t_ddd[i]); order.append(["dynamic_dd", i])

    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 157, "backend": backend_name, "shots": shots, "job_id": job.job_id(),
                "phases": PHASES, "order": order,
                "transpiled_1q_gates": {"nodd": float(avg_nod), "dd": float(avg_ddd)},
                "prereg": {"confidence": 0.55,
                           "gate": "(V_dd_erase - V_nodd_erase) > 2*sigma_bootstrap AND V_marginal < 0.1",
                           "null_is_first_class": "DD<=0 recovery => idle error is not DD-refocusable "
                                                  "quasi-static dephasing (measurement crosstalk/leakage/T1)",
                           "not_sim_replicable": "noiseless XX=I; DD benefit is hardware-only"},
                "note": "DD echo on marker across feed-forward idle; static ceiling + dynamic no-DD/DD; "
                        "within-job A/B; self-verifying (known phi); no-signaling fence"}
    out = os.path.join(HERE, "..", "results", "exp157_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = 3 arms x {N_PHI} phi, {shots} shots) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    by = {"static_erase": [None] * N_PHI, "dynamic_nodd": [None] * N_PHI, "dynamic_dd": [None] * N_PHI}
    for idx, (arm, i) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        by[arm][i] = getattr(r.data, reg).get_counts()

    cs, ms, _, _ = _cond_fringe(by["static_erase"], None)
    n1, mn1, nnum, nden = _cond_fringe(by["dynamic_nodd"], lambda k: _bit(k, 2) == "1")
    n0, _, _, _ = _cond_fringe(by["dynamic_nodd"], lambda k: _bit(k, 2) == "0")
    d1, md1, dnum, dden = _cond_fringe(by["dynamic_dd"], lambda k: _bit(k, 2) == "1")
    d0, _, _, _ = _cond_fringe(by["dynamic_dd"], lambda k: _bit(k, 2) == "0")

    Vs, Vn1, Vd1 = map(_fit_visibility, (cs, n1, d1))
    Vn0, Vd0 = map(_fit_visibility, (n0, d0))
    Vmarg = max(_visibility(ms), _visibility(mn1), _visibility(md1))

    se_nod = _bootstrap_vis_se(nnum, nden)
    se_dd = _bootstrap_vis_se(dnum, dden)
    recovery = Vd1 - Vn1
    se_rec = float(np.hypot(se_nod, se_dd))
    z = recovery / se_rec if se_rec > 1e-9 else 0.0
    frac_closed = recovery / (Vs - Vn1) if (Vs - Vn1) > 1e-6 else float("nan")

    print(f"Exp157 decode | job {man['job_id']} | backend {man['backend']}")
    print(f"  STATIC erase (ceiling)   V={Vs:.3f}")
    print(f"  DYNAMIC no-DD  erase     V={Vn1:.3f} +/- {se_nod:.3f}   keep V={Vn0:.3f}")
    print(f"  DYNAMIC +DD    erase     V={Vd1:.3f} +/- {se_dd:.3f}   keep V={Vd0:.3f}")
    print(f"  NO-SIGNALING marginal    V_marg={Vmarg:.3f}")
    print(f"\n  DD RECOVERY  V_dd_erase - V_nodd_erase = {recovery:+.3f} +/- {se_rec:.3f}  (z = {z:+.2f})")
    print(f"  fraction of the static gap closed by DD: {frac_closed:.1%}  (gap = {Vs - Vn1:.3f})")
    gate = z > 2.0 and Vmarg < 0.1
    print(f"  PRE-REG GATE (recovery > 2 sigma AND V_marg<0.1): {'HELD' if gate else 'FALSIFIED'}")
    if z <= 2.0:
        print("  -> NULL/FALSIFIED is first-class: no >2sigma DD recovery -> the feed-forward idle "
              "error is not DD-refocusable quasi-static dephasing at these timescales "
              "(measurement crosstalk / leakage / T1), OR DD gate-cost offsets the gain.")

    out = {"job_id": man["job_id"], "backend": man["backend"], "V_static": Vs,
           "V_nodd_erase": Vn1, "se_nodd": se_nod, "V_dd_erase": Vd1, "se_dd": se_dd,
           "dd_recovery": recovery, "se_recovery": se_rec, "z": z,
           "fraction_gap_closed": frac_closed, "V_nodd_keep": Vn0, "V_dd_keep": Vd0,
           "V_marginal": Vmarg, "prereg_gate_held": bool(gate),
           "cond_static": cs, "cond_nodd": n1, "cond_dd": d1}
    fn = os.path.join(HERE, "..", "results", "exp157_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp157_manifest.json"))
    else: ap.print_help()
