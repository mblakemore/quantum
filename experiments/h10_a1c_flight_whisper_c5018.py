#!/usr/bin/env python3
"""H10-A1c FLIGHT — quorum fact with context-priced custody + the context-cost gate
(Whisper C5018). Prereg: docs/h10-a1c-prereg-whisper-c5018.md (frozen at seal request).
GO on record: Creator direct 2026-08-02 "run A1c". Flies on Ember seal.

Imports the A1b module (which imports A1): encode, decoders, iterators, graders,
cx_graph, pub_stats, dial_of — nothing re-typed. New here: 6 SCTX pubs (codeword v0 +
per-seed scramble = the context-matched custody floor), per-seed G4b bars, the B
context-cost gate, G2 absolute re-derived to 0.780 (sealed).

SEALED CONSTANTS (prereg §4): G1a 0.10 · G1b max(floor−3se−0.030, 0.700) · G2 0.780 ·
G3 0.950 · G4a 0.10 · G4b max(floor_ctx(seed)−3se−0.030, 0.650) · G5 0.820 · B ±2se ·
boundary 2 · depth HOLD 100 · cal HOLD 0.5% · e2e KA: A=HOLDS, B=UNDERPOWERED.
"""
import hashlib, importlib.util, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
RESULTS = os.path.join(HERE, "..", "results")
DOCS = os.path.join(HERE, "..", "docs")

_spec = importlib.util.spec_from_file_location(
    "a1b", os.path.join(HERE, "h10_a1b_flight_whisper_c5018.py"))
a1b = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(a1b)
a1 = a1b.a1

GO_REF = "Creator direct 2026-08-02 'run A1c'"
PREREG = os.path.join(DOCS, "h10-a1c-prereg-whisper-c5018.md")
FREEZE_SHA12 = "1fe4b5eb9331"   # frozen at seal request (text freezes at the request post)
SEAL_REF = None                 # set to Ember's seal post; fly() refuses until then

def assert_freeze():
    h = hashlib.sha256(open(PREREG, "rb").read()).hexdigest()
    if FREEZE_SHA12 is not None:
        assert h.startswith(FREEZE_SHA12), f"PREREG FROZEN-TEXT MISMATCH: {h[:12]}"
    return h

CAP, BAR_REV, BAR_STORY = 0.10, 0.950, 0.820
CTRL_ABS = 0.780                                  # G2 re-derived pre-data (Elder #3883)
ALLOW_PAIR, BACKSTOP_PAIR = 0.030, 0.700
ALLOW_CTX, BACKSTOP_CTX = 0.030, 0.650            # G4b: context in the floor now
SHOTS = {"dial": 3000, "rc": 3000, "sctx": 1500, "rev": 2000, "scr": 1500, "story": 4000}

def build_pubs():
    from qiskit import QuantumCircuit
    g = a1b.cx_graph()
    pubs = []
    def finish(qc, kind, name, shots, **kw):
        qc.measure(range(7), range(7))
        pubs.append({"kind": kind, "name": name, "shots": shots, "qc": qc, **kw})
    for b in (0, 1):
        qc = QuantumCircuit(7, 7)
        if b: qc.x(0)
        a1.encode_threshold(qc)
        finish(qc, "dial", f"T_b{b}", SHOTS["dial"], b=b, map="T")
    for vname, s1 in (("C0", 0), ("C1", 3)):
        for b in (0, 1):
            qc = QuantumCircuit(7, 7)
            if b: qc.x(0)
            if s1 & 2: qc.x(1)
            if s1 & 1: qc.x(2)
            qc.compose(g, inplace=True)
            finish(qc, "dial", f"{vname}_b{b}", SHOTS["dial"], b=b, map=vname)
    qc = QuantumCircuit(7, 7); qc.h(0); qc.compose(g, inplace=True)
    finish(qc, "rc", "RC_pair12dial", SHOTS["rc"])
    # SCTX: the context-matched custody floor — codeword v0 + that seed's ACTUAL scramble
    for seed in a1.SEEDS:
        for b in (0, 1):
            qc = QuantumCircuit(7, 7)
            if b: qc.x(0)
            qc.compose(g, inplace=True)
            qc.append(a1.scramble_gate(seed), [5, 6])
            finish(qc, "dial", f"SCTX{seed}_b{b}", SHOTS["sctx"], b=b, map=f"SCTX{seed}")
    qc = QuantumCircuit(7, 7); qc.h(0); a1.encode_threshold(qc)
    e = QuantumCircuit(7); a1.encode_threshold(e)
    qc.compose(e.inverse(), inplace=True); qc.h(0)
    finish(qc, "rev", "A3_revival", SHOTS["rev"])
    for seed in a1.SEEDS:
        qc = QuantumCircuit(7, 7); qc.h(0); a1.encode_threshold(qc)
        qc.append(a1.scramble_gate(seed), [5, 6]); qc.h(0)
        finish(qc, "scr_d", f"SCR{seed}_Dcontrast", SHOTS["scr"], seed=seed)
        qc = QuantumCircuit(7, 7); qc.h(0); a1.encode_threshold(qc)
        qc.append(a1.scramble_gate(seed), [5, 6])
        finish(qc, "scr_pair", f"SCR{seed}_pair12dial", SHOTS["scr"], seed=seed)
    qc = QuantumCircuit(7, 7); qc.h(0); a1.encode_threshold(qc)
    for q in range(7): qc.h(q)
    finish(qc, "story", "A5_story", SHOTS["story"])
    assert len(pubs) == 21 and sum(p["shots"] for p in pubs) == 45000
    return pubs

