#!/usr/bin/env python3
"""Exp251 (H7-P3) — THE PATTERN BUFFER: teleport a state INTO a live-corrected memory and show the
memory protects it during the hold. Composes two certified H6 pieces never before chained:
teleportation (Pauli-frame deferral, Exp177) + the repeated-rounds QEC loop (Exp241).

STATIC + offline decode (the Exp247 lesson): teleport source->d0 with the Bell-frame DEFERRED to
post-processing; encode d0 into the bit-flip memory (d0,d1,d2); hold R rounds of syndrome extraction
(NO in-circuit feed-forward) with real idle tau; decode OFFLINE (majority QEC correction + teleport
frame); read logical Z of the teleported |1> (the T1-sensitive state — T1 decay |1>->|0> is a bit flip
the code corrects). PD-1 verified: pipeline+frame recover |1> exactly (1.000) with no noise.

Arms: tp_corr_R{2,3} (teleport+corrected memory) | tp_bare_R{2,3} (teleport, hold d0 bare, same idle) |
direct_corr_R3 (no teleport, isolates its cost) | tp_immediate (R=0 seam). 8 pubs x 8000, tau=30us.
CLAIM: F(tp_corr,R=3) > F(tp_bare,R=3) + 5se AND seam bounded (tp_immediate F>0.9).
Substrate claude-opus-4-8, Whisper C4961."""
import os, sys, json
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
SHOTS = 8000; TAU_US = 30

def buffer_circuit(R, teleport=True, encode=True, storm_p=0.0):
    s = QuantumRegister(1, "s"); b = QuantumRegister(2, "b"); dd = QuantumRegister(2, "dd")
    a = QuantumRegister(2, "a")
    ms = ClassicalRegister(2, "m"); out = ClassicalRegister(3, "o")
    syn = [ClassicalRegister(2, f"s{r}") for r in range(R)]
    qc = QuantumCircuit(s, b, a, dd, *syn, out, ms)
    d = [b[1], dd[0], dd[1]]
    if teleport:
        qc.x(s[0]); qc.h(b[0]); qc.cx(b[0], b[1])
        qc.cx(s[0], b[0]); qc.h(s[0])
        qc.measure(s[0], ms[0]); qc.measure(b[0], ms[1])
    else:
        qc.x(b[1])
    if encode:
        qc.cx(d[0], d[1]); qc.cx(d[0], d[2])
        hold = d
    else:
        hold = [d[0]]
    ang = 2 * np.arcsin(np.sqrt(storm_p)) if storm_p > 0 else 0.0
    for r in range(R):
        if storm_p > 0:
            for q in hold: qc.rx(ang, q)
        else:
            for q in hold: qc.delay(TAU_US, unit="us")
        if encode:
            qc.cx(d[0], a[0]); qc.cx(d[1], a[0]); qc.cx(d[1], a[1]); qc.cx(d[2], a[1])
            qc.measure(a[0], syn[r][0]); qc.measure(a[1], syn[r][1]); qc.reset(a[0]); qc.reset(a[1])
    if encode:
        for i in range(3): qc.measure(d[i], out[i])
    else:
        qc.measure(d[0], out[0])
    return qc

PUBS = [("tp_corr_R2", dict(R=2)), ("tp_corr_R3", dict(R=3)),
        ("tp_bare_R2", dict(R=2, encode=False)), ("tp_bare_R3", dict(R=3, encode=False)),
        ("direct_corr_R3", dict(R=3, teleport=False)), ("tp_immediate", dict(R=0))]

def _fid_from_counts(counts, R, teleport, encode):
    good = 0; n = 0
    for key, c in counts.items():
        regs = key.split()                       # qiskit: ms, out, s{R-1}..s0
        ms = regs[0]; out = regs[1]
        if encode:
            maj = 1 if out.count("1") >= 2 else 0
        else:
            maj = int(out.replace(" ", "")[-1])
        if teleport:
            maj ^= int(ms[0])                     # X-bar frame (ms = 'm1 m0')
        good += c * (1 if maj == 1 else 0); n += c
    return good / n

