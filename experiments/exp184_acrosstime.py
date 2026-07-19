#!/usr/bin/env python3
"""Exp184 — THE HANDSHAKE ACROSS TIME: entangling states that never coexisted. C4874.
Delayed-choice entanglement swapping (Peres/Ma/Megidish): Bell(A,B); MEASURE A (state destroyed);
only then create Bell(C,D); later Bell-measure (B,C); finally measure D. Frame-sift on the swap
outcome -> if the (A-record, D-record) correlations cross F>1/2, two states with DISJOINT
LIFETIMES were entangled — and the latechoice arm (product measurement instead of Bell) shows
the SAME early data sorts separable: the entanglement was decided after both states were gone.
Window-physics secondary (our own model): a dead qubit cannot dephase -> acrosstime should BEAT
the standard swap by one spectator's window dose.
A=q0, B=q1, C=q2, D=q3. clbits: c0,c1 = swap bits; c2 = A record; c3 = D record.
Frame on D (Exp162): x=c1, z=c0 -> flip D by Z:x, X:z, Y:x^z.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import fidelity

ARMS = ("acrosstime", "standard", "latechoice", "nomeas")
SETTINGS = ("ZZ", "XX", "YY")
WITNESS = 0.5


def _rot(qc, basis, q):
    if basis == "XX": qc.h(q)
    elif basis == "YY": qc.sdg(q); qc.h(q)


def circuit(arm, setting):
    qc = QuantumCircuit(4, 4)
    qc.h(0); qc.cx(0, 1)              # Bell(A,B)
    if arm == "standard":
        qc.h(2); qc.cx(2, 3)          # Bell(C,D) up front
        qc.barrier()
        qc.cx(1, 2); qc.h(1)          # swap
        qc.measure(1, 0); qc.measure(2, 1)
        qc.barrier()
        _rot(qc, setting, 0); _rot(qc, setting, 3)
        qc.measure(0, 2); qc.measure(3, 3)
        return qc
    # across-time schedule: A dies BEFORE D is born
    qc.barrier()
    _rot(qc, setting, 0)
    qc.measure(0, 2)                  # A measured — state destroyed, record classical
    qc.barrier()
    qc.h(2); qc.cx(2, 3)              # Bell(C,D): D's state born AFTER A's died
    qc.barrier()
    if arm == "acrosstime":
        qc.cx(1, 2); qc.h(1)          # the late swap — the handshake
        qc.measure(1, 0); qc.measure(2, 1)
    elif arm == "latechoice":
        qc.measure(1, 0); qc.measure(2, 1)   # product Z(x)Z measurement — the other choice
    # nomeas: B,C never measured
    qc.barrier()
    _rot(qc, setting, 3)
    qc.measure(3, 3)                  # D measured last
    return qc


def _parity(counts, shots, setting, arm):
    """<A D> from c2,c3 with frame sift (swap-bearing arms only). 'c3c2c1c0'."""
    frame = arm in ("acrosstime", "standard")
    acc = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        a = int(b[-3]); d = int(b[-4])
        if frame:
            c0, c1 = int(b[-1]), int(b[-2])
            if setting == "ZZ": d ^= c1
            elif setting == "XX": d ^= c0
            else: d ^= c0 ^ c1
        acc += (1 - 2 * a) * (1 - 2 * d) * n
    return acc / shots


def a_marginal(counts, shots):
    """P(a=0) — the no-signaling audit quantity."""
    return sum(n for s, n in counts.items() if s.replace(" ", "")[-3] == "0") / shots


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        par = {s: _parity(get(arm, s), shots, s, arm) for s in SETTINGS}
        marg = {s: a_marginal(get(arm, s), shots) for s in SETTINGS}
        out[arm] = {"F": float(fidelity(par)), **{k: float(v) for k, v in par.items()},
                    "A_marginal": {k: float(v) for k, v in marg.items()}}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, s):
        if (arm, s) not in cache:
            cache[(arm, s)] = sim.run(circuit(arm, s), shots=shots).result().get_counts()
        return cache[(arm, s)]
    r = analyze(get, shots)
    print("Exp184 selftest (noiseless Aer)")
    for arm in ARMS:
        print(f"  {arm:>10}: ZZ={r[arm]['ZZ']:+.3f} XX={r[arm]['XX']:+.3f} YY={r[arm]['YY']:+.3f} "
              f"-> F={r[arm]['F']:.3f}")
    assert r["acrosstime"]["F"] > 0.99, "across-time handshake must be exact noiseless"
    assert r["standard"]["F"] > 0.99, "standard swap must be exact"
    lc = r["latechoice"]
    assert abs(lc["XX"]) < 0.03 and abs(lc["YY"]) < 0.03 and lc["F"] <= 0.52, \
        "latechoice must sort the same data separable (F caps at 1/2)"
    assert abs(r["nomeas"]["F"] - 0.25) < 0.04, "nomeas must sit at 0.25"
    for s in SETTINGS:   # no-signaling: A's marginal identical across later choices
        ms = [r[a]["A_marginal"][s] for a in ("acrosstime", "latechoice", "nomeas")]
        assert max(ms) - min(ms) < 0.03, "A's record must not depend on any later choice"
    print("SELFTEST PASS: the late Bell measurement sorts the early record entangled (F=1); the "
          "late product choice sorts THE SAME record separable (F=1/2); A's marginal blind to "
          "every later choice (no-signaling). Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for s in SETTINGS:
            circuits.append(transpile(circuit(arm, s), backend=backend, optimization_level=3))
            order.append([arm, s])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 184, "slug": "acrosstime", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "witness": WITNESS,
                "prereg": {"primary": "F(acrosstime) > 1/2 at >=5 sigma (band 0.80-0.90)",
                           "latechoice": "F < 0.55 with |XX|,|YY| < 0.10 — same early data sorts separable",
                           "window_model_secondary": "F(acrosstime) - F(standard) > 0 at >=2 sigma "
                                                     "(dead qubits cannot dephase; standard band 0.78-0.88)",
                           "null": "nomeas 0.18-0.32",
                           "no_signaling_gauge": "A marginal spread < 0.02 across acrosstime/latechoice/nomeas"}}
    out = os.path.join(HERE, "..", "results", "exp184_acrosstime_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp184_acrosstime_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, s)], shots)
    se = 0.75 / np.sqrt(shots); se_d = float(np.sqrt(2) * se)
    print(f"Exp184 HANDSHAKE ACROSS TIME decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        print(f"  {arm:>10}: ZZ={r[arm]['ZZ']:+.3f} XX={r[arm]['XX']:+.3f} YY={r[arm]['YY']:+.3f} "
              f"-> F = {r[arm]['F']:.3f}")
    at, st, lc = r["acrosstime"], r["standard"], r["latechoice"]
    nsig = (at["F"] - WITNESS) / se
    dwin = at["F"] - st["F"]
    spread = max(abs(r[a]["A_marginal"][s] - r[b]["A_marginal"][s])
                 for s in SETTINGS for a in ("acrosstime", "latechoice", "nomeas")
                 for b in ("acrosstime", "latechoice", "nomeas"))
    p_ok = at["F"] > WITNESS and nsig >= 5
    lc_ok = lc["F"] < 0.55 and abs(lc["XX"]) < 0.10 and abs(lc["YY"]) < 0.10
    w_ok = dwin > 0 and (dwin / se_d) >= 2
    print(f"\nTHE HANDSHAKE: F(A-record, D-record) = {at['F']:.3f} ({nsig:.0f} sigma over 1/2) — "
          f"A was measured before D existed. {'HELD' if p_ok else 'NOT HELD'}")
    print(f"THE LATE CHOICE: product-sort of the same early record -> F = {lc['F']:.3f} "
          f"(XX {lc['XX']:+.2f}, YY {lc['YY']:+.2f}) {'— separable, as the choice decides' if lc_ok else '— UNEXPECTED'}")
    print(f"WINDOW MODEL: acrosstime - standard = {dwin:+.3f} ({dwin/se_d:+.1f} sigma) "
          f"{'— the dead qubit paid no window tax (model HELD)' if w_ok else '— model prediction not confirmed'}")
    print(f"NO-SIGNALING AUDIT: max A-marginal spread across later choices = {spread:.4f} "
          f"({'clean' if spread < 0.02 else 'CHECK'})")
    print(f"NULL: nomeas F = {r['nomeas']['F']:.3f}")
    print(f"VERDICT: {'ENTANGLED ACROSS TIME — two states with disjoint lifetimes certified entangled, and the late choice decided it' if (p_ok and lc_ok) else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r, "handshake_sigma": float(nsig),
           "window_delta": float(dwin), "window_sigma": float(dwin / se_d),
           "a_marginal_max_spread": float(spread),
           "primary_ok": bool(p_ok), "latechoice_ok": bool(lc_ok), "window_ok": bool(w_ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp184_acrosstime_decode.json"), "w"), indent=1)
    print("-> results/exp184_acrosstime_decode.json")


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