def grade(stats):
    """COMPLETE post-counts decode -> verdicts A and B. One code path, KA'd e2e."""
    out = {"experiment": "h10_a1c_quorum_fact_context_priced", "dials": {}, "floors": {},
           "bars": {}, "gates": {}}
    maps = ["T", "C0", "C1"] + [f"SCTX{s}" for s in a1.SEEDS]
    for m in maps:
        for c in a1b.COALS:
            k = a1.coal_name(c)
            d, se = a1b.dial_of(stats[f"{m}_b0"], stats[f"{m}_b1"], k)
            out["dials"][f"{m}_{k}"] = {"dial": d, "se": se}
    for pr in a1b.PAIRS:                            # G1b floors from C0/C1 (as A1b)
        k = a1.coal_name(pr)
        f = (out["dials"][f"C0_{k}"]["dial"] + out["dials"][f"C1_{k}"]["dial"]) / 2
        se = float(np.sqrt(out["dials"][f"C0_{k}"]["se"] ** 2
                           + out["dials"][f"C1_{k}"]["se"] ** 2) / 2)
        out["floors"][k] = {"floor": f, "se": se}
        out["bars"][f"pair_{k}"] = max(f - 3 * se - ALLOW_PAIR, BACKSTOP_PAIR)
    rc = stats["RC_pair12dial"]
    floor_plain = 2 * rc["p"] - 1; se_plain = 2 * rc["se_p"]
    out["floors"]["rec_plain"] = {"floor": floor_plain, "se": se_plain}
    for seed in a1.SEEDS:                           # per-seed context floors + bars
        fc = out["dials"][f"SCTX{seed}_s1s2"]
        out["floors"][f"ctx{seed}"] = {"floor": fc["dial"], "se": fc["se"]}
        out["bars"][f"custody{seed}"] = max(fc["dial"] - 3 * fc["se"] - ALLOW_CTX,
                                            BACKSTOP_CTX)
    g1a = [a1.three_state(out["dials"][f"T_s{i}"]["dial"], CAP,
                          out["dials"][f"T_s{i}"]["se"], "<=") for i in (1, 2, 3)]
    g1b = [a1.three_state(out["dials"][f"T_{a1.coal_name(pr)}"]["dial"],
                          out["bars"][f"pair_{a1.coal_name(pr)}"],
                          out["dials"][f"T_{a1.coal_name(pr)}"]["se"], ">=")
           for pr in a1b.PAIRS]
    g2 = [a1.three_state(out["dials"][f"{m}_{a1.coal_name(pr)}"]["dial"], CTRL_ABS,
                         out["dials"][f"{m}_{a1.coal_name(pr)}"]["se"], ">=")
          for m in ("C0", "C1") for pr in a1b.PAIRS]
    rev = stats["A3_revival"]
    g3 = [a1.three_state(rev["contrast"], BAR_REV, rev["se"], ">=")]
    g4a, g4b = [], []
    for seed in a1.SEEDS:
        dc = stats[f"SCR{seed}_Dcontrast"]
        pd = stats[f"SCR{seed}_pair12dial"]
        g4a.append(a1.three_state(abs(dc["contrast"]), CAP, dc["se"], "<="))
        g4b.append(a1.three_state(2 * pd["p"] - 1, out["bars"][f"custody{seed}"],
                                  2 * pd["se_p"], ">="))
    st = stats["A5_story"]
    g5 = [a1.three_state(st["sorted_absX"], BAR_STORY, st["se_sorted"], ">=")]
    receipt = abs(st["unsorted_X"]) <= 3 * st["se_unsorted"]
    for name, subs in (("G1a_blindness", g1a), ("G1b_pair_read", g1b),
                       ("G2_control_abs", g2), ("G3_revival", g3),
                       ("G4a_cannot_revive", g4a), ("G4b_custody_ctx", g4b),
                       ("G5_story", g5)):
        out["gates"][name] = {"subs": subs, "verdict": a1.combine(subs)}
    out["A3_revival"] = rev
    out["A4_custody"] = {f"seed{s}": {"Dcontrast": stats[f"SCR{s}_Dcontrast"],
                                      "pair12dial": stats[f"SCR{s}_pair12dial"]}
                         for s in a1.SEEDS}
    out["A5_story"] = st
    out["A5_receipt_unsorted_flat_within_3sigma"] = bool(receipt)
    va = [out["gates"][k]["verdict"] for k in out["gates"]]
    out["VERDICT_A_quorum_fact"] = ("HOLDS" if all(v == "PASS" for v in va)
                                    else "DOES NOT HOLD" if any(v == "FAIL" for v in va)
                                    else "UNDERPOWERED")
    ctxs = [out["floors"][f"ctx{s}"] for s in a1.SEEDS]
    mean_ctx = float(np.mean([c["floor"] for c in ctxs]))
    se_pool = float(np.sqrt(sum(c["se"] ** 2 for c in ctxs)) / 3)
    cost = floor_plain - mean_ctx
    se_diff = float(np.sqrt(se_plain ** 2 + se_pool ** 2))
    out["B_context_cost"] = {"floor_plain": floor_plain, "mean_floor_ctx": mean_ctx,
                             "cost": cost, "se_diff": se_diff}
    out["VERDICT_B_context_cost"] = ("CONFIRMED" if cost >= 2 * se_diff
                                     else "REFUTED" if cost <= -2 * se_diff
                                     else "UNDERPOWERED")
    # ordering replication — REPORTED, not a verdict (A1b's G6 already CONFIRMED)
    f12, f13, f23 = (out["floors"]["s1s2"], out["floors"]["s1s3"], out["floors"]["s2s3"])
    lo = f12 if f12["floor"] <= f13["floor"] else f13
    out["ordering_replication_reported"] = {
        "diff": lo["floor"] - f23["floor"],
        "se_diff": float(np.sqrt(lo["se"] ** 2 + f23["se"] ** 2)),
        "floors": {k: out["floors"][k]["floor"] for k in ("s1s2", "s1s3", "s2s3")}}
    return out

