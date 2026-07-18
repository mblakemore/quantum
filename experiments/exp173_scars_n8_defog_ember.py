#!/usr/bin/env python3
"""Exp173 — N=8 scars, CLEAR THE FOG: readout mitigation + data-driven s -> does the de-fogged scar
anomaly reach the NOISELESS value? (Creator directive 2026-07-18: "clear the fog at N=8 instead" of
going deeper to N=10.)

WHY. Exp172 (N=8, 433 CZ) showed the scar SURVIVES the wall (Neel anomaly +0.064, R=0.58~N=6's 0.56),
but two fogs limited the read: (1) the fidelity channel F was readout-limited (8-qubit return prob,
R=0.45 < Neel's 0.58, only 1.7 sigma); (2) even Neel's R~0.58 (not 1.0) means ~0.42 of the signal is
lost to fog my 2q-only survival model does not capture (readout + 1q/idle + coherent Trotter error).
Going to N=10 adds MORE fog; clearing it at N=8 sharpens the same question with no depth penalty.

WHAT (two removable fogs, both measured in-job — no borrowed calibrations, C4199):
  1. READOUT MITIGATION. Two calibration circuits (prep |0>^8, prep |1>^8) on the SAME pinned 8 qubits
     give per-qubit readout fidelities a_i=P(0|0), b_i=P(1|1). Rigorous per-qubit de-bias of <Z_i>:
     <Z_i>_true = (<Z_i>_raw + b_i - a_i)/(a_i + b_i - 1). (F gets the tensored per-qubit-product
     correction — approximate, so the rigorous claim rides the Neel channel.)
  2. DATA-DRIVEN DEPOLARIZING s. Under global depolarizing every observable scales by the SAME s:
     <Z_i>_meas = s * <Z_i>_ideal. Fit s by regressing ALL mitigated <Z_i> (every init/step/qubit)
     against noiseless -> s_data captures the TOTAL decoherence, not just the 2q-gate model. This is a
     measured fog gauge, not a borrowed rate.

THE TEST. R_defog = mitigated_anomaly / (noiseless_anomaly * s_data). If R_defog -> ~1.0, the fog was
entirely removable/accountable noise and the N=8 scar is intact AT THE NOISELESS LEVEL (the strongest
"scar survives" statement). If R_defog stays < 1, the residual is coherent Trotter error the linear
depolarizing picture cannot absorb -> an honest decomposition of the fog. Secondary: does readout
mitigation lift the F channel to match Neel (proving the F<Neel gap in Exp172 was mundane readout)?

FENCE: pinned single 8-qubit line; tensored (uncorrelated) readout model; s_data assumes global
depolarizing (tested by whether scar and generics share one s). A sharper READ of the Exp172 scar,
not a new claim about the physics.

Usage:
  python3 exp173_scars_n8_defog_ember.py --selftest
  python3 exp173_scars_n8_defog_ember.py --submit [--backend ibm_fez --steps 6 --shots 8000]
  python3 exp173_scars_n8_defog_ember.py --decode --manifest ../results/exp173_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp172_scars_n8_wall_ember as X   # reuse N=8 PXP machinery + inits

N = X.N; DT = X.DT; SCAR_INIT = X.SCAR_INIT; CTRL_INITS = X.CTRL_INITS; INITS = X.INITS


def cal_circuit(prep_ones):
    qc = QuantumCircuit(N, N)
    if prep_ones:
        for q in range(N):
            qc.x(q)
    qc.measure(range(N), range(N))
    return qc


def _counts_to_z_and_F(counts, shots, init):
    z = np.zeros(N); ret = 0
    for bit, c in counts.items():
        b = bit.replace(" ", "")[::-1]
        for i in range(N):
            z[i] += (1 if b[i] == "0" else -1) * c
        if b == init:
            ret += c
    return z / shots, ret / shots


def _readout_fidelities(counts0, counts1, shots):
    """a_i = P(measure 0 | prep 0), b_i = P(measure 1 | prep 1) per qubit, from the two cal circuits."""
    a = np.zeros(N); b = np.zeros(N)
    for bit, c in counts0.items():
        bb = bit.replace(" ", "")[::-1]
        for i in range(N):
            if bb[i] == "0": a[i] += c
    for bit, c in counts1.items():
        bb = bit.replace(" ", "")[::-1]
        for i in range(N):
            if bb[i] == "1": b[i] += c
    return a / shots, b / shots


def _mitigate_z(z_raw, a, b):
    return (z_raw + b - a) / (a + b - 1)


def _mitigate_F(F_raw, init, a, b):
    """Approximate tensored correction: divide by the per-qubit prob the correct bit is read."""
    corr = 1.0
    for i in range(N):
        corr *= (a[i] if init[i] == "0" else b[i])
    return F_raw / corr if corr > 1e-9 else float("nan")


def _stag(z):
    return float(np.mean([((-1) ** i) * z[i] for i in range(N)]))


def _fog_z(i, steps, s_i, a, b):
    """Fabricate a fogged per-qubit <Z_i>: noiseless x s_i (depolarizing) x readout-contraction."""
    from qiskit.quantum_info import Statevector, SparsePauliOp
    sv = Statevector(X.pxp_circuit(i, steps, measure=False)); zz = []
    for k in range(N):
        lbl = ["I"] * N; lbl[N - 1 - k] = "Z"; zz.append(float(np.real(sv.expectation_value(SparsePauliOp("".join(lbl))))))
    return np.array(zz) * s_i * (a + b - 1)


def selftest():
    """Truth-gate on the RELATIVE (non-circular) metric R_rel = s_scar / s_gen — scar's decay vs the
    generic ensemble's, with s fit from each SEPARATELY (advisor C4203: fitting one global s that
    includes the scar makes R=1 a tautology). Two fabricated worlds, both must be flagged correctly:
      (A) pure global depolarizing (scar decays like the pack)  -> R_rel ~ 1.0
      (B) scar-SPECIFIC extra decay (x0.8 on scar only)         -> R_rel ~ 0.8  (< 1: fragility detected)
    If the metric cannot distinguish A from B it cannot detect the thing it exists to detect."""
    steps = 6; a = np.full(N, 0.97); b = np.full(N, 0.97); s0 = 0.4
    for label, scar_extra, expect in (("A: global-dep (no fragility)", 1.0, 1.0),
                                       ("B: scar-specific x0.8 decay", 0.8, 0.8)):
        mit = {}
        for i in INITS:
            s_i = s0 * (scar_extra if i == SCAR_INIT else 1.0)
            mit[i] = _mitigate_z(_fog_z(i, steps, s_i, a, b), a, b)
        s_gen = _fit_s(mit, [steps], CTRL_INITS)
        s_scar = _fit_s(mit, [steps], [SCAR_INIT])
        R_rel = s_scar / s_gen
        print(f"  {label:32s}: s_gen={s_gen:.3f} s_scar={s_scar:.3f}  R_rel={R_rel:.3f} (expect ~{expect})")
        assert abs(R_rel - expect) < 0.05, f"R_rel must flag {label} (~{expect})"
    print("SELFTEST PASS: R_rel = s_scar/s_gen recovers 1.0 for global-dep AND drops to 0.8 for a "
          "scar-specific decay -> non-circular, and it can DETECT scar fragility. Can fail.")


def _fit_s(z_by_init, steps_list, inits):
    """Global depolarizing s = slope of mitigated <Z_i> vs noiseless <Z_i> over the GIVEN inits (fit
    scar and generics SEPARATELY -> non-circular relative metric), steps, qubits with |noiseless|>0.1."""
    from qiskit.quantum_info import Statevector, SparsePauliOp
    xs, ys = [], []
    for i in inits:
        for st in steps_list:
            sv = Statevector(X.pxp_circuit(i, st, measure=False))
            zmit = z_by_init[i] if not isinstance(z_by_init[i], dict) else z_by_init[i][st]
            for k in range(N):
                lbl = ["I"] * N; lbl[N - 1 - k] = "Z"
                znl = float(np.real(sv.expectation_value(SparsePauliOp("".join(lbl)))))
                if abs(znl) > 0.1:
                    xs.append(znl); ys.append(zmit[k])
    xs = np.array(xs); ys = np.array(ys)
    return float(np.sum(xs * ys) / np.sum(xs * xs))     # least-squares slope through origin


def submit(backend_name, steps, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    # pin ALL circuits to the SAME physical qubits as the deepest scar circuit (consistent readout cal)
    probe = transpile(X.pxp_circuit(SCAR_INIT, steps, measure=True), backend=backend, optimization_level=3)
    layout = [probe.layout.final_index_layout()[q] for q in range(N)]
    print(f"pinned physical qubits: {layout}")
    circuits, order = [], []
    for init in INITS:
        for s in range(steps + 1):
            tqc = transpile(X.pxp_circuit(init, s, measure=True), backend=backend,
                            optimization_level=3, initial_layout=layout)
            circuits.append(tqc); order.append([init, s])
    for tag, ones in (("cal0", False), ("cal1", True)):
        tqc = transpile(cal_circuit(ones), backend=backend, optimization_level=1, initial_layout=layout)
        circuits.append(tqc); order.append([tag, -1])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 173, "backend": backend_name, "steps": steps, "shots": shots, "N": N, "dt": DT,
                "scar_init": SCAR_INIT, "ctrl_inits": CTRL_INITS, "layout": layout, "job_id": job.job_id(),
                "order": order,
                "prereg": {"confidence": 0.55,
                           "gate": "R_rel = s_scar/s_gen > 0.85 (scar decays like the generic pack; no scar-specific fragility) AND readout mitigation lifts the F-channel R by more than the Neel R (F<Neel gap was readout)",
                           "note": "CLEAR THE FOG (advisor C4203): independent normalizers only. R_rel fits scar and generics SEPARATELY (non-circular, detects fragility per selftest). Fog DECOMPOSITION: readout-mit lifts F not Neel -> residual is coherent Trotter, not readout. In-job cal, pinned qubits (C4199)."},
                "note": "N=8 scar fog-clear: readout mitigation (pinned qubits, in-job cal) + fog DECOMPOSITION (F-vs-Neel recovery = readout vs coherent) + non-circular fragility R_rel=s_scar/s_gen"}
    out = os.path.join(HERE, "..", "results", "exp173_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = {len(INITS)}x{steps+1} + 2 cal, {shots} shots) -> {out}")


def _price_indep_s(man):
    """INDEPENDENT gate-model survival s = (1-mean_CZ)^n2q on the pinned qubits of the deepest scar
    circuit — a model NOT derived from the anomaly (avoids the R=s/s tautology, advisor C4203)."""
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); job = svc.job(man["job_id"]); props = svc.backend(man["backend"]).properties()
    pubs = job.inputs.get("pubs")
    best = max(pubs, key=lambda p: sum(1 for inst in p[0].data if inst.operation.num_qubits == 2))
    qc = best[0]; cz = sum(1 for inst in qc.data if inst.operation.num_qubits == 2)
    edges = {tuple(sorted(qc.find_bit(bb).index for bb in inst.qubits)) for inst in qc.data if inst.operation.num_qubits == 2}
    errs = [pr.value for (u, v) in edges for g in props.gates
            if g.gate in ("cz", "ecr") and sorted(g.qubits) == sorted([u, v]) for pr in g.parameters if pr.name == "gate_error"]
    return float((1 - np.mean(errs)) ** cz) if errs else float("nan")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    steps = man["steps"]; shots = man["shots"]
    zc = {i: {} for i in INITS}; Fc = {i: {} for i in INITS}; cal = {}
    for idx, (init, s) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]; counts = getattr(r.data, reg).get_counts()
        if init in ("cal0", "cal1"):
            cal[init] = counts; continue
        z, F = _counts_to_z_and_F(counts, shots, init)
        zc[init][s] = z; Fc[init][s] = F
    a, b = _readout_fidelities(cal["cal0"], cal["cal1"], shots)
    print(f"Exp173 decode | job {man['job_id']} | backend {man['backend']} | N={N}")
    print(f"readout fidelities a=P(0|0) mean {a.mean():.3f}, b=P(1|1) mean {b.mean():.3f}")
    zmit = {i: {s: _mitigate_z(zc[i][s], a, b) for s in zc[i]} for i in INITS}
    Fmit = {i: {s: _mitigate_F(Fc[i][s], i, a, b) for s in Fc[i]} for i in INITS}
    nl = {i: X._stag_and_F_exact(i, steps) for i in INITS}
    aMs_nl = abs(nl[SCAR_INIT][0]) - max(abs(nl[c][0]) for c in CTRL_INITS)
    aF_nl = nl[SCAR_INIT][1] - max(nl[c][1] for c in CTRL_INITS)
    s_indep = _price_indep_s(man)                          # INDEPENDENT gate-model s (not from the anomaly)

    def anom(getter):  # scar - max generic at the revival step
        vals = {i: getter(i) for i in INITS}
        return vals[SCAR_INIT] - max(vals[c] for c in CTRL_INITS)
    aMs_raw = anom(lambda i: abs(_stag(zc[i][steps])));  aMs_mit = anom(lambda i: abs(_stag(zmit[i][steps])))
    aF_raw = anom(lambda i: Fc[i][steps]);               aF_mit = anom(lambda i: Fmit[i][steps])
    # ABSOLUTE R with INDEPENDENT s: does readout mitigation lift R above Exp172's 0.58?
    RN_raw, RN_mit = aMs_raw/(aMs_nl*s_indep), aMs_mit/(aMs_nl*s_indep)
    RF_raw, RF_mit = aF_raw/(aF_nl*s_indep),   aF_mit/(aF_nl*s_indep)
    # RELATIVE non-circular fragility: scar's own decay vs the generic ensemble's (s fit SEPARATELY)
    s_gen = _fit_s({i: zmit[i] for i in INITS}, list(range(steps+1)), CTRL_INITS)
    s_scar = _fit_s({i: zmit[i] for i in INITS}, list(range(steps+1)), [SCAR_INIT])
    R_rel = s_scar / s_gen
    print(f"\nINDEPENDENT gate-model s = {s_indep:.3f}")
    print(f"                       RAW anomaly   MITIGATED    R_raw   R_mit   (noiseless)")
    print(f"  Neel (readout-robust)  {aMs_raw:+.3f}       {aMs_mit:+.3f}      {RN_raw:.2f}    {RN_mit:.2f}    ({aMs_nl:+.3f})")
    print(f"  F    (readout-limited) {aF_raw:+.3f}       {aF_mit:+.3f}      {RF_raw:.2f}    {RF_mit:.2f}    ({aF_nl:+.3f})")
    print(f"\nFOG DECOMPOSITION:")
    print(f"  readout mitigation lifts F R by {RF_mit-RF_raw:+.2f}, Neel R by {RN_mit-RN_raw:+.2f}")
    print(f"  -> if F rises toward Neel while Neel barely moves: the F<Neel gap was READOUT (removable);")
    print(f"     the residual (1 - Neel R_mit = {1-RN_mit:.2f}) is COHERENT Trotter/1q/idle error (NOT readout).")
    print(f"\nNON-CIRCULAR fragility  R_rel = s_scar/s_gen = {s_scar:.3f}/{s_gen:.3f} = {R_rel:.2f}")
    print(f"  R_rel ~ 1 => scar decays like the generic pack (no scar-specific fragility); R_rel << 1 => fragile")
    out = {"job_id": man["job_id"], "backend": man["backend"], "N": N,
           "readout_a_mean": float(a.mean()), "readout_b_mean": float(b.mean()), "s_indep": s_indep,
           "neel_anomaly_raw": aMs_raw, "neel_anomaly_mit": aMs_mit, "neel_anomaly_noiseless": aMs_nl,
           "F_anomaly_raw": aF_raw, "F_anomaly_mit": aF_mit, "F_anomaly_noiseless": aF_nl,
           "R_neel_raw": RN_raw, "R_neel_mit": RN_mit, "R_F_raw": RF_raw, "R_F_mit": RF_mit,
           "s_gen": s_gen, "s_scar": s_scar, "R_rel_fragility": R_rel}
    fn = os.path.join(HERE, "..", "results", "exp173_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.steps, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp173_manifest.json"))
    else: ap.print_help()
