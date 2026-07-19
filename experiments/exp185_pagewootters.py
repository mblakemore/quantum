#!/usr/bin/env python3
"""Exp185 — THE UNIVERSE WHERE TIME IS OPTIONAL: Page-Wootters emergent time. C4875.
A 3-qubit universe: clock C (q0=1s bit, q1=2s bit) entangled with system S (q2) in the Feynman
history state |Psi> = 1/2 sum_t |t> S^t |+>  (law U = S, U^4 = I exactly).
Three legs: (1) INTERNAL TIME — conditional on clock=t the system sweeps the equator 90deg/tick;
(2) EXTERNAL FROZEN — the internal translation T = increment(x)S leaves |Psi> invariant
(Loschmidt echo ~ prep quality), while the WRONG-LAW translation increment(x)1 costs exactly 1/2;
(3) OFF-SWITCH — cut the entanglement and every tick shows the same |+>: time vanishes.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

PI = np.pi
# predicted equator sweep (X,Y) per tick for S^t|+>
PRED = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}
CIRCS = ("history_X", "history_Y", "echo_id", "echo_T", "echo_Tclock", "notime_X", "notime_Y")


def _prep(qc, entangled=True):
    qc.h(0); qc.h(1); qc.h(2)
    if entangled:
        qc.cp(PI / 2, 0, 2)       # controlled-S from the 1s bit
        qc.cz(1, 2)               # controlled-S^2 = CZ from the 2s bit
    qc.barrier()


def _prep_inv(qc, entangled=True):
    qc.barrier()
    if entangled:
        qc.cz(1, 2)
        qc.cp(-PI / 2, 0, 2)
    qc.h(0); qc.h(1); qc.h(2)


def _translation(qc, with_law):
    qc.cx(0, 1); qc.x(0)          # clock increment mod 4 (carry, then flip 1s bit)
    if with_law:
        qc.s(2)                   # ...carrying the law of physics with it


def circuit(name):
    qc = QuantumCircuit(3, 3)
    if name.startswith("history") or name.startswith("notime"):
        _prep(qc, entangled=name.startswith("history"))
        basis = name[-1]
        if basis == "X": qc.h(2)
        else: qc.sdg(2); qc.h(2)
        qc.measure(0, 0); qc.measure(1, 1); qc.measure(2, 2)
    else:
        _prep(qc, True)
        if name == "echo_T": _translation(qc, with_law=True)
        elif name == "echo_Tclock": _translation(qc, with_law=False)
        _prep_inv(qc, True)
        qc.measure(0, 0); qc.measure(1, 1); qc.measure(2, 2)
    return qc


def conditional_bloch(counts_X, counts_Y, shots):
    """Per clock tick t: (X_t, Y_t, n_t) from the two tomography circuits."""
    out = {}
    for t in range(4):
        c0, c1 = t & 1, (t >> 1) & 1
        vals = {}
        for basis, counts in (("X", counts_X), ("Y", counts_Y)):
            n0 = n1 = 0
            for s, n in counts.items():
                b = s.replace(" ", "")
                if int(b[-1]) == c0 and int(b[-2]) == c1:
                    if int(b[-3]) == 0: n0 += n
                    else: n1 += n
            tot = n0 + n1
            vals[basis] = ((n0 - n1) / tot if tot else 0.0, tot)
        out[t] = {"X": vals["X"][0], "Y": vals["Y"][0], "n": vals["X"][1] + vals["Y"][1]}
    return out


def tick_fidelity(bloch, pred):
    return (1 + bloch["X"] * pred[0] + bloch["Y"] * pred[1]) / 2


def p000(counts, shots):
    return sum(n for s, n in counts.items() if s.replace(" ", "") == "000") / shots


def analyze(get, shots):
    r = {}
    hist = conditional_bloch(get("history_X"), get("history_Y"), shots)
    noti = conditional_bloch(get("notime_X"), get("notime_Y"), shots)
    r["history"] = {t: {**hist[t], "F_evolving": float(tick_fidelity(hist[t], PRED[t]))}
                    for t in range(4)}
    r["notime"] = {t: {**noti[t], "F_static": float(tick_fidelity(noti[t], PRED[0]))}
                   for t in range(4)}
    r["echo_id"] = float(p000(get("echo_id"), shots))
    r["echo_T"] = float(p000(get("echo_T"), shots))
    r["echo_Tclock"] = float(p000(get("echo_Tclock"), shots))
    r["mean_F_evolving"] = float(np.mean([r["history"][t]["F_evolving"] for t in range(4)]))
    r["mean_F_static"] = float(np.mean([r["notime"][t]["F_static"] for t in range(4)]))
    return r


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(name):
        if name not in cache:
            cache[name] = sim.run(circuit(name), shots=shots).result().get_counts()
        return cache[name]
    r = analyze(get, shots)
    print("Exp185 selftest (noiseless Aer)")
    for t in range(4):
        h = r["history"][t]
        print(f"  tick {t}: (X,Y)=({h['X']:+.2f},{h['Y']:+.2f}) pred {PRED[t]}  F={h['F_evolving']:.3f}")
    print(f"  echo_id={r['echo_id']:.3f}  echo_T={r['echo_T']:.3f}  echo_Tclock={r['echo_Tclock']:.3f}")
    print(f"  notime mean F(static |+>)={r['mean_F_static']:.3f}")
    assert r["mean_F_evolving"] > 0.99, "inhabitants must see exact evolution"
    for t in range(4):
        px, py = PRED[t]; h = r["history"][t]
        assert abs(h["X"] - px) < 0.05 and abs(h["Y"] - py) < 0.05, f"tick {t} sign pattern"
    assert r["echo_id"] > 0.99 and r["echo_T"] > 0.99, "correct-law translation must be invisible"
    assert abs(r["echo_Tclock"] - 0.5) < 0.02, "wrong-law translation must cost exactly 1/2"
    assert r["mean_F_static"] > 0.99, "cut the entanglement and time must vanish"
    print("SELFTEST PASS: inhabitants see 90deg/tick evolution; the correct-law translation is "
          "echo-invisible while the clock-only translation costs exactly 1/2; without entanglement "
          "every tick is |+> — time switched off. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for name in CIRCS:
        circuits.append(transpile(circuit(name), backend=backend, optimization_level=3))
        order.append(name)
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 185, "slug": "pagewootters", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"leg1_internal_time": "mean per-tick F(evolving) >= 0.90 (band 0.92-0.98), sign pattern 4/4",
                           "leg2_frozen": "echo_T >= 0.80 (band 0.82-0.95) AND echo_T - echo_Tclock >= 0.25; "
                                          "echo_Tclock band 0.40-0.55 (ideal 0.5); echo_id band 0.88-0.98; "
                                          "sharp form: echo_T within 0.06 of echo_id",
                           "leg3_offswitch": "notime mean F(static |+>) >= 0.90 (band 0.93-0.99)"}}
    out = os.path.join(HERE, "..", "results", "exp185_pagewootters_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp185_pagewootters_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda name: raw[name], shots)
    print(f"Exp185 PAGE-WOOTTERS decode | job {man['job_id']} | backend {man['backend']}")
    print("  THE INHABITANTS' CLOCK (conditional on the clock reading):")
    signs_ok = True
    for t in range(4):
        h = r["history"][t]
        px, py = PRED[t]
        ok = (abs(h["X"] - px) < 0.5 and abs(h["Y"] - py) < 0.5)
        signs_ok &= ok
        print(f"    tick {t}: (X,Y)=({h['X']:+.3f},{h['Y']:+.3f})  pred ({px:+d},{py:+d})  "
              f"F={h['F_evolving']:.3f}  [n={h['n']}]")
    print(f"  mean F(evolving) = {r['mean_F_evolving']:.3f}")
    print(f"  THE OUTSIDE VIEW: echo_id={r['echo_id']:.3f}  echo_T={r['echo_T']:.3f}  "
          f"echo_Tclock={r['echo_Tclock']:.3f}")
    print(f"  THE OFF-SWITCH: notime per-tick F(static)= " +
          " ".join(f"{r['notime'][t]['F_static']:.3f}" for t in range(4)) +
          f"  mean={r['mean_F_static']:.3f}")
    leg1 = r["mean_F_evolving"] >= 0.90 and signs_ok
    leg2 = r["echo_T"] >= 0.80 and (r["echo_T"] - r["echo_Tclock"]) >= 0.25
    leg2_sharp = abs(r["echo_T"] - r["echo_id"]) <= 0.06
    leg3 = r["mean_F_static"] >= 0.90
    print(f"\nLEG 1 — INHABITANTS HAVE TIME:   {'HELD' if leg1 else 'NOT HELD'} "
          f"(mean F {r['mean_F_evolving']:.3f}, signs {'4/4' if signs_ok else 'FAILED'})")
    print(f"LEG 2 — OUTSIDE IS FROZEN:       {'HELD' if leg2 else 'NOT HELD'} "
          f"(correct-law echo {r['echo_T']:.3f} vs wrong-law {r['echo_Tclock']:.3f}; "
          f"{'law-translation costs ~nothing vs prep' if leg2_sharp else 'law-translation cost above sharp band'})")
    print(f"LEG 3 — TIME HAS AN OFF-SWITCH:  {'HELD' if leg3 else 'NOT HELD'} "
          f"(no entanglement -> every tick identical at F {r['mean_F_static']:.3f})")
    ok = leg1 and leg2 and leg3
    print(f"VERDICT: {'TIME IS ENTANGLEMENT — the inhabitants evolve, the outside is frozen, and cutting the entanglement switches time off' if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r, "legs": {"internal_time": bool(leg1),
           "frozen_outside": bool(leg2), "frozen_sharp": bool(leg2_sharp), "off_switch": bool(leg3)},
           "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp185_pagewootters_decode.json"), "w"), indent=1)
    print("-> results/exp185_pagewootters_decode.json")


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
