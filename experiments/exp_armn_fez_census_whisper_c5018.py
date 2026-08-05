#!/usr/bin/env python3
"""ARM-N STEP 1 — fresh FEZ drift census (Whisper C5018, Creator GO general#4711/4712).

The C4998 drifter set is kingston-physical AND 12 days stale; C5002's rule (drifter sets are
epoch-volatile) makes a fresh census on the TARGET chip the mandatory first step of the arm-N
chain. This is that flight: the widesweep twin pads at the census-discriminating depth pair
{160, 280} (reference pattern: drifters collapse 160->280, non-drifters hold), Z-basis only,
plus same-job cal0/cal1 — which doubles as req-2's per-qubit readout profile input for block
selection.

Portability: fez and kingston are both Heron-r2 156q heavy-hex; build_twins transpiles with
the frozen race_n40 layout in index space and its CZ-only assert guards structure. The census
DISCOVERS fez's current drifters (per-qubit |<Z>| excess decay vs the register median) rather
than assuming kingston's.

Outputs (decode): per-qubit |<Z>|_160, |<Z>|_280, decay excess vs median, drifter ranking with
sigma margins; per-qubit readout e0/e1 from the in-job cal (req-2 input). Block selection and
the compile asserts are STEP 2, driven by this artifact.
"""
import json, os, sys, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

from exp_crossblock_widesweep import build_twins, SEED, NPHYS

BACKEND = "ibm_fez"
ACCOUNT = "IBMQ_ALT2"
DEPTHS = [160, 280]
SHOTS = 8000


def submit():
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    svc = service_for_submission(ACCOUNT)
    u = svc.usage()
    print(f"POOL ({ACCOUNT}): {u['usage_remaining_seconds']}s remaining (re-read at submission)")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    cal = str(props.last_update_date)
    print(f"{BACKEND} cal epoch: {cal}")
    twins, active = build_twins(backend)
    print(f"[build] twin register {len(active)} active qubits on {BACKEND}")
    pubs, meta = [], []
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, SHOTS))
        meta.append({"block": tag, "shots": SHOTS})
    for D in DEPTHS:
        qc = twins[D].copy()
        qc.measure_all()
        tqc = transpile(qc, backend, optimization_level=0,
                        initial_layout=list(range(NPHYS)), seed_transpiler=SEED)
        d2q = sum(1 for i in tqc.data if i.operation.num_qubits == 2)
        assert d2q > 0, f"pad-cancel at depth {D}"
        pubs.append((tqc, None, SHOTS))
        meta.append({"block": f"d{D}_Z", "depth": D, "shots": SHOTS})
    job = SamplerV2(mode=backend).run(pubs)
    man = {"card": "armn_fez_census", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch": cal,
           "depths": DEPTHS, "register": active, "seed": SEED,
           "go": "Creator general#4711 'Go' (G4) -> #4712 chain",
           "purpose": "arm-N step 1: discover fez's CURRENT drifters + req-2 readout profiles",
           "pubs_meta": meta, "job_id": job.job_id(),
           "submit_iso": datetime.datetime.now(datetime.UTC).isoformat()}
    path = os.path.join(RES, f"armn_fez_census_manifest_{job.job_id()}.json")
    json.dump(man, open(path, "w"), indent=1)
    print(f"SUBMITTED {job.job_id()} -> {path}")


def decode(jid):
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(jid)
    job = svc.job(jid)
    res = job.result()
    man = json.load(open(os.path.join(RES, f"armn_fez_census_manifest_{jid}.json")))
    reg = man["register"]

    def marg(i, q):
        c = res[i].data.meas.get_counts()
        tot = sum(c.values()); s = 0
        for bs, n in c.items():
            if bs.replace(" ", "")[::-1][q] == "1":
                s += n
        return s / tot, tot

    e0 = {q: marg(0, q)[0] for q in reg}
    e1 = {q: 1.0 - marg(1, q)[0] for q in reg}
    rows = {}
    for i, m in enumerate(man["pubs_meta"]):
        if m["block"].startswith("d"):
            D = m["depth"]
            for q in reg:
                p1, tot = marg(i, q)
                den = 1 - e0[q] - e1[q]
                if abs(den) < 1e-6:
                    continue
                p1c = min(max((p1 - e0[q]) / den, 0), 1)
                z = abs(1 - 2 * p1c)
                sig = 2 * np.sqrt(p1 * (1 - p1) / tot) / abs(den)
                rows.setdefault(q, {})[D] = (round(z, 4), round(sig, 4))
    # decay excess vs register median
    d0, d1 = man["depths"]
    decays = {q: rows[q][d0][0] - rows[q][d1][0] for q in rows if d0 in rows[q] and d1 in rows[q]}
    med = float(np.median(list(decays.values())))
    out = {"card": "armn_fez_census_DECODE", "job": jid, "cal_epoch": man["cal_epoch"],
           "readout": {str(q): {"e0": round(e0[q], 5), "e1": round(e1[q], 5)} for q in reg},
           "zrows": {str(q): {str(D): rows[q][D] for D in rows[q]} for q in rows},
           "median_decay": round(med, 4), "drifter_ranking": []}
    for q in sorted(decays, key=lambda q: -(decays[q] - med)):
        ex = decays[q] - med
        s0, s1 = rows[q][d0][1], rows[q][d1][1]
        sig = float(np.hypot(s0, s1))
        out["drifter_ranking"].append({"q": q, "excess": round(ex, 4),
                                       "sigma": round(sig, 4),
                                       "margin": round(ex / sig, 1) if sig > 0 else None})
    path = os.path.join(RES, f"armn_fez_census_decode_{jid}.json")
    json.dump(out, open(path, "w"), indent=1)
    top = [r for r in out["drifter_ranking"] if r["margin"] and r["margin"] >= 3]
    print(f"median decay {med:.4f}; drifters (excess >=3sigma): " +
          ", ".join(f"q{r['q']}(+{r['excess']:.3f},{r['margin']}s)" for r in top[:8]))
    print(f"-> {path}")


if __name__ == "__main__":
    if "--decode" in sys.argv:
        decode(sys.argv[sys.argv.index("--decode") + 1])
    else:
        submit()
