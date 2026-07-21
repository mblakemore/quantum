#!/usr/bin/env python3
"""Exp247 (H7-P7, REDESIGNED) — THE ADAPTIVE HELM, static form: does T1-aware memory decoding beat
memoryless decoding at BALANCED accuracy on live syndrome streams?

Redesign per finding-exp241c: the in-circuit rules were killed offline; the T1-aware ML decoder won
0.82-vs-0.53 offline BUT only on |1_L> data (one-class caveat). This flight closes it: encode BOTH
|0_L>=|000> and |1_L>=|111>, run R rounds of syndrome extraction with NO feed-forward (static — no
dynamic-circuit risk), decode OFFLINE (how production QEC decoders work), grade BALANCED accuracy.
Bonus: the |0_L> arm isolates the re-excitation rate p01 — never measured in this campaign.

Pubs: 2 classes x R in {2,3,4} + 2 readout cals = 8 x 8,000 shots, ibm_fez, tau=30us/round (241-match).
Decoders (frozen here, before data): D0 majority | M frame-replayed memoryless (CORR map of 241) |
ML_T1 asymmetric HMM, params grid-fit on the train half (even shots, both classes), all decoders
evaluated on the held-out test half (odd shots) only.
Substrate claude-fable-5, Whisper C4954. Pre-reg frozen separately pre-submit."""
import os, sys, json
import numpy as np
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(QROOT, "tools"))
from qiskit import QuantumCircuit
from qiskit.circuit import ClassicalRegister
from exp241c_offline_decoders import syn_of, CORR
from exp241c_t1_ml import loglik_t1

SHOTS = 8000
TAU_US = 30
ROUNDS = (2, 3, 4)

def circuit(enc, R):
    from qiskit.circuit import QuantumRegister
    d = QuantumRegister(3, "d"); a = QuantumRegister(2, "a")
    syns = [ClassicalRegister(2, f"syn{r}") for r in range(R)]
    out = ClassicalRegister(3, "out")
    qc = QuantumCircuit(d, a, *syns, out)
    if enc == 1:
        qc.x(d[0])
    qc.cx(d[0], d[1]); qc.cx(d[1], d[2])
    for r in range(R):
        qc.barrier()
        qc.delay(TAU_US, unit="us")
        qc.cx(d[0], a[0]); qc.cx(d[1], a[0])
        qc.cx(d[1], a[1]); qc.cx(d[2], a[1])
        qc.measure(a[0], syns[r][0]); qc.measure(a[1], syns[r][1])
        qc.reset(a[0]); qc.reset(a[1])
    qc.barrier()
    for i in range(3):
        qc.measure(d[i], out[i])
    return qc

def build():
    pubs = [(f"e{enc}_R{R}", circuit(enc, R), SHOTS) for enc in (0, 1) for R in ROUNDS]
    for lab, enc in (("cal0", 0), ("cal1", 1)):
        qc = QuantumCircuit(3, 3)
        if enc: [qc.x(q) for q in range(3)]
        [qc.measure(q, q) for q in range(3)]
        pubs.append((lab, qc, SHOTS))
    return pubs

# ---------------- frozen offline decoders + grading ----------------

def _records(databin, R):
    recs = [np.array([int(b, 2) for b in getattr(databin, f"syn{r}").get_bitstrings()]) for r in range(R)]
    out = np.array([int(b, 2) for b in databin.out.get_bitstrings()])
    return recs, out

def _maj(o):  # majority-decoded logical value of a 3-bit readout
    return 1 if bin(o).count("1") >= 2 else 0

def dec_majority(recs, out, enc):
    return np.array([_maj(o) == enc for o in out])

def dec_memoryless(recs, out, enc):
    R, n = len(recs), len(out)
    ok = np.zeros(n, bool)
    for s in range(n):
        f = 0
        for r in range(R):
            f ^= CORR[recs[r][s] ^ syn_of(f)]
        ok[s] = _maj(out[s] ^ f) == enc
    return ok

def dec_ml(recs, out, enc_true, params):
    n = len(out); ok = np.zeros(n, bool)
    for s in range(n):
        l1 = loglik_t1([rc[s] for rc in recs], out[s], 1, *params)
        l0 = loglik_t1([rc[s] for rc in recs], out[s], 0, *params)
        ok[s] = (1 if l1 >= l0 else 0) == enc_true
    return ok