def grade(counts_by_label, out):
    F = {}
    for lab, kw in PUBS:
        R = kw.get("R", 0); tp = kw.get("teleport", True); en = kw.get("encode", True)
        F[lab] = _fid_from_counts(counts_by_label[lab], R, tp, en)
    se = lambda p, n=SHOTS: float(np.sqrt(max(p*(1-p), 1e-6)/n))
    sep = F["tp_corr_R3"] - F["tp_bare_R3"]
    se_sep = float(np.hypot(se(F["tp_corr_R3"]), se(F["tp_bare_R3"])))
    g_compose = sep > 5 * se_sep
    g_seam = F["tp_immediate"] > 0.90
    verdict = "PATTERN-BUFFER-CERTIFIED" if (g_compose and g_seam) else (
        "SEAM-FAIL" if not g_seam else "NO-ADVANTAGE(corrected<=bare)")
    print(f"  seam (tp_immediate, R=0): F={F['tp_immediate']:.4f} (>0.90) -> {g_seam}")
    print(f"  R2: tp_corr={F['tp_corr_R2']:.4f} tp_bare={F['tp_bare_R2']:.4f}")
    print(f"  R3: tp_corr={F['tp_corr_R3']:.4f} tp_bare={F['tp_bare_R3']:.4f}  sep={sep:+.4f} ({sep/se_sep:.1f}s) -> {g_compose}")
    print(f"  direct_corr_R3 (no teleport)={F['direct_corr_R3']:.4f}  teleport cost={F['direct_corr_R3']-F['tp_corr_R3']:+.4f}")
    print(f"  VERDICT: {verdict}")
    out.update({"F": {k: round(float(v), 4) for k, v in F.items()},
                "sep_R3": round(float(sep), 4), "se_sep": round(float(se_sep), 5),
                "gates": {"compose": bool(g_compose), "seam": bool(g_seam)}, "verdict": verdict})
    return verdict

def selftest():
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    sim = AerSimulator()
    # noiseless: pipeline+frame must recover |1> exactly
    counts = {}
    for lab, kw in PUBS:
        qc = buffer_circuit(**kw); counts[lab] = sim.run(transpile(qc, sim), shots=8000).result().get_counts()
    out = {}; grade(counts, out)
    assert out["F"]["tp_immediate"] > 0.99 and out["F"]["tp_corr_R3"] > 0.99, "noiseless pipeline must be ~1"
    print("  [noiseless: pipeline+frame exact]")
    # storm proxy: corrected must beat bare (logic check)
    counts2 = {}
    for lab, kw in PUBS:
        qc = buffer_circuit(**{**kw, "storm_p": 0.15}); counts2[lab] = sim.run(transpile(qc, sim), shots=8000).result().get_counts()
    out2 = {}; v2 = grade(counts2, out2)
    assert v2 == "PATTERN-BUFFER-CERTIFIED", (v2, out2["gates"])
    print("SELFTEST PASS: noiseless pipeline exact; under a bit-flip storm the corrected buffer beats bare -> logic sound. Hardware T1 decides.")

def submit(backend_name):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); backend = svc.backend(backend_name)
    circs, labels = [], []
    for lab, kw in PUBS:
        qc = buffer_circuit(**kw)
        circs.append(transpile(qc, backend, optimization_level=1, seed_transpiler=23, scheduling_method="asap"))
        labels.append(lab)
    n2 = [sum(1 for i in c.data if len(i.qubits) == 2) for c in circs]
    assert max(n2) <= 40, n2
    print(f"DEPTH CHECK: {len(circs)} pubs, transpiled 2q {min(n2)}-{max(n2)}")
    job = SamplerV2(mode=backend).run([(c,) for c in circs], shots=SHOTS)
    man = {"job_id": job.job_id(), "backend": backend_name, "labels": labels}
    json.dump(man, open(os.path.join(QROOT, "results", "exp251_manifest.json"), "w"), indent=1)
    print("handle persisted:", man["job_id"])
    res = job.result()
    def cts(i):
        d = res[i].data
        # join all classical registers in qiskit print order: ms, o, s{R-1}..s0
        regs = [r for r in dir(d) if not r.startswith("_") and r not in ("keys",)]
        return res[i].join_data().get_counts() if hasattr(res[i], "join_data") else _joincounts(d)
    counts = {}
    for i, lab in enumerate(labels):
        counts[lab] = _joincounts(res[i].data)
    out = {"job_id": man["job_id"], "backend": backend_name, "substrate": "claude-opus-4-8", "tau_us": TAU_US}
    grade(counts, out)
    json.dump({"card": out, "counts": counts}, open(os.path.join(QROOT, "results", "exp251_result.json"), "w"), indent=1, default=float)
    print("card -> results/exp251_result.json")

def _joincounts(databin):
    # reproduce space-separated multi-register key: ms o s{R-1}..s0 (qiskit convention: reverse add order)
    names = [n for n in databin.__dict__ if not n.startswith("_")]
    order = ["m", "o"] + sorted([n for n in names if n.startswith("s") and n != "s"],
                                key=lambda x: int(x[1:]), reverse=True)
    order = [n for n in order if n in names]
    bitarrays = {n: getattr(databin, n).get_bitstrings() for n in order}
    shots = len(next(iter(bitarrays.values())))
    from collections import Counter
    keys = [" ".join(bitarrays[n][s] for n in order) for s in range(shots)]
    return dict(Counter(keys))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--submit":
        submit(sys.argv[2] if len(sys.argv) > 2 else "ibm_fez")
    else:
        selftest()
