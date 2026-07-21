#!/usr/bin/env python3
"""Exp249 (H7-P1) — THE SELF-PRESCRIBING SHIELD (the EMH): diagnose the noise axis same-window,
apply the frozen prescription rule, certify that the prescribed orientation neutralizes what the
mis-prescribed orientation lets through silently.

Geometry (certified in Exp216): the [[4,2,2]] shield is blind to error axes PERPENDICULAR to the
logical readout basis (silent corruption) and TRANSPARENT to the readout's own axis (harmless).
Prescription rule (FROZEN): given diagnosed noise axis n, store/read the logical bit in the n basis.
Refinement vs the H7 plan: the 216 rule grants full IMMUNITY (transparent), not merely detection.

Flight (ibm_fez, 10 pubs x 8000, static, <=3 2q + 1q dressing; reuses exp216.circuit VERBATIM):
  scan_X/Y/Z   = (X-readout, axis, t=0.5)   in-job mini-scan; scan_Z doubles as ALIGNED @ t=0.5
  aligned_25   = (X-readout, Z-axis, 0.25)
  presc_25/50  = (Z-readout, Z-axis, 0.25 / 0.5)   the prescription under the SAME injected noise
  clean_X/Z    = t=0 baselines
  bare_25/50   = single |+> under Rz(theta), X-measure (the noise is real without armor)
FROZEN GATES: G_SCAN A(X,Z,.5)>=0.8 & L(X,Z,.5)>=0.5 & P_sil(X,X,.5)<=0.15 (diagnosis valid
same-window; else NO-DIAGNOSIS, prescription ungraded). G1 L(Z,Z,t)<=0.10 both t AND
L(X,Z,.5)-L(Z,Z,.5) > 5*se. G2 A(Z,Z,.5)>=0.8 (no acceptance tax). G3 bare corruption@pi/2>=0.4.
PASS-PRESCRIPTION = G_SCAN & G1 & G2 & G3. Substrate claude-fable-5, Whisper C4956."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from qiskit import QuantumCircuit
from exp216_blind_spot_locus_rotation import circuit as t216_circuit, _stats, exact

SHOTS = 8000
PUBS = [("scan_X", ("X","X",0.5)), ("scan_Y", ("X","Y",0.5)), ("scan_Z", ("X","Z",0.5)),
        ("aligned_25", ("X","Z",0.25)), ("presc_25", ("Z","Z",0.25)), ("presc_50", ("Z","Z",0.5)),
        ("clean_X", ("X","Z",0.0)), ("clean_Z", ("Z","Z",0.0))]

def bare(t):
    qc = QuantumCircuit(1,1); qc.h(0); qc.rz(t*np.pi, 0); qc.h(0); qc.measure(0,0)
    return qc

def build():
    pubs = [(lab, t216_circuit(*args), SHOTS) for lab, args in PUBS]
    pubs += [("bare_25", bare(0.25), SHOTS), ("bare_50", bare(0.5), SHOTS)]
    return pubs

def grade(counts, out):
    s = {lab: _stats(counts[lab]) for lab, _ in PUBS}
    for lab, _ in PUBS: s[lab]["P_silent"] = s[lab]["A"]*s[lab]["L"]
    b = {}
    for lab in ("bare_25","bare_50"):
        c = counts[lab]; n = sum(c.values())
        b[lab] = sum(v for k,v in c.items() if k.strip()[-1]=="1")/n
    se = lambda st: np.sqrt(max(st["L"]*(1-st["L"]),1e-9)/max(st["n_acc"],1))
    sep = s["scan_Z"]["L"] - s["presc_50"]["L"]
    se_sep = float(np.hypot(se(s["scan_Z"]), se(s["presc_50"])))
    g_scan = s["scan_Z"]["A"]>=0.8 and s["scan_Z"]["L"]>=0.5 and s["scan_X"]["P_silent"]<=0.15
    g1 = s["presc_25"]["L"]<=0.10 and s["presc_50"]["L"]<=0.10 and sep > 5*se_sep
    g2 = s["presc_50"]["A"]>=0.8
    g3 = b["bare_50"]>=0.4
    verdict = ("PASS-PRESCRIPTION" if (g_scan and g1 and g2 and g3)
               else "NO-DIAGNOSIS(scan)" if not g_scan else "NOT-HELD")
    print(f"  SCAN (X-readout, t=0.5): P_silent X={s['scan_X']['P_silent']:.3f} "
          f"Y={s['scan_Y']['P_silent']:.3f} Z={s['scan_Z']['P_silent']:.3f}  -> prescribe Z-basis storage")
    print(f"  ALIGNED  (X-readout under Z-noise): L={s['scan_Z']['L']:.3f}@.5  {s['aligned_25']['L']:.3f}@.25  A={s['scan_Z']['A']:.3f}")
    print(f"  PRESCRIBED (Z-readout under Z-noise): L={s['presc_50']['L']:.3f}@.5  {s['presc_25']['L']:.3f}@.25  A={s['presc_50']['A']:.3f}")
    print(f"  separation L_aligned-L_prescribed = {sep:.3f} ± {se_sep:.4f} ({sep/se_sep:.0f} sigma)   bare corruption@pi/2 = {b['bare_50']:.3f}")
    print(f"  gates: SCAN={g_scan} G1={g1} G2={g2} G3={g3}  VERDICT: {verdict}")
    out.update({"stats": {k: {kk: round(float(vv),4) for kk,vv in v.items()} for k,v in s.items()},
                "bare": {k: round(float(v),4) for k,v in b.items()},
                "separation": round(float(sep),4), "se_sep": round(float(se_sep),5),
                "gates": {"scan": bool(g_scan), "g1": bool(g1), "g2": bool(g2), "g3": bool(g3)},
                "verdict": verdict})
    return verdict

def selftest():
    ex = exact()
    assert ex[("Z","Z",0.5)]["L"] <= 1e-9 and ex[("Z","Z",0.5)]["A"] >= 0.999, "prescription ideal: immune"
    assert ex[("X","Z",0.5)]["L"] >= 0.60 and ex[("X","Z",0.5)]["A"] >= 0.85, "aligned ideal: silent corruption"
    from qiskit_aer import AerSimulator
    from qiskit.quantum_info import Statevector
    sim = AerSimulator()
    counts = {}
    for lab, args in PUBS:
        sv = Statevector(t216_circuit(*args, measured=False))
        counts[lab] = {k: int(round(v*SHOTS)) for k,v in sv.probabilities_dict().items() if v>1e-12}
    for lab, t in (("bare_25",0.25),("bare_50",0.5)):
        p1 = float(np.sin(t*np.pi/2)**2)
        counts[lab] = {"0": int(round((1-p1)*SHOTS)), "1": int(round(p1*SHOTS))}
    out = {}
    v = grade(counts, out)
    assert v == "PASS-PRESCRIPTION", (v, out["gates"])
    print("SELFTEST PASS: ideal counts -> PASS-PRESCRIPTION (aligned L=0.667 silently accepted; "
          "prescribed L=0, A=1; bare 0.5). The closed loop scan->prescribe->verify is well-posed.")

def submit(backend_name):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); backend = svc.backend(backend_name)
    pubs = build()
    circs = [transpile(qc, backend, optimization_level=3, seed_transpiler=17) for _,qc,_ in pubs]
    n2 = [sum(1 for i in c.data if len(i.qubits)==2) for c in circs]
    assert max(n2) <= 8, n2
    print(f"DEPTH CHECK: {len(circs)} pubs, transpiled 2q {min(n2)}-{max(n2)}")
    job = SamplerV2(mode=backend).run([(c,) for c in circs], shots=SHOTS)
    man = {"job_id": job.job_id(), "backend": backend_name, "labels": [l for l,_,_ in pubs]}
    json.dump(man, open(os.path.join(QROOT,"results","exp249_manifest.json"),"w"), indent=1)
    print("handle persisted:", man["job_id"])
    res = job.result()
    counts = {lab: res[i].data.c.get_counts() for i,(lab,_,_) in enumerate(pubs)}
    out = {"job_id": man["job_id"], "backend": backend_name, "substrate": "claude-fable-5"}
    grade(counts, out)
    json.dump({"card": out, "counts": counts},
              open(os.path.join(QROOT,"results","exp249_result.json"),"w"), indent=1, default=float)
    print("card -> results/exp249_result.json")

if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--submit":
        submit(sys.argv[2] if len(sys.argv)>2 else "ibm_fez")
    else:
        selftest()
