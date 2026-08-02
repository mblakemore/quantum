#!/usr/bin/env python3
"""H10-A1b FLIGHT — quorum fact on floor-anchored bars + the ordering gate (Whisper C5018).

Prereg: docs/h10-a1b-prereg-whisper-c5018.md (frozen at seal request; FREEZE_SHA below).
GO on record: Creator general#3865 "Go A1b". Flies on Ember seal.

ARCHITECTURE (the transcription-surface rule, applied to reuse):
- Every frozen primitive is IMPORTED from the fenced A1 flight module — GF(4) algebra,
  Lagrange decoders, share layout, threshold encode, scramble gates+seeds, outcome
  iterators, three_state/combine, and A1's pub_stats for the revival/custody/story
  statistics. Nothing is re-typed.
- The depth-matched control circuits are DERIVED from the imported threshold encode by
  stripping its non-CX gates (asserted: exactly the 9-CX graph remains, CX list
  identical). The control is the threshold circuit minus superposition, by construction.
- The control codeword decodes b through the SAME decode_threshold Lagrange path as the
  threshold arm — the control calibrates the decoder itself, like-for-like.

SEALED CONSTANTS (prereg §4 — Ember's [3] looks for these literals):
  G1a singles cap 0.10 · G1b pair bar = max(floor_pair - 3*se_floor - 0.030, 0.700)
  G2 control pairs >= 0.800 (absolute) · G3 revival >= 0.950
  G4a |D-contrast| <= 0.10 · G4b custody bar = max(floor_rec - 3*se_floor - 0.040, 0.650)
  G5 story >= 0.820 (receipt <= 3 sigma reported)
  G6 ordering: diff = min(floor_s1s2, floor_s1s3) - floor_s2s3; CONFIRMED/REFUTED at
  +/-2*se_diff, else UNDERPOWERED
  Three-state boundary: 2*se (SEALED) · depth HOLD 100 · calibration HOLD 0.5%
  Shots: dial 3000, record-control 3000, revival 2000, scramble 1500, story 4000 (36,000)
  KA e2e targets on ideal counts: verdict A = HOLDS, verdict B = UNDERPOWERED.
"""
import hashlib, importlib.util, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
RESULTS = os.path.join(HERE, "..", "results")
DOCS = os.path.join(HERE, "..", "docs")

_spec = importlib.util.spec_from_file_location(
    "a1", os.path.join(HERE, "h10_a1_flight_whisper_c5018.py"))
a1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(a1)

GO_REF = "Creator general#3865 'Go A1b' (2026-08-02)"
PREREG = os.path.join(DOCS, "h10-a1b-prereg-whisper-c5018.md")
FREEZE_SHA12 = "41ef8972e333"   # frozen at seal request (text freezes at the request post)
SEAL_REF = None                 # set to Ember's seal post reference; fly() refuses until then

def assert_freeze():
    h = hashlib.sha256(open(PREREG, "rb").read()).hexdigest()
    if FREEZE_SHA12 is not None:
        assert h.startswith(FREEZE_SHA12), f"PREREG FROZEN-TEXT MISMATCH: {h[:12]}"
    return h

