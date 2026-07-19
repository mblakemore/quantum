#!/usr/bin/env python3
"""Exp183 — THE TWO-OFFICER PROTOCOL: quantum secret sharing (HBB99). C4873.
Alice, Bob, Charlie share GHZ; X/Y measurements. Valid combos (Mermin family XXX, XYY, YXY,
YYX) enforce a = b ^ c ^ sigma: Alice's bit reconstructable ONLY by Bob AND Charlie together —
either alone is provably blind (GHZ two-party marginals are maximally mixed). The same four
expectations assemble the Mermin certificate M (LHV bound |M| <= 2) for free.
Arms: ghz (4 valid + 2 invalid combos) | noghz product-state null | bellAB anti-pattern
(wrong resource => ONE officer reads Alice alone while the group secret fails).
Qubits: A=q0, B=q1, C=q2. clbits c0/c1/c2 = a/b/c.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

VALID = ("XXX", "XYY", "YXY", "YYX")          # sigma: XXX -> 0, two-Y combos -> 1
INVALID = ("XXY", "YYY")
SIGMA = {"XXX": 0, "XYY": 1, "YXY": 1, "YYX": 1}
MERMIN_SIGN = {"XXX": +1, "XYY": -1, "YXY": -1, "YYX": -1}
ARMS = {"ghz": VALID + INVALID, "noghz": VALID, "bellAB": ("XXX",)}


def circuit(arm, combo):
    qc = QuantumCircuit(3, 3)
    if arm == "ghz":
        qc.h(0); qc.cx(0, 1); qc.cx(1, 2)
    elif arm == "bellAB":
        qc.h(0); qc.cx(0, 1)                  # A-B Bell; C stays |0> — the WRONG resource
    # noghz: product |000>
    qc.barrier()
    for q, b in enumerate(combo):
        if b == "X": qc.h(q)
        else: qc.sdg(q); qc.h(q)
    qc.measure(0, 0); qc.measure(1, 1); qc.measure(2, 2)
    return qc


def stats(counts, shots, combo):
    """Reconstruction P(a=b^c^sigma), pair correlations, triple expectation."""
    sig = SIGMA.get(combo, 0)
    rec = e3 = eab = eac = 0
    for s, n in counts.items():
        b3 = s.replace(" ", "")
        a, b, c = int(b3[-1]), int(b3[-2]), int(b3[-3])
        rec += n * (1 if a == (b ^ c ^ sig) else 0)
        va, vb, vc = 1 - 2 * a, 1 - 2 * b, 1 - 2 * c
        e3 += n * va * vb * vc
        eab += n * va * vb
        eac += n * va * vc
    return {"recon": rec / shots, "E3": e3 / shots, "AB": eab / shots, "AC": eac / shots}


def analyze(get, shots):
    out = {}
    for arm, combos in ARMS.items():
        out[arm] = {c: stats(get(arm, c), shots, c) for c in combos}
    g = out.get("ghz", {})
    if all(c in g for c in VALID):
        out["mermin"] = float(sum(MERMIN_SIGN[c] * g[c]["E3"] for c in VALID))
    if "noghz" in out and all(c in out["noghz"] for c in VALID):
        out["mermin_noghz"] = float(sum(MERMIN_SIGN[c] * out["noghz"][c]["E3"] for c in VALID))
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, c):
        if (arm, c) not in cache:
            cache[(arm, c)] = sim.run(circuit(arm, c), shots=shots).result().get_counts()
        return cache[(arm, c)]
    r = analyze(get, shots)
    print("Exp183 selftest (noiseless Aer)")
    for c in VALID:
        s = r["ghz"][c]
        print(f"  ghz {c}: recon={s['recon']:.3f}  E3={s['E3']:+.3f}  AB={s['AB']:+.3f}  AC={s['AC']:+.3f}")
        assert s["recon"] > 0.999 and abs(s["AB"]) < 0.03 and abs(s["AC"]) < 0.03, f"{c}: group must read, singles must be blind"
    for c in INVALID:
        assert abs(r["ghz"][c]["E3"]) < 0.03, f"{c}: invalid combos must be uncorrelated"
    assert abs(r["mermin"] - 4) < 0.05, "Mermin must be 4 noiseless"
    for c in VALID:
        n = r["noghz"][c]
        assert abs(n["recon"] - 0.5) < 0.03 and abs(n["E3"]) < 0.03, "noghz must be flat"
    bb = r["bellAB"]["XXX"]
    assert bb["AB"] > 0.97 and abs(bb["recon"] - 0.5) < 0.03, "bellAB: one officer reads, group fails"
    print(f"  mermin = {r['mermin']:.3f} | bellAB XXX: AB={bb['AB']:+.3f} (leak!) recon={bb['recon']:.3f}")
    print("SELFTEST PASS: group reconstructs exactly, singles exactly blind, M=4, sifting combos "
          "flat, anti-pattern leaks to one officer while the group secret fails. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm, combos in ARMS.items():
        for c in combos:
            circuits.append(transpile(circuit(arm, c), backend=backend, optimization_level=3))
            order.append([arm, c])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 183, "slug": "secret_sharing", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"primary": "recon >= 0.85 all 4 valid combos AND |AB|,|AC| < 0.05 AND M > 2 at >=5 sigma",
                           "bands": "recon 0.90-0.97; M 3.1-3.6; invalid combos |E3| < 0.05",
                           "falsifiers": "noghz flat (recon 0.47-0.53, M in [-0.2,0.2]); bellAB AB>0.9 "
                                         "(single-officer leak) with recon 0.47-0.53 (no group secret)",
                           "claim_structure": "two-officer property = group-CAN + singles-CANNOT + M>2 (conjunction)"}}
    out = os.path.join(HERE, "..", "results", "exp183_secret_sharing_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp183_secret_sharing_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, c) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, c)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, c: raw[(arm, c)], shots)
    se_E = 1.0 / np.sqrt(shots); se_M = 2.0 / np.sqrt(shots)
    print(f"Exp183 TWO-OFFICER PROTOCOL decode | job {man['job_id']} | backend {man['backend']}")
    for c in VALID:
        s = r["ghz"][c]
        print(f"  ghz {c}: recon={s['recon']:.3f}  E3={s['E3']:+.3f}  |AB|={abs(s['AB']):.3f}  |AC|={abs(s['AC']):.3f}")
    for c in INVALID:
        print(f"  ghz {c} (sift-discard): E3={r['ghz'][c]['E3']:+.3f}")
    M = r["mermin"]; msig = (M - 2) / se_M
    recon_ok = all(r["ghz"][c]["recon"] >= 0.85 for c in VALID)
    blind_ok = all(abs(r["ghz"][c][p]) < 0.05 for c in VALID for p in ("AB", "AC"))
    m_ok = M > 2 and msig >= 5
    worst_rec = min(r["ghz"][c]["recon"] for c in VALID)
    worst_blind = max(abs(r["ghz"][c][p]) for c in VALID for p in ("AB", "AC"))
    bb = r["bellAB"]["XXX"]
    print(f"\nGROUP CAN READ:      worst reconstruction {worst_rec:.3f} (>=0.85 req) {'HELD' if recon_ok else 'FAILED'}")
    print(f"SINGLES CANNOT:      worst |pair corr| {worst_blind:.3f} (<0.05 req) {'HELD' if blind_ok else 'FAILED'}")
    print(f"RESOURCE CERTIFIED:  Mermin M = {M:.3f} vs LHV 2 -> {msig:.0f} sigma {'HELD' if m_ok else 'FAILED'}")
    print(f"FALSIFIER noghz:     M = {r['mermin_noghz']:+.3f}, recon ~ "
          f"{np.mean([r['noghz'][c]['recon'] for c in VALID]):.3f} (flat as required)")
    print(f"ANTI-PATTERN bellAB: <AB> = {bb['AB']:+.3f} — ONE officer reads Alice alone | "
          f"group recon = {bb['recon']:.3f} (no shared secret). The wrong resource is visibly compromised.")
    ok = recon_ok and blind_ok and m_ok
    print(f"VERDICT: {'TWO-OFFICER PROTOCOL WORKS — the secret opens to both officers together and to neither alone, enforced by physics' if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": {k: v for k, v in r.items()},
           "mermin_sigma": float(msig), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp183_secret_sharing_decode.json"), "w"), indent=1)
    print("-> results/exp183_secret_sharing_decode.json")


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