def grade(get_records, out_card):
    """get_records(label) -> (recs, out). Frozen rule: PASS if BA(ML)-BA(M) > 0 with pooled McNemar
    z > 5 at BOTH R=3 and R=4 on the test half. Reported always: class-conditional accuracies (the
    bias check), R=2 row, fitted params incl. re-excitation p01."""
    results = {}
    verdict_terms = []
    for R in ROUNDS:
        data = {enc: get_records(f"e{enc}_R{R}") for enc in (0, 1)}
        n = len(data[0][1]); test = np.arange(n) % 2 == 1; train = ~test
        # fit on train half, both classes pooled (supervised decoder calibration)
        rng = np.random.RandomState(2)
        pool = np.where(train)[0]
        sub = {e: rng.choice(pool, size=min(250, len(pool)), replace=False) for e in (0, 1)}
        best, bp = -np.inf, None
        for p10, p01, q, rf in product((0.08, 0.14, 0.22), (0.003, 0.01, 0.03, 0.08),
                                       (0.05, 0.10, 0.18), (0.02, 0.05, 0.10)):
            ll = 0.0
            for e in (0, 1):
                recs, out = data[e]
                ll += sum(loglik_t1([rc[s] for rc in recs], out[s], e, p10, p01, q, rf) for s in sub[e])
            if ll > best: best, bp = ll, (p10, p01, q, rf)
        row = {"params(p10,p01,q,rf)": bp}
        accs = {}
        for name, fn in (("majority", dec_majority), ("memoryless", dec_memoryless),
                         ("ML_T1", lambda r, o, e: dec_ml(r, o, e, bp))):
            per = {e: fn(*data[e], e) for e in (0, 1)}
            accs[name] = per
            row[name] = {"acc_e0": round(float(per[0][test].mean()), 4),
                         "acc_e1": round(float(per[1][test].mean()), 4),
                         "balanced": round(float(np.mean([per[e][test].mean() for e in (0, 1)])), 4)}
        # pooled paired McNemar ML vs memoryless on test half
        b01 = sum(int((~accs["memoryless"][e][test] & accs["ML_T1"][e][test]).sum()) for e in (0, 1))
        b10 = sum(int((accs["memoryless"][e][test] & ~accs["ML_T1"][e][test]).sum()) for e in (0, 1))
        z = (b01 - b10) / np.sqrt(b01 + b10) if (b01 + b10) > 0 else 0.0
        dBA = row["ML_T1"]["balanced"] - row["memoryless"]["balanced"]
        row.update({"mcnemar(+,-)": [b01, b10], "z": round(float(z), 2), "dBA": round(float(dBA), 4)})
        results[f"R{R}"] = row
        if R in (3, 4):
            verdict_terms.append(dBA > 0 and z > 5)
        print(f"R={R}: params={bp}  " + "  ".join(
            f"{k}: e0={row[k]['acc_e0']} e1={row[k]['acc_e1']} BA={row[k]['balanced']}"
            for k in ("majority", "memoryless", "ML_T1")))
        print(f"      dBA(ML-M)={dBA:+.4f}  McNemar {b01}/{b10}  z={z:+.2f}")
    verdict = "MEMORY-DECODER-CERTIFIED" if all(verdict_terms) else "NOT-HELD(balanced)"
    print(f"VERDICT: {verdict}  (rule: dBA>0 AND z>5 at BOTH R=3 and R=4, test half)")
    out_card.update({"rounds": results, "verdict": verdict})
    return verdict

def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    from qiskit import transpile
    counts_ok = True
    def get_records_factory(shots=400):
        store = {}
        def get(label):
            enc, R = int(label[1]), int(label[-1])
            qc = transpile(circuit(enc, R), sim)
            res = sim.run(qc, shots=shots).result().get_counts()
            # expand counts to per-shot arrays (noiseless: single outcome)
            recs = [np.zeros(shots, dtype=int) for _ in range(R)]
            outv = np.zeros(shots, dtype=int)
            i = 0
            for k, v in res.items():
                parts = k.split()  # 'out synR-1 ... syn0'
                o = int(parts[0], 2); syns = [int(x, 2) for x in parts[::-1][:R]]
                for _ in range(v):
                    for r in range(R): recs[r][i] = syns[r]
                    outv[i] = o; i += 1
            return recs, outv
        return get
    out = {}
    v = grade(get_records_factory(), out)
    for R in ROUNDS:
        for k in ("majority", "memoryless", "ML_T1"):
            assert out["rounds"][f"R{R}"][k]["balanced"] > 0.999, (R, k, out["rounds"][f"R{R}"][k])
    print("SELFTEST PASS: noiseless sim — all three decoders perfect on BOTH classes at all R;")
    print("grader wiring (registers, replay, HMM, balanced metric) verified end-to-end. Hardware decides.")

def submit(backend_name):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); backend = svc.backend(backend_name)
    pubs = build()
    circs = [transpile(qc, backend, optimization_level=3, seed_transpiler=13) for _, qc, _ in pubs]
    n2 = [sum(1 for i in c.data if len(i.qubits) == 2) for c in circs]
    assert max(n2) <= 32, n2  # C4954b: d1 needs degree-4 -> routing unavoidable on heavy-hex (241 paid the same); wall guard is 40
    print(f"DEPTH CHECK: {len(circs)} pubs, transpiled 2q {min(n2)}-{max(n2)}")
    job = SamplerV2(mode=backend).run([(c,) for c in circs], shots=SHOTS)
    man = {"job_id": job.job_id(), "backend": backend_name, "labels": [l for l, _, _ in pubs]}
    json.dump(man, open(os.path.join(QROOT, "results", "exp247_manifest.json"), "w"), indent=1)
    print("handle persisted:", man["job_id"])
    res = job.result()
    idx = {lab: i for i, (lab, _, _) in enumerate(pubs)}
    def get(label):
        enc, R = int(label[1]), int(label[-1])
        return _records(res[idx[label]].data, R)
    out = {"job_id": man["job_id"], "backend": backend_name, "substrate": "claude-fable-5",
           "tau_us": TAU_US, "shots": SHOTS}
    grade(get, out)
    # persist raw streams compactly for archival + future re-analysis (the 241b rule)
    raw = {}
    for lab, _, _ in pubs:
        if lab.startswith("cal"):
            raw[lab] = res[idx[lab]].data.c.get_counts()
        else:
            enc, R = int(lab[1]), int(lab[-1])
            recs, o = _records(res[idx[lab]].data, R)
            raw[lab] = {"syn": [r.tolist() for r in recs], "out": o.tolist()}
    json.dump({"card": out, "raw": raw}, open(os.path.join(QROOT, "results", "exp247_result.json"), "w"))
    print("card -> results/exp247_result.json")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--submit":
        submit(sys.argv[2] if len(sys.argv) > 2 else "ibm_fez")
    else:
        selftest()