def ka_gate(verbose=True):
    from qiskit.quantum_info import Statevector
    ok = True
    def chk(name, val, tgt):
        nonlocal ok
        good = abs(val - tgt) < 1e-9
        ok &= good
        if verbose: print(f"  KA {'PASS' if good else 'FAIL'}  {name:30s} {val:+.12f} (target {tgt})")
    pubs = build_pubs()
    ex = {p["name"]: a1b.pub_stats(p, a1.outcome_iter_exact(p["qc"])) for p in pubs}
    for c in a1b.COALS:
        k = a1.coal_name(c)
        chk(f"T dial {k}", a1b.dial_of(ex["T_b0"], ex["T_b1"], k)[0],
            0.0 if len(c) == 1 else 1.0)
    for m in ("C0", "C1"):
        for pr in a1b.PAIRS:
            k = a1.coal_name(pr)
            chk(f"{m} pair {k}", a1b.dial_of(ex[f"{m}_b0"], ex[f"{m}_b1"], k)[0], 1.0)
    # THE A1c integer target: pair-(1,2) reads b exactly under each REAL seeded scramble
    for seed in a1.SEEDS:
        chk(f"SCTX{seed} pair s1s2",
            a1b.dial_of(ex[f"SCTX{seed}_b0"], ex[f"SCTX{seed}_b1"], "s1s2")[0], 1.0)
    chk("RC p(pair12==mD)", ex["RC_pair12dial"]["p"], 1.0)
    chk("revival contrast", ex["A3_revival"]["contrast"], 1.0)
    for seed in a1.SEEDS:
        chk(f"SCR{seed} |D-contrast|", abs(ex[f"SCR{seed}_Dcontrast"]["contrast"]), 0.0)
        chk(f"SCR{seed} pair12 p", ex[f"SCR{seed}_pair12dial"]["p"], 1.0)
    chk("story sorted |X|", ex["A5_story"]["sorted_absX"], 1.0)
    chk("story unsorted X", ex["A5_story"]["unsorted_X"], 0.0)
    # counts-path self-test (anchored convention per A1 #3834)
    synth_stats = {}
    worst = 0.0
    for p in pubs:
        probs = Statevector(p["qc"].remove_final_measurements(inplace=False)).probabilities()
        synth = {format(i, "07b"): float(pr) * p["shots"]
                 for i, pr in enumerate(probs) if pr > 1e-14}
        via = a1b.pub_stats(p, a1.outcome_iter_counts(synth))
        synth_stats[p["name"]] = via
        e_ = ex[p["name"]]
        if p["kind"] == "dial":
            w = max(abs(e_[k]["p"] - via[k]["p"]) for k in e_)
        else:
            w = max(abs(e_[k] - via[k]) for k in
                    ("p", "contrast", "sorted_absX", "unsorted_X", "n_outcomes") if k in e_)
        worst = max(worst, w)
    ok &= worst < 1e-9
    if verbose: print(f"  KA {'PASS' if worst < 1e-9 else 'FAIL'}  counts-path self-test: 21/21 pubs (worst {worst:.2e})")
    g = grade(synth_stats)
    e2e = (g["VERDICT_A_quorum_fact"] == "HOLDS"
           and g["VERDICT_B_context_cost"] == "UNDERPOWERED"
           and g["A5_receipt_unsorted_flat_within_3sigma"])
    ok &= e2e
    if verbose:
        print(f"  KA {'PASS' if e2e else 'FAIL'}  e2e grade(): A={g['VERDICT_A_quorum_fact']} "
              f"B={g['VERDICT_B_context_cost']} (targets HOLDS / UNDERPOWERED)")
    triples = [(a1.three_state(1.00, 0.85, 0.001, ">="), "PASS"),
               (a1.three_state(0.70, 0.85, 0.001, ">="), "FAIL"),
               (a1.three_state(0.90, 0.85, 0.020, ">="), "PASS"),
               (a1.three_state(0.80, 0.85, 0.020, ">="), "FAIL"),
               (a1.three_state(0.86, 0.85, 0.020, ">="), "UNDERPOWERED"),
               (a1.three_state(0.05, 0.10, 0.001, "<="), "PASS"),
               (a1.three_state(0.15, 0.10, 0.001, "<="), "FAIL"),
               (a1.three_state(0.11, 0.10, 0.020, "<="), "UNDERPOWERED"),
               (a1.combine(["PASS", "PASS"]), "PASS"),
               (a1.combine(["PASS", "FAIL"]), "FAIL"),
               (a1.combine(["PASS", "UNDERPOWERED"]), "UNDERPOWERED"),
               (a1.combine(["FAIL", "UNDERPOWERED"]), "FAIL")]
    gka = all(got == want for got, want in triples)
    ok &= gka
    if verbose:
        print(f"  KA {'PASS' if gka else 'FAIL'}  grader branch KA: "
              f"{sum(g_ == w for g_, w in triples)}/12 (boundary-2 discriminating)")
        n2q = [sum(1 for inst in p['qc'].data
                   if len(inst.qubits) == 2 and inst.operation.name != 'measure') for p in pubs]
        print(f"  logical 2q: min {min(n2q)} max {max(n2q)} (HOLD 100 transpiled)")
        print(f"  prereg frozen-text sha: {assert_freeze()[:12]}")
    return ok