COALS = [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
PAIRS = [(1, 2), (1, 3), (2, 3)]
SHOTS = {"dial": 3000, "rc": 3000, "rev": 2000, "scr": 1500, "story": 4000}
ALLOW_PAIR, BACKSTOP_PAIR = 0.030, 0.700         # G1b sealed constants
ALLOW_REC, BACKSTOP_REC = 0.040, 0.650           # G4b sealed constants
CTRL_ABS = 0.800                                 # G2 sealed absolute
BAR_REV, BAR_STORY, CAP = 0.950, 0.820, 0.10     # G3 / G5 / caps, sealed

def shares_of(s1, b):
    """Codeword line f(x) = a*x + b with a = s1 XOR b (campaign-verified)."""
    a = s1 ^ b
    return {i: a1.gmul(a, a1.X_PTS[i]) ^ b for i in (1, 2, 3)}

def cx_graph():
    """The threshold encode's CX graph, DERIVED from the imported fenced circuit."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(7); a1.encode_threshold(qc)
    g = QuantumCircuit(7); ncx = 0
    for inst in qc.data:
        if inst.operation.name == "cx":
            g.append(inst.operation, inst.qubits); ncx += 1
        else:
            assert inst.operation.name == "h", f"unexpected gate {inst.operation.name}"
    assert ncx == 9, f"threshold graph is not 9 CX ({ncx})"
    return g

def build_pubs():
    from qiskit import QuantumCircuit
    g = cx_graph()
    pubs = []
    def finish(qc, kind, name, shots, **kw):
        qc.measure(range(7), range(7))
        pubs.append({"kind": kind, "name": name, "shots": shots, "qc": qc, **kw})
    for b in (0, 1):                                       # threshold dials
        qc = QuantumCircuit(7, 7)
        if b: qc.x(0)
        a1.encode_threshold(qc)
        finish(qc, "dial", f"T_b{b}", SHOTS["dial"], b=b, map="T")
    for vname, s1 in (("C0", 0), ("C1", 3)):               # depth-matched controls
        for b in (0, 1):
            qc = QuantumCircuit(7, 7)
            if b: qc.x(0)
            if s1 & 2: qc.x(1)
            if s1 & 1: qc.x(2)
            qc.compose(g, inplace=True)
            finish(qc, "dial", f"{vname}_b{b}", SHOTS["dial"], b=b, map=vname, s1=s1)
    qc = QuantumCircuit(7, 7); qc.h(0); qc.compose(g, inplace=True)   # record-control
    finish(qc, "rc", "RC_pair12dial", SHOTS["rc"])
    qc = QuantumCircuit(7, 7); qc.h(0); a1.encode_threshold(qc)       # revival (as A1)
    e = QuantumCircuit(7); a1.encode_threshold(e)
    qc.compose(e.inverse(), inplace=True); qc.h(0)
    finish(qc, "rev", "A3_revival", SHOTS["rev"])
    for seed in a1.SEEDS:                                  # custody (A1 seeds, frozen)
        qc = QuantumCircuit(7, 7); qc.h(0); a1.encode_threshold(qc)
        qc.append(a1.scramble_gate(seed), [5, 6]); qc.h(0)
        finish(qc, "scr_d", f"SCR{seed}_Dcontrast", SHOTS["scr"], seed=seed)
        qc = QuantumCircuit(7, 7); qc.h(0); a1.encode_threshold(qc)
        qc.append(a1.scramble_gate(seed), [5, 6])
        finish(qc, "scr_pair", f"SCR{seed}_pair12dial", SHOTS["scr"], seed=seed)
    qc = QuantumCircuit(7, 7); qc.h(0); a1.encode_threshold(qc)       # story (as A1)
    for q in range(7): qc.h(q)
    finish(qc, "story", "A5_story", SHOTS["story"])
    assert len(pubs) == 15 and sum(p["shots"] for p in pubs) == 36000
    return pubs

def pub_stats(pub, outcomes):
    """Dial pubs: per-coalition shared-shot stats through the imported frozen decoder.
    All other kinds: PASS THROUGH to A1's fenced pub_stats (zero re-implementation)."""
    if pub["kind"] == "dial":
        tot = 0.0; hit = {c: 0.0 for c in COALS}
        for w, bit in outcomes:
            tot += w
            for c in COALS:
                hit[c] += w * (a1.decode_threshold(bit, c) == pub["b"])
        out = {}
        for c in COALS:
            p = hit[c] / tot
            out[a1.coal_name(c)] = {"p": p,
                                    "se_p": float(np.sqrt(max(p * (1 - p), 0.25 / tot) / tot))}
        return out
    passthru = {"rc": ("A4", "RC_pair12dial"), "scr_pair": ("A4", pub["name"]),
                "scr_d": ("A4", pub["name"]), "rev": ("A3", "A3_revival"),
                "story": ("A5", "A5_story")}
    arm, name = passthru[pub["kind"]]
    return a1.pub_stats({"arm": arm, "name": name}, outcomes)

def dial_of(st0, st1, coal_key):
    d = (2 * st0[coal_key]["p"] - 1 + 2 * st1[coal_key]["p"] - 1) / 2
    se = float(np.sqrt(st0[coal_key]["se_p"] ** 2 + st1[coal_key]["se_p"] ** 2))
    return d, se

def grade(stats):
    """COMPLETE post-counts decode -> both verdicts. One code path, KA'd end-to-end."""
    out = {"experiment": "h10_a1b_quorum_fact_floor_anchored", "dials": {}, "floors": {},
           "bars": {}, "gates": {}}
    for m in ("T", "C0", "C1"):
        for c in COALS:
            k = a1.coal_name(c)
            d, se = dial_of(stats[f"{m}_b0"], stats[f"{m}_b1"], k)
            out["dials"][f"{m}_{k}"] = {"dial": d, "se": se}
    for pr in PAIRS:                                       # floors (mean over variants)
        k = a1.coal_name(pr)
        f = (out["dials"][f"C0_{k}"]["dial"] + out["dials"][f"C1_{k}"]["dial"]) / 2
        se = float(np.sqrt(out["dials"][f"C0_{k}"]["se"] ** 2
                           + out["dials"][f"C1_{k}"]["se"] ** 2) / 2)
        out["floors"][k] = {"floor": f, "se": se}
        out["bars"][f"pair_{k}"] = max(f - 3 * se - ALLOW_PAIR, BACKSTOP_PAIR)
    rc = stats["RC_pair12dial"]
    floor_rec = 2 * rc["p"] - 1; se_rec = 2 * rc["se_p"]
    out["floors"]["rec12"] = {"floor": floor_rec, "se": se_rec}
    out["bars"]["custody"] = max(floor_rec - 3 * se_rec - ALLOW_REC, BACKSTOP_REC)
    g1a = [a1.three_state(out["dials"][f"T_s{i}"]["dial"], CAP,
                          out["dials"][f"T_s{i}"]["se"], "<=") for i in (1, 2, 3)]
    g1b = [a1.three_state(out["dials"][f"T_{a1.coal_name(pr)}"]["dial"],
                          out["bars"][f"pair_{a1.coal_name(pr)}"],
                          out["dials"][f"T_{a1.coal_name(pr)}"]["se"], ">=") for pr in PAIRS]
    g2 = [a1.three_state(out["dials"][f"{m}_{a1.coal_name(pr)}"]["dial"], CTRL_ABS,
                         out["dials"][f"{m}_{a1.coal_name(pr)}"]["se"], ">=")
          for m in ("C0", "C1") for pr in PAIRS]
    rev = stats["A3_revival"]
    g3 = [a1.three_state(rev["contrast"], BAR_REV, rev["se"], ">=")]
    g4a, g4b = [], []
    for seed in a1.SEEDS:
        dc = stats[f"SCR{seed}_Dcontrast"]
        pd = stats[f"SCR{seed}_pair12dial"]
        g4a.append(a1.three_state(abs(dc["contrast"]), CAP, dc["se"], "<="))
        g4b.append(a1.three_state(2 * pd["p"] - 1, out["bars"]["custody"],
                                  2 * pd["se_p"], ">="))
    st = stats["A5_story"]
    g5 = [a1.three_state(st["sorted_absX"], BAR_STORY, st["se_sorted"], ">=")]
    receipt = abs(st["unsorted_X"]) <= 3 * st["se_unsorted"]
    for name, subs in (("G1a_blindness", g1a), ("G1b_pair_read", g1b),
                       ("G2_control_abs", g2), ("G3_revival", g3),
                       ("G4a_cannot_revive", g4a), ("G4b_custody_read", g4b),
                       ("G5_story", g5)):
        out["gates"][name] = {"subs": subs, "verdict": a1.combine(subs)}
    out["A3_revival"] = rev
    out["A5_story"] = st
    out["A5_receipt_unsorted_flat_within_3sigma"] = bool(receipt)
    va = [out["gates"][k]["verdict"] for k in out["gates"]]
    out["VERDICT_A_quorum_fact"] = ("HOLDS" if all(v == "PASS" for v in va)
                                    else "DOES NOT HOLD" if any(v == "FAIL" for v in va)
                                    else "UNDERPOWERED")
    f12, f13 = out["floors"]["s1s2"], out["floors"]["s1s3"]
    f23 = out["floors"]["s2s3"]
    lo = f12 if f12["floor"] <= f13["floor"] else f13
    diff = lo["floor"] - f23["floor"]
    se_diff = float(np.sqrt(lo["se"] ** 2 + f23["se"] ** 2))
    out["G6_ordering"] = {"diff": diff, "se_diff": se_diff,
                          "floors": {k: out["floors"][k]["floor"]
                                     for k in ("s1s2", "s1s3", "s2s3")}}
    out["VERDICT_B_depth_mechanism"] = ("CONFIRMED" if diff >= 2 * se_diff
                                        else "REFUTED" if diff <= -2 * se_diff
                                        else "UNDERPOWERED")
    return out

def ka_gate(verbose=True):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    ok = True
    def chk(name, val, tgt):
        nonlocal ok
        good = abs(val - tgt) < 1e-9
        ok &= good
        if verbose: print(f"  KA {'PASS' if good else 'FAIL'}  {name:30s} {val:+.12f} (target {tgt})")
    pubs = build_pubs()
    # structural: control graph CX list == threshold encode CX list (depth-match assert)
    qc = QuantumCircuit(7); a1.encode_threshold(qc)
    tlist = [(inst.qubits[0]._index, inst.qubits[1]._index)
             for inst in qc.data if inst.operation.name == "cx"]
    glist = [(inst.qubits[0]._index, inst.qubits[1]._index) for inst in cx_graph().data]
    same = tlist == glist and len(glist) == 9
    ok &= same
    if verbose: print(f"  KA {'PASS' if same else 'FAIL'}  depth-match: control CX list == threshold ({len(glist)} CX)")
    # control codeword states are the exact computational states of the campaign algebra
    for vname, s1 in (("C0", 0), ("C1", 3)):
        for b in (0, 1):
            p = next(x for x in pubs if x["name"] == f"{vname}_b{b}")
            sh = shares_of(s1, b)
            idx = b
            for i, (q1, q0) in ((1, (1, 2)), (2, (3, 4)), (3, (5, 6))):
                idx |= ((sh[i] >> 1) << q1) | ((sh[i] & 1) << q0)
            v = np.asarray(Statevector(p["qc"].remove_final_measurements(inplace=False)))
            chk(f"codeword state {vname} b={b}", float(abs(v[idx]) ** 2), 1.0)
    # exact stats through the one code path
    ex = {p["name"]: pub_stats(p, a1.outcome_iter_exact(p["qc"])) for p in pubs}
    for c in COALS:
        k = a1.coal_name(c)
        tgt = 0.0 if len(c) == 1 else 1.0
        chk(f"T dial {k}", dial_of(ex["T_b0"], ex["T_b1"], k)[0], tgt)
    for m in ("C0", "C1"):
        for pr in PAIRS:
            k = a1.coal_name(pr)
            chk(f"{m} pair dial {k}", dial_of(ex[f"{m}_b0"], ex[f"{m}_b1"], k)[0], 1.0)
    for m, s1 in (("C0", 0), ("C1", 3)):     # control singles ideals DERIVED from algebra
        for i in (1, 2, 3):
            want = np.mean([2.0 * ((shares_of(s1, b)[i] & 1) == b) - 1 for b in (0, 1)])
            chk(f"{m} single dial s{i}", dial_of(ex[f"{m}_b0"], ex[f"{m}_b1"], f"s{i}")[0],
                float(want))
    chk("RC p(pair12==mD)", ex["RC_pair12dial"]["p"], 1.0)
    chk("revival contrast", ex["A3_revival"]["contrast"], 1.0)
    for seed in a1.SEEDS:
        chk(f"SCR{seed} |D-contrast|", abs(ex[f"SCR{seed}_Dcontrast"]["contrast"]), 0.0)
        chk(f"SCR{seed} pair12 p", ex[f"SCR{seed}_pair12dial"]["p"], 1.0)
    chk("story sorted |X|", ex["A5_story"]["sorted_absX"], 1.0)
    chk("story unsorted X", ex["A5_story"]["unsorted_X"], 0.0)
    # counts-path self-test (Elder [8]; format(i,'07b') anchored vs reality at A1 #3834)
    synth_stats = {}
    worst_all = 0.0
    for p in pubs:
        probs = Statevector(p["qc"].remove_final_measurements(inplace=False)).probabilities()
        synth = {format(i, "07b"): float(pr) * p["shots"]
                 for i, pr in enumerate(probs) if pr > 1e-14}
        via = pub_stats(p, a1.outcome_iter_counts(synth))
        synth_stats[p["name"]] = via
        exp_ = ex[p["name"]]
        if p["kind"] == "dial":
            w = max(abs(exp_[k]["p"] - via[k]["p"]) for k in exp_)
        else:
            w = max(abs(exp_[k] - via[k]) for k in
                    ("p", "contrast", "sorted_absX", "unsorted_X", "n_outcomes") if k in exp_)
        worst_all = max(worst_all, w)
    ok &= worst_all < 1e-9
    if verbose: print(f"  KA {'PASS' if worst_all < 1e-9 else 'FAIL'}  counts-path self-test: 15/15 pubs (worst {worst_all:.2e})")
    # end-to-end grade on ideal counts: A = HOLDS, B = UNDERPOWERED (sealed KA targets)
    g = grade(synth_stats)
    e2e = (g["VERDICT_A_quorum_fact"] == "HOLDS"
           and g["VERDICT_B_depth_mechanism"] == "UNDERPOWERED"
           and g["A5_receipt_unsorted_flat_within_3sigma"])
    ok &= e2e
    if verbose:
        print(f"  KA {'PASS' if e2e else 'FAIL'}  e2e grade(): A={g['VERDICT_A_quorum_fact']} "
              f"B={g['VERDICT_B_depth_mechanism']} (targets HOLDS / UNDERPOWERED)")
        print(f"       ideal bars: pairs {[round(g['bars'][f'pair_{a1.coal_name(p)}'], 4) for p in PAIRS]} "
              f"custody {g['bars']['custody']:.4f}")
    # The two 0.02-se triples below DISCRIMINATE the sealed boundary constant 2 from any
    # neighbor (margin 0.05 = 2.5*se: PASS/FAIL iff the constant is 2; UNDERPOWERED if 3)
    # — Elder's #3868 residual made executable: the fence pins the code to the seal.
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
        print(f"  KA {'PASS' if gka else 'FAIL'}  grader branch KA: {sum(g_ == w for g_, w in triples)}/12 (boundary-2 discriminating)")
        n2q = [sum(1 for inst in p['qc'].data
                   if len(inst.qubits) == 2 and inst.operation.name != 'measure') for p in pubs]
        print(f"  logical 2q: min {min(n2q)} max {max(n2q)} (HOLD 100 transpiled)")
        print(f"  prereg frozen-text sha: {assert_freeze()[:12]}")
    return ok

def fly():
    assert_freeze()
    if not ka_gate(): sys.exit("KA FENCE FAILED — NO SUBMISSION")
    if SEAL_REF is None:
        sys.exit("NO SEAL ON RECORD — set SEAL_REF to Ember's seal post (no-seal-no-fly, executable)")
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
    man = {"experiment": "h10_a1b_quorum_fact_floor_anchored", "cycle": "C5018",
           "prereg": "docs/h10-a1b-prereg-whisper-c5018.md",
           "prereg_frozen_sha12": FREEZE_SHA12, "go": GO_REF, "account": "ALT2",
           "pool_remaining_at_submit_s": u["usage_remaining_seconds"],
           "backend": backend.name, "median_2q_err": med,
           "hardening": "ALAP + X-X DD (standard)", "dd_x_pulses": [xb, xa],
           "scramble_seeds": a1.SEEDS,
           "pubs": [{"kind": p["kind"], "name": p["name"], "shots": p["shots"]} for p in pubs],
           "transpiled_2q_counts": n2q, "job_id": job.job_id(),
           "committer": "Whisper (DC15W)"}
    path = os.path.join(RESULTS, f"h10_a1b_flight_manifest_{job.job_id()}.json")
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
        stats[p["name"]] = pub_stats(p, a1.outcome_iter_counts(counts))
    out = grade(stats)
    out["job_id"] = job_id
    path = os.path.join(RESULTS, f"h10_a1b_decode_{job_id}.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    for k, v in out["gates"].items():
        print(f"  {k:18s} {v['verdict']:12s} subs={v['subs']}")
    print(f"  floors: {[(k, round(v['floor'], 4)) for k, v in out['floors'].items()]}")
    print(f"  bars:   {[(k, round(v, 4)) for k, v in out['bars'].items()]}")
    print(f"  G6: diff {out['G6_ordering']['diff']:+.4f} ± {out['G6_ordering']['se_diff']:.4f}")
    print(f"  receipt flat: {out['A5_receipt_unsorted_flat_within_3sigma']}")
    print(f"  VERDICT A (quorum fact): {out['VERDICT_A_quorum_fact']}")
    print(f"  VERDICT B (depth mechanism): {out['VERDICT_B_depth_mechanism']}\n-> {path}")

if __name__ == "__main__":
    if "--fly" in sys.argv:
        fly()
    elif "--decode" in sys.argv:
        decode(sys.argv[sys.argv.index("--decode") + 1])
    else:
        print("BUILD CHECK (KA fence, exact):")
        print("KA GATE:", "PASS — awaiting Ember seal (FREEZE_SHA12), then fly" if ka_gate()
              else "FAIL")
