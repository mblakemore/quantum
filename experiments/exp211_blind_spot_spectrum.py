#!/usr/bin/env python3
"""Exp211 — THE BLIND-SPOT SPECTRUM: the shield's coherent-error transfer function. C4905.

Horizons-5 P5, flight 1 (the self-characterizing chip), on the standing go. Exp199 found ONE
blind spot: a global coherent Z-rotation passes the [[4,2,2]] shield's inspection while
corrupting most of what it accepts. This flight maps the FULL spectrum — which coherent-error
AXES pass silently, which are transparent, which are caught — turning the shield into a
spectrometer for its own coherent noise (the P5 "self-characterizing chip").

Apparatus (Exp199 verbatim): prep |+bar +bar> = H^4 . GHZ4; apply a global coherent rotation
R_axis(theta)^4 (the error family); X-basis readout (H^4, measure). Per (axis, dose):
  ACCEPTANCE A = fraction passing the XXXX-parity check (does the shield SEE the error?)
  CORRUPTION L = fraction of ACCEPTED shots with Xbar1 flipped (does it DAMAGE the logical?)
  SILENT-CORRUPTION P_silent = A * L (high = passes inspection AND corrupts = a blind spot)

Axes {X, Y, Z} x doses theta/pi {0, 1/4, 1/2, 3/4, 1} = 15 circuits. On the X-eigenstate
|+bar>, the Z-axis is the 199 blind spot; the X-axis rotation leaves |+bar> invariant
(transparent); the Y-axis is the discriminating third point. Exact A, L per axis/dose from the
statevector (frozen from the selftest, no hand algebra).

FROZEN GATES (relative to statevector-exact, computed in selftest):
  G1_REPRODUCE_199: Z-axis at theta=pi/2 has A >= 0.85 AND L >= 0.60 (the blind spot; 199
     measured 0.956 / 0.75).
  G2_TRANSFER_FUNCTION: |A_meas - A_exact| <= 0.12 and |L_meas - L_exact| <= 0.12 at every
     (axis, interior dose) — the measured transfer function matches theory.
  G3_AXIS_DISCRIMINATION: P_silent(blind axis, pi/2) - P_silent(transparent axis, pi/2) >= 0.30
     at >=5 sigma (the shield's response is axis-selective — the spectrometer resolves).
  G4_MAP (reported): the full A/L/P_silent map; the blind-spot locus identified.
Registered verdict = G1 and G2 and G3.
SCOPE: [[4,2,2]] coherent-error transfer function on the X-basis logical info, |+bar> input,
global-rotation error family (single-qubit-correlated). Extends 199 from one axis to the
spectrum. Textbook code + 199 priors credited; the contribution is the measured transfer
function / blind-spot map.
BUDGET CHECK (C4887): 199 measured the Z blind spot at A~0.96/L~0.75 with baseline escape 0.02;
margins >> noise. Filed: Z blind spot A>=0.88/L>=0.65; X-axis P_silent < 0.10; discrimination
>= 0.4.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
AXES = ("X", "Y", "Z")
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
INTERIOR = (0.25, 0.5, 0.75)


def circuit(axis, t, measured=True):
    th = t * PI
    qc = QuantumCircuit(4, 4 if measured else 0)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)   # |0bar0bar> = GHZ4
    for q in range(4): qc.h(q)                        # -> |+bar+bar>
    qc.barrier()
    for q in range(4):                                # global coherent error R_axis(theta)^4
        if axis == "X": qc.rx(th, q)
        elif axis == "Y": qc.ry(th, q)
        elif axis == "Z": qc.rz(th, q)
    qc.barrier()
    for q in range(4): qc.h(q)                        # X-basis readout
    if measured:
        for q in range(4): qc.measure(q, q)
    return qc


def _stats(counts):
    acc = rej = corr = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(4)]
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) != 0:          # XXXX-parity reject
            rej += n; continue
        acc += n
        corr += n * (1 if ((v[0] ^ v[1]) or (v[0] ^ v[2])) else 0)  # Xbar1 OR Xbar2 (199 union)
    tot = acc + rej
    return {"A": acc / tot if tot else 0.0, "L": corr / acc if acc else 0.0,
            "n_acc": acc, "n": tot}


def analyze(get):
    r = {(ax, t): _stats(get(ax, t)) for ax in AXES for t in DOSES}
    for k in r:
        r[k]["P_silent"] = r[k]["A"] * r[k]["L"]
    return r


def exact():
    """Statevector-exact A, L, P_silent per (axis, dose) — the frozen theory."""
    from qiskit.quantum_info import Statevector
    out = {}
    for ax in AXES:
        for t in DOSES:
            sv = Statevector(circuit(ax, t, measured=False))
            probs = sv.probabilities_dict(range(4))
            acc = corr = 0.0
            for bs, p in probs.items():
                b = bs[::-1]                           # index i = qubit i
                v = [int(b[i]) for i in range(4)]
                if (v[0] ^ v[1] ^ v[2] ^ v[3]) != 0:
                    continue
                acc += p
                corr += p * (1 if ((v[0] ^ v[1]) or (v[0] ^ v[2])) else 0)
            A = acc; L = corr / acc if acc > 1e-12 else 0.0
            out[(ax, t)] = {"A": A, "L": L, "P_silent": A * L}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    ex = exact()
    print("Exp211 selftest | the shield's coherent-error transfer function (statevector-exact):")
    print(f"  {'axis':>4} {'dose':>5} {'A(accept)':>10} {'L(corrupt)':>11} {'P_silent':>9}")
    for ax in AXES:
        for t in DOSES:
            e = ex[(ax, t)]
            print(f"  {ax:>4} {t:>5} {e['A']:>10.4f} {e['L']:>11.4f} {e['P_silent']:>9.4f}")
    # sanity: Z is the 199 blind spot; identify the transparent axis
    z_blind = ex[("Z", 0.5)]
    assert z_blind["A"] >= 0.85 and z_blind["L"] >= 0.60, "Z@pi/2 must reproduce the 199 blind spot"
    psil = {ax: ex[(ax, 0.5)]["P_silent"] for ax in AXES}
    blind_axis = max(psil, key=psil.get); transp_axis = min(psil, key=psil.get)
    print(f"  blind-spot axis @pi/2: {blind_axis} (P_silent {psil[blind_axis]:.3f}); "
          f"transparent axis: {transp_axis} (P_silent {psil[transp_axis]:.3f})")
    assert psil[blind_axis] - psil[transp_axis] >= 0.30, "axes must be discriminable"
    # Aer matches statevector
    sim = AerSimulator(); shots = 40000
    def get(ax, t):
        return sim.run(circuit(ax, t), shots=shots).result().get_counts()
    r = analyze(get)
    for ax in AXES:
        for t in DOSES:
            assert abs(r[(ax, t)]["A"] - ex[(ax, t)]["A"]) < 0.02, f"A mismatch {ax},{t}"
            if r[(ax, t)]["n_acc"] > 1000:
                assert abs(r[(ax, t)]["L"] - ex[(ax, t)]["L"]) < 0.03, f"L mismatch {ax},{t}"
    print("SELFTEST PASS: the transfer function is exact; the Z-axis reproduces 199's blind spot, "
          "the axes are discriminable, Aer matches statevector. Cleared to fly.")
    return ex


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    ex = exact()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = [[ax, t] for ax in AXES for t in DOSES]
    circuits = [transpile(circuit(ax, t), backend=backend, optimization_level=3, seed_transpiler=0)
                for ax, t in names]
    n2s = [sum(1 for inst in c.data if inst.operation.num_qubits == 2) for c in circuits]
    print(f"  {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp211_blind_spot_spectrum_manifest.json")
    man = {"exp": 211, "slug": "blind_spot_spectrum", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names,
           "exact": {f"{ax}_{t}": ex[(ax, t)] for ax in AXES for t in DOSES}}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "G1_reproduce_199": "Z-axis theta=pi/2: A >= 0.85 AND L >= 0.60",
        "G2_transfer_function": "|A_meas-A_exact|<=0.12 and |L_meas-L_exact|<=0.12 at every "
                                "(axis, interior dose)",
        "G3_axis_discrimination": "P_silent(blind axis,pi/2) - P_silent(transparent axis,pi/2) "
                                  ">= 0.30 at >=5 sigma",
        "G4_map": "full A/L/P_silent map + blind-spot locus (reported)",
        "registered_verdict": "G1 and G2 and G3",
        "budget_predictions": "Z blind spot A>=0.88/L>=0.65; X-axis P_silent<0.10; "
                              "discrimination >= 0.4"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp211_blind_spot_spectrum_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (ax, t) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(ax, float(t))] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda ax, t: raw[(ax, t)])
    ex = {(ax, t): man["exact"][f"{ax}_{t}"] for ax in AXES for t in DOSES}
    shots = man["shots"]
    print(f"Exp211 THE BLIND-SPOT SPECTRUM decode | job {man['job_id']}")
    print(f"  {'axis':>4} {'dose':>5} {'A':>7} {'(exact)':>8} {'L':>7} {'(exact)':>8} {'P_silent':>9}")
    for ax in AXES:
        for t in DOSES:
            m = r[(ax, t)]; e = ex[(ax, t)]
            print(f"  {ax:>4} {t:>5} {m['A']:>7.3f} {e['A']:>8.3f} {m['L']:>7.3f} {e['L']:>8.3f} "
                  f"{m['P_silent']:>9.3f}")
    zb = r[("Z", 0.5)]
    g1 = zb["A"] >= 0.85 and zb["L"] >= 0.60
    g2 = all(abs(r[(ax, t)]["A"] - ex[(ax, t)]["A"]) <= 0.12
             and abs(r[(ax, t)]["L"] - ex[(ax, t)]["L"]) <= 0.12
             for ax in AXES for t in INTERIOR)
    psil = {ax: r[(ax, 0.5)]["P_silent"] for ax in AXES}
    blind_axis = max(psil, key=psil.get); transp_axis = min(psil, key=psil.get)
    disc = psil[blind_axis] - psil[transp_axis]
    na = min(r[(blind_axis, 0.5)]["n_acc"], max(r[(transp_axis, 0.5)]["n_acc"], 1))
    se_disc = np.sqrt(2) / np.sqrt(shots)     # conservative
    z_disc = disc / se_disc
    g3 = disc >= 0.30 and z_disc >= 5
    print(f"\nG1 REPRODUCE 199 (Z blind spot @pi/2): A={zb['A']:.3f} L={zb['L']:.3f} "
          f"{'OK' if g1 else 'MISS'}")
    print(f"G2 TRANSFER FUNCTION: max |dA| "
          f"{max(abs(r[(ax,t)]['A']-ex[(ax,t)]['A']) for ax in AXES for t in INTERIOR):.3f}, "
          f"max |dL| {max(abs(r[(ax,t)]['L']-ex[(ax,t)]['L']) for ax in AXES for t in INTERIOR):.3f} "
          f"{'OK' if g2 else 'MISS'}")
    print(f"G3 AXIS DISCRIMINATION: blind={blind_axis} (P_s {psil[blind_axis]:.3f}) vs "
          f"transparent={transp_axis} (P_s {psil[transp_axis]:.3f}); gap {disc:.3f} "
          f"({z_disc:.0f} sigma) {'OK' if g3 else 'MISS'}")
    print(f"G4 MAP: blind-spot locus = {blind_axis}-axis; "
          f"P_silent by axis @pi/2: " + " ".join(f"{ax}:{psil[ax]:.3f}" for ax in AXES))
    ok = g1 and g2 and g3
    win = ("THE BLIND-SPOT SPECTRUM — the [[4,2,2]] shield's coherent-error transfer function "
           "measured: the code is a spectrometer for its own coherent noise, resolving which "
           "error axes pass silently (blind) from which it catches or ignores")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "map": {f"{ax}_{t}": r[(ax, t)] for ax in AXES for t in DOSES},
               "blind_axis": blind_axis, "transparent_axis": transp_axis,
               "discrimination": float(disc), "sigma_disc": float(z_disc),
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp211_blind_spot_spectrum_decode.json"), "w"), indent=1)
    print("-> results/exp211_blind_spot_spectrum_decode.json")


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