def fly():
    assert_freeze()
    if not ka_gate(): sys.exit("KA FENCE FAILED — NO SUBMISSION")
    if SEAL_REF is None: sys.exit("NO SEAL ON RECORD — set SEAL_REF (no-seal-no-fly)")
    sys.path.insert(0, SCRIPTS)
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT2")
    u = svc.usage()
    print(f"POOL RE-READ (ALT2): remaining {u['usage_remaining_seconds']}s of {u['usage_limit_seconds']}")
    best = None
    for b in svc.backends():
        st = b.status()
        if st.operational and b.configuration().n_qubits >= 7:
            if best is None or st.pending_jobs < best[0]: best = (st.pending_jobs, b)
    backend = best[1]
    props = backend.properties()
    errs = [p.value for g in props.gates if len(g.qubits) == 2 for p in g.parameters
            if p.name == "gate_error"]
    med = float(np.median(errs))
    if med > 0.005: sys.exit(f"CALIBRATION HOLD: median 2q {med:.4f} > 0.5%")
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling
    from qiskit.circuit.library import XGate
    pubs = build_pubs()
    tq = transpile([p["qc"] for p in pubs], backend, optimization_level=3, seed_transpiler=1104)
    try:
        durations = backend.target.durations()
        pm = PassManager([ALAPScheduleAnalysis(durations),
                          PadDynamicalDecoupling(durations, [XGate(), XGate()])])
        out = pm.run(tq)
    except Exception as e:
        sys.exit(f"DD HOLD: {e}")
    xb = sum(sum(1 for i in t.data if i.operation.name == "x") for t in tq)
    xa = sum(sum(1 for i in t.data if i.operation.name == "x") for t in out)
    if xa <= xb: sys.exit(f"DD HOLD: no DD pulses inserted (x {xb} -> {xa})")
    print(f"DD applied: X pulses {xb} -> {xa}")
    tq = out
    n2q = [sum(1 for inst in t.data if len(inst.qubits) == 2) for t in tq]
    print(f"transpiled 2q: min {min(n2q)} median {int(np.median(n2q))} max {max(n2q)}")
    if max(n2q) > 100: sys.exit(f"DEPTH HOLD: max {max(n2q)} > 100")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, p["shots"]) for t, p in zip(tq, pubs)])
    man = {"experiment": "h10_a1c_quorum_fact_context_priced", "cycle": "C5018",
           "prereg": "docs/h10-a1c-prereg-whisper-c5018.md",
           "prereg_frozen_sha12": FREEZE_SHA12, "seal": SEAL_REF, "go": GO_REF,
           "account": "ALT2", "pool_remaining_at_submit_s": u["usage_remaining_seconds"],
           "backend": backend.name, "median_2q_err": med,
           "hardening": "ALAP + X-X DD (standard)", "dd_x_pulses": [xb, xa],
           "scramble_seeds": a1.SEEDS,
           "pubs": [{"kind": p["kind"], "name": p["name"], "shots": p["shots"]} for p in pubs],
           "transpiled_2q_counts": n2q, "job_id": job.job_id(),
           "committer": "Whisper (DC15W)"}
    path = os.path.join(RESULTS, f"h10_a1c_flight_manifest_{job.job_id()}.json")
    json.dump(man, open(path, "w"), indent=1)
    print(f"SUBMITTED: {job.job_id()} -> {path}")

def decode(job_id):
    sys.path.insert(0, SCRIPTS)
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(job_id)
    print(f"job on {acct}")
    res = svc.job(job_id).result()
    pubs = build_pubs()
    stats = {}
    for p, r in zip(pubs, res):
        counts = r.data.c.get_counts() if hasattr(r.data, "c") else r.data.meas.get_counts()
        stats[p["name"]] = a1b.pub_stats(p, a1.outcome_iter_counts(counts))
    out = grade(stats)
    out["job_id"] = job_id
    path = os.path.join(RESULTS, f"h10_a1c_decode_{job_id}.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    for k, v in out["gates"].items():
        print(f"  {k:18s} {v['verdict']:12s} subs={v['subs']}")
    print(f"  floors: {[(k, round(v['floor'], 4)) for k, v in out['floors'].items()]}")
    print(f"  bars:   {[(k, round(v, 4)) for k, v in out['bars'].items()]}")
    b = out["B_context_cost"]
    print(f"  B: cost {b['cost']:+.4f} ± {b['se_diff']:.4f} (plain {b['floor_plain']:.4f} vs ctx {b['mean_floor_ctx']:.4f})")
    o = out["ordering_replication_reported"]
    print(f"  ordering (reported): diff {o['diff']:+.4f} ± {o['se_diff']:.4f}")
    print(f"  receipt flat: {out['A5_receipt_unsorted_flat_within_3sigma']}")
    print(f"  VERDICT A (quorum fact): {out['VERDICT_A_quorum_fact']}")
    print(f"  VERDICT B (context cost): {out['VERDICT_B_context_cost']}\n-> {path}")

if __name__ == "__main__":
    if "--fly" in sys.argv:
        fly()
    elif "--decode" in sys.argv:
        decode(sys.argv[sys.argv.index("--decode") + 1])
    else:
        print("BUILD CHECK (KA fence, exact):")
        print("KA GATE:", "PASS — awaiting Ember seal (SEAL_REF), then fly" if ka_gate()
              else "FAIL")
