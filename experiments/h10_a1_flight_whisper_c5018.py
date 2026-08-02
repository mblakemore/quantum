#!/usr/bin/env python3
"""H10-A1 FLIGHT — The Quorum Fact (Whisper C5018).

Sealed prereg: docs/h10-a1-prereg-whisper-c5018.md — Ember seal a91a577d over prefix 5494
(whole document). This script is the as-built instrument that prereg registered; Ember's
check [3] (registered bars present in flight code) runs against THIS file before it flies.

CONSTRUCTION (7 qubits, D + 6 share qubits — the sealed count):
  coherent (2,3) Shamir over GF(4), degree 1: share_i = a*x_i + b, x_i in {1, w, w+1}.
  The mask a is ABSORBED into share 1's superposition (share1 = a + b is a bijection in a,
  so summing over a == summing over share1): H,H on share-1's two qubits IS the uniform
  mask, and shares 2,3 are computed from share 1 and D by CNOTs. 9 CX logical, no ancilla,
  nothing to uncompute — the sealed "mask register uncomputed in-circuit" realized by
  never materializing it. The KA fence proves as-built == campaign state at 1e-9.

REGISTERED VALUES (sealed §3/§4 — Ember's [3] looks for these literals):
  G1 threshold: singles dial <= 0.10  AND  pairs dial >= 0.85
  G2 control  : control singles dial >= 0.85          (positive-condition health)
  G3 revival  : D X-contrast >= 0.80
  G4 custody  : post-scramble |D-contrast| <= 0.10 AND pair-(1,2) dial >= 0.85 (worst seed)
  G5 story    : sorted weighted mean |<X>_D| >= 0.70  (unsorted flat = REPORTED receipt)
  KA fence 1e-9 on INTEGER targets; depth HOLD 100 transpiled 2q; calibration HOLD 0.5%;
  shots 500/pub dial, 2000 revival, 1000/pub scramble, 4000 story (26,000 total).
  Three-state verdicts: UNDERPOWERED if |value - bar| < 2*se, else PASS/FAIL.
"""
import hashlib, importlib.util, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
RESULTS = os.path.join(HERE, "..", "results")
DOCS = os.path.join(HERE, "..", "docs")

# ---- sealed-prereg freeze (Ember coordination#3823) ----
SEAL_PREFIX = 5494
SEAL_SHA12 = "a91a577d09b9"

def assert_seal():
    raw = open(os.path.join(DOCS, "h10-a1-prereg-whisper-c5018.md"), "rb").read()
    h = hashlib.sha256(raw[:SEAL_PREFIX]).hexdigest()
    assert h.startswith(SEAL_SHA12), f"SEALED PREREG MISMATCH: {h[:12]} != {SEAL_SHA12}"
    return h

# ---- Creator GO (seats §5: no GO, no submission). Set to the GO reference when granted.
GO_REF = "Creator general#3843 'A1 Go' (2026-08-02 21:36Z)"

# ---- GF(4): bits (c1,c0); add = xor; w^2 = w+1 ----
def gmul(a, b):
    a1, a0 = a >> 1, a & 1; b1, b0 = b >> 1, b & 1
    c1 = (a1 & b0) ^ (a0 & b1) ^ (a1 & b1)
    c0 = (a0 & b0) ^ (a1 & b1)
    return (c1 << 1) | c0

def ginv(a):
    return next(x for x in range(1, 4) if gmul(a, x) == 1)

X_PTS = {1: 1, 2: 2, 3: 3}                      # share index -> x_i (1, w, w+1)

def lagrange_coeffs(i, j):
    """b = s_i*L_i + s_j*L_j at x=0 (char 2: x_i - x_j == x_i ^ x_j)."""
    xi, xj = X_PTS[i], X_PTS[j]
    inv = ginv(xi ^ xj)
    return gmul(xj, inv), gmul(xi, inv)

# ---- qubit layout: 0=D, (1,2)=share1 (c1,c0), (3,4)=share2, (5,6)=share3 ----
SHARE_Q = {1: (1, 2), 2: (3, 4), 3: (5, 6)}
SEEDS = [1101, 1102, 1103]                       # frozen scramble seeds (3, per prereg)
SHOTS = {"dial": 500, "revival": 2000, "scramble": 1000, "story": 4000}

def encode_threshold(qc):
    """9-CX Shamir encode from D (=b) and share-1 superposition (=absorbed mask)."""
    qc.h(1); qc.h(2)
    qc.cx(1, 3); qc.cx(2, 3); qc.cx(0, 3)        # s2_c1 = s1_c1 + s1_c0 + b
    qc.cx(1, 4); qc.cx(0, 4)                     # s2_c0 = s1_c1 + b
    qc.cx(2, 5); qc.cx(0, 5)                     # s3_c1 = s1_c0 + b
    qc.cx(1, 6); qc.cx(2, 6)                     # s3_c0 = s1_c1 + s1_c0

def encode_control(qc):
    """Plain-redundancy control: every share qubit copies b (6 CX)."""
    for t in range(1, 7):
        qc.cx(0, t)

def scramble_gate(seed):
    from qiskit.circuit.library import UnitaryGate
    from qiskit.quantum_info import random_unitary
    return UnitaryGate(random_unitary(4, seed=seed), label=f"scr{seed}")

def coal_name(coal):
    """THE canonical coalition label: (1,)->'s1', (1,2)->'s1s2'. One function, every site
    -- the grading-path fence caught grade() writing 'A1_1s2' while gates read 'A1_s1s2'
    (two inline conventions). Naming is derived, never re-transcribed."""
    return "".join(f"s{x}" for x in coal)

def build_pubs():
    from qiskit import QuantumCircuit
    pubs = []
    coals = [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]

    def base(record, encoder):
        qc = QuantumCircuit(7, 7)
        if record: qc.h(0)
        encoder(qc)
        return qc

    for arm, encoder in (("A1", encode_threshold), ("A2", encode_control)):
        for b in (0, 1):
            for coal in coals:
                qc = QuantumCircuit(7, 7)
                if b: qc.x(0)
                encoder(qc)
                qc.measure(range(7), range(7))
                pubs.append({"arm": arm, "name": f"{arm}_dial_{coal_name(coal)}_b{b}",
                             "coal": coal, "b": b, "shots": SHOTS["dial"], "qc": qc})
    qc = base(True, encode_threshold)
    inv = base(False, lambda q: None)            # E-dagger appended below
    e = QuantumCircuit(7); encode_threshold(e)
    qc.compose(e.inverse(), inplace=True)
    qc.h(0)
    qc.measure(range(7), range(7))
    pubs.append({"arm": "A3", "name": "A3_revival", "shots": SHOTS["revival"], "qc": qc})
    for seed in SEEDS:
        qc = base(True, encode_threshold)
        qc.append(scramble_gate(seed), [5, 6])
        qc.h(0); qc.measure(range(7), range(7))
        pubs.append({"arm": "A4", "name": f"A4_seed{seed}_Dcontrast", "seed": seed,
                     "shots": SHOTS["scramble"], "qc": qc})
        qc = base(True, encode_threshold)
        qc.append(scramble_gate(seed), [5, 6])
        qc.measure(range(7), range(7))
        pubs.append({"arm": "A4", "name": f"A4_seed{seed}_pair12dial", "seed": seed,
                     "shots": SHOTS["scramble"], "qc": qc})
    qc = base(True, encode_threshold)
    for q in range(7): qc.h(q)
    qc.measure(range(7), range(7))
    pubs.append({"arm": "A5", "name": "A5_story", "shots": SHOTS["story"], "qc": qc})
    assert len(pubs) == 36 and sum(p["shots"] for p in pubs) == 26000
    return pubs

# ---- FROZEN DECODERS — one code path for KA (exact) and hardware (counts) ----
# A bit accessor bit(k) returns qubit k's measured bit for one outcome.

def share_elem(bit, i):
    q1, q0 = SHARE_Q[i]
    return (bit(q1) << 1) | bit(q0)

def decode_threshold(bit, coal):
    """Frozen: singles guess b_hat = c0(share) (mask-0 guess; blindness makes it 1/2);
    pairs = Lagrange c0; triple = Lagrange on shares (1,2) [frozen choice]."""
    if len(coal) == 1:
        return share_elem(bit, coal[0]) & 1
    i, j = coal[0], coal[1]
    Li, Lj = lagrange_coeffs(i, j)
    return (gmul(share_elem(bit, i), Li) ^ gmul(share_elem(bit, j), Lj)) & 1

def decode_control(bit, coal):
    """Frozen control-map decoder: c0 of the first-listed share."""
    return share_elem(bit, coal[0]) & 1

def outcome_iter_exact(qc):
    """(prob, bit-accessor) over the exact statevector of qc minus final measures."""
    from qiskit.quantum_info import Statevector
    body = qc.remove_final_measurements(inplace=False)
    probs = Statevector(body).probabilities()
    for idx, p in enumerate(probs):
        if p > 1e-14:
            yield float(p), (lambda k, idx=idx: (idx >> k) & 1)

def outcome_iter_counts(counts):
    for key, n in counts.items():
        yield float(n), (lambda k, key=key: int(key[len(key) - 1 - k]))

def pub_stats(pub, outcomes):
    """Frozen statistics per pub kind. Returns dict of raw p-hats / values."""
    kind = pub["name"]
    tot = 0.0; hit = 0.0; d0 = 0.0
    story = {}
    for w, bit in outcomes:
        tot += w
        if pub["arm"] in ("A1", "A2"):
            dec = decode_threshold if pub["arm"] == "A1" else decode_control
            hit += w * (dec(bit, pub["coal"]) == pub["b"])
        elif kind == "A3_revival" or kind.endswith("Dcontrast"):
            d0 += w * (bit(0) == 0)
        elif kind.endswith("pair12dial"):
            hit += w * (decode_threshold(bit, (1, 2)) == bit(0))
        elif kind == "A5_story":
            o = sum(bit(k) << (k - 1) for k in range(1, 7))
            n, n0 = story.get(o, (0.0, 0.0))
            story[o] = (n + w, n0 + w * (bit(0) == 0))
    if pub["arm"] in ("A1", "A2") or kind.endswith("pair12dial"):
        p = hit / tot
        return {"p": p, "se_p": np.sqrt(max(p * (1 - p), 0.25 / tot) / tot)}
    if kind == "A3_revival" or kind.endswith("Dcontrast"):
        p = d0 / tot
        se = np.sqrt(max(p * (1 - p), 0.25 / tot) / tot)
        return {"contrast": 2 * p - 1, "se": 2 * se}
    xs = {o: (2 * n0 - n) / n for o, (n, n0) in story.items()}
    sorted_x = sum(n / tot * abs(xs[o]) for o, (n, n0) in story.items())
    unsorted_x = sum(n / tot * xs[o] for o, (n, n0) in story.items())
    se_sorted = float(np.sqrt(sum((n / tot) ** 2 * max(1 - xs[o] ** 2, 1 / n) / n
                                  for o, (n, n0) in story.items())))
    se_uns = float(np.sqrt(max(1 - unsorted_x ** 2, 1 / tot) / tot))
    return {"sorted_absX": sorted_x, "unsorted_X": unsorted_x, "n_outcomes": len(story),
            "se_sorted": se_sorted, "se_unsorted": se_uns}

def dial_from_pair(st0, st1):
    """dial = mean over b of (2*p_hat - 1); se from binomial per b-pub."""
    d = (2 * st0["p"] - 1 + 2 * st1["p"] - 1) / 2
    return d, float(np.sqrt(st0["se_p"] ** 2 + st1["se_p"] ** 2))

# ---- KA FENCE: every sealed ideal at 1e-9 (integer targets) + campaign cross-check ----
def ka_gate(verbose=True):
    pubs = build_pubs()
    stats = {p["name"]: pub_stats(p, outcome_iter_exact(p["qc"])) for p in pubs}
    checks = []
    coals = [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    for arm, tgt in (("A1", {1: 0.0, 2: 1.0, 3: 1.0}), ("A2", {1: 1.0, 2: 1.0, 3: 1.0})):
        for coal in coals:
            cs = coal_name(coal)
            d, _ = dial_from_pair(stats[f"{arm}_dial_{cs}_b0"], stats[f"{arm}_dial_{cs}_b1"])
            checks.append((f"{arm} dial {cs}", d, tgt[len(coal)]))
    checks.append(("A3 revival contrast", stats["A3_revival"]["contrast"], 1.0))
    for seed in SEEDS:
        checks.append((f"A4 seed{seed} |D-contrast|",
                       abs(stats[f"A4_seed{seed}_Dcontrast"]["contrast"]), 0.0))
        checks.append((f"A4 seed{seed} pair12 dial",
                       2 * stats[f"A4_seed{seed}_pair12dial"]["p"] - 1, 1.0))
    checks.append(("A5 sorted |X|", stats["A5_story"]["sorted_absX"], 1.0))
    checks.append(("A5 unsorted X", stats["A5_story"]["unsorted_X"], 0.0))
    ok = True
    for name, val, tgt in checks:
        good = abs(val - tgt) < 1e-9
        ok &= good
        if verbose: print(f"  KA {'PASS' if good else 'FAIL'}  {name:28s} {val:+.12f} (target {tgt:.0f})")
    # campaign cross-check: as-built statevector == sim psi_b / record (bit-reversal map)
    spec = importlib.util.spec_from_file_location(
        "sim", os.path.join(SCRIPTS, "h10_a1_quorum_sim_c5018.py"))
    sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    def rev7(v):
        out = np.zeros(128, complex)
        for i in range(128):
            j = int(format(i, "07b")[::-1], 2)
            out[j] = v[i]
        return out
    for b in (0, 1):
        qc = QuantumCircuit(7)
        if b: qc.x(0)
        encode_threshold(qc)
        want = np.zeros(128, complex)
        want[b * 64: b * 64 + 64] = sim.psi_b(b)
        m = np.abs(np.asarray(Statevector(qc)) - rev7(want)).max()
        ok &= m < 1e-9
        if verbose: print(f"  KA {'PASS' if m < 1e-9 else 'FAIL'}  campaign state b={b} (max amp diff {m:.2e})")
    qc = QuantumCircuit(7); qc.h(0); encode_threshold(qc)
    m = np.abs(np.asarray(Statevector(qc)) - rev7(sim.record_state())).max()
    ok &= m < 1e-9
    if verbose: print(f"  KA {'PASS' if m < 1e-9 else 'FAIL'}  campaign record state (max amp diff {m:.2e})")
    # counts-path self-test (Elder coordination#3829, his [8]): the fence must exercise
    # EVERY decode path the flight uses. outcome_iter_counts extracts bits from qiskit
    # counts KEYS (string, MSB-left); synthesize those keys from the same exact
    # distribution and assert both iterators yield identical statistics. A bit-convention
    # mismatch here passes the exact fence and decodes every dial to a PLAUSIBLE wrong
    # number — no absurd 13/21 rescues the reader.
    # EXTERNAL ANCHOR (Elder #3834): iterator agreement alone is circular — format(i,"07b")
    # and the counts iterator invert each other BY CONSTRUCTION. That format() matches
    # qiskit's real get_counts convention was verified against hardware reality with an
    # asymmetric |100> run: statevector index 4 -> "100" == real sampler key. With that
    # one assumption anchored, this check is load-bearing, not mutual-consistency.
    value_keys = ("p", "contrast", "sorted_absX", "unsorted_X", "n_outcomes")
    synth_stats = {}
    for p in pubs:
        body = p["qc"].remove_final_measurements(inplace=False)
        probs = Statevector(body).probabilities()
        synth = {format(i, "07b"): float(pr) * p["shots"]
                 for i, pr in enumerate(probs) if pr > 1e-14}
        exact = pub_stats(p, outcome_iter_exact(p["qc"]))
        via = pub_stats(p, outcome_iter_counts(synth))
        synth_stats[p["name"]] = via
        worst = max(abs(exact[k] - via[k]) for k in value_keys if k in exact)
        ok &= worst < 1e-9
        if worst >= 1e-9 and verbose:
            print(f"  KA FAIL  counts-path {p['name']}: exact vs via-counts diff {worst:.2e}")
    if verbose:
        print(f"  KA PASS  counts-path self-test: 36/36 pubs, both iterators agree" if ok
              else "  KA counts-path self-test FAILED")
    # grading-path fence (Ember [8] residual, coordination#3835): run the COMPLETE decode
    # pipeline — grade(): dials -> three_state -> combine -> verdict — on the synthetic
    # ideal counts and demand HOLDS with every gate PASS and the receipt flat. Then hit
    # the verdict branches ideal data can never reach with direct known-answer triples.
    g = grade(synth_stats)
    all_pass = all(g["gates"][k]["verdict"] == "PASS" for k in g["gates"])
    e2e = g["VERDICT"] == "HOLDS" and all_pass and g["A5_receipt_unsorted_flat_within_3sigma"]
    ok &= e2e
    if verbose:
        print(f"  KA {'PASS' if e2e else 'FAIL'}  end-to-end grade() on ideal counts -> "
              f"{g['VERDICT']}, gates {'all PASS' if all_pass else 'NOT all PASS'}")
    grader_ka = [
        (three_state(1.00, 0.85, 0.001, ">="), "PASS"),
        (three_state(0.70, 0.85, 0.001, ">="), "FAIL"),
        (three_state(0.86, 0.85, 0.020, ">="), "UNDERPOWERED"),
        (three_state(0.05, 0.10, 0.001, "<="), "PASS"),
        (three_state(0.15, 0.10, 0.001, "<="), "FAIL"),
        (three_state(0.11, 0.10, 0.020, "<="), "UNDERPOWERED"),
        (combine(["PASS", "PASS"]), "PASS"),
        (combine(["PASS", "FAIL"]), "FAIL"),
        (combine(["PASS", "UNDERPOWERED"]), "UNDERPOWERED"),
        (combine(["FAIL", "UNDERPOWERED"]), "FAIL"),
    ]
    gka = all(got == want for got, want in grader_ka)
    ok &= gka
    if verbose:
        print(f"  KA {'PASS' if gka else 'FAIL'}  grader branch KA: "
              f"{sum(got == want for got, want in grader_ka)}/10 verdict triples")
    n2q = [sum(1 for inst in p["qc"].data if len(inst.qubits) == 2 and inst.operation.name != "measure")
           for p in pubs]
    if verbose:
        print(f"  logical 2q counts: min {min(n2q)} max {max(n2q)} (HOLD at 100 transpiled)")
        print(f"  seal: {assert_seal()[:12]} over prefix {SEAL_PREFIX} verified")
    return ok

# ---- FLY ----
def fly():
    assert_seal()
    if not ka_gate(): sys.exit("KA FENCE FAILED — NO SUBMISSION")
    if GO_REF is None: sys.exit("NO CREATOR GO ON RECORD (seats §5) — set GO_REF to the GO reference")
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
    pubs = build_pubs()
    tq = transpile([p["qc"] for p in pubs], backend, optimization_level=3, seed_transpiler=1104)
    # DD standard from B1b onward (prereg §2); identical machinery, identical HOLDs
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling
    from qiskit.circuit.library import XGate
    try:
        durations = backend.target.durations()
        pm = PassManager([ALAPScheduleAnalysis(durations),
                          PadDynamicalDecoupling(durations, [XGate(), XGate()])])
        out = pm.run(tq)
    except Exception as e:
        sys.exit(f"DD HOLD: scheduling/DD pass failed — {e}")
    xb = sum(sum(1 for i in t.data if i.operation.name == "x") for t in tq)
    xa = sum(sum(1 for i in t.data if i.operation.name == "x") for t in out)
    if xa <= xb: sys.exit(f"DD HOLD: no DD pulses inserted (x {xb} -> {xa})")
    print(f"DD applied: X pulses {xb} -> {xa}")
    tq = out
    n2q = [sum(1 for inst in t.data if len(inst.qubits) == 2) for t in tq]
    print(f"transpiled 2q counts: min {min(n2q)} median {int(np.median(n2q))} max {max(n2q)}")
    if max(n2q) > 100: sys.exit(f"DEPTH HOLD: max transpiled 2q {max(n2q)} > 100")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, p["shots"]) for t, p in zip(tq, pubs)])
    man = {"experiment": "h10_a1_quorum_fact", "cycle": "C5018",
           "prereg": "docs/h10-a1-prereg-whisper-c5018.md",
           "prereg_seal": {"prefix": SEAL_PREFIX, "sha256_12": SEAL_SHA12,
                           "sealed_by": "ember coordination#3823"},
           "go": GO_REF, "account": "ALT2",
           "pool_remaining_at_submit_s": u["usage_remaining_seconds"],
           "backend": backend.name, "median_2q_err": med,
           "hardening": "ALAP + X-X dynamical decoupling (standard from B1b)",
           "dd_x_pulses": [xb, xa], "scramble_seeds": SEEDS,
           "pubs": [{"arm": p["arm"], "name": p["name"], "shots": p["shots"]} for p in pubs],
           "transpiled_2q_counts": n2q, "job_id": job.job_id(),
           "committer": "Whisper (DC15W)"}
    path = os.path.join(RESULTS, f"h10_a1_flight_manifest_{job.job_id()}.json")
    json.dump(man, open(path, "w"), indent=1)
    print(f"SUBMITTED: {job.job_id()} -> {path}")

# ---- DECODE (job-named; no discretion) ----
def three_state(value, bar, se, direction):
    """direction '>=': pass if value >= bar; '<=': pass if value <= bar.
    UNDERPOWERED if |value - bar| < 2*se."""
    if abs(value - bar) < 2 * se: return "UNDERPOWERED"
    ok = value >= bar if direction == ">=" else value <= bar
    return "PASS" if ok else "FAIL"

def combine(subs):
    if any(s == "FAIL" for s in subs): return "FAIL"
    if all(s == "PASS" for s in subs): return "PASS"
    return "UNDERPOWERED"

def grade(stats):
    """The COMPLETE post-counts decode: stats -> dials -> gates -> verdict. One code path,
    exercised end-to-end by ka_gate() on synthetic ideal counts (Ember [8] residual:
    grading logic must be fenced too, not just bit extraction)."""
    out = {"experiment": "h10_a1_quorum_fact", "gates": {}, "dials": {}}
    coals = [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    for arm in ("A1", "A2"):
        for coal in coals:
            cs = coal_name(coal)
            d, se = dial_from_pair(stats[f"{arm}_dial_{cs}_b0"], stats[f"{arm}_dial_{cs}_b1"])
            out["dials"][f"{arm}_{cs}"] = {"dial": d, "se": se}
    g1 = [three_state(out["dials"][f"A1_s{i}"]["dial"], 0.10, out["dials"][f"A1_s{i}"]["se"], "<=")
          for i in (1, 2, 3)]
    g1 += [three_state(out["dials"][f"A1_{cs}"]["dial"], 0.85, out["dials"][f"A1_{cs}"]["se"], ">=")
           for cs in ("s1s2", "s1s3", "s2s3")]
    g2 = [three_state(out["dials"][f"A2_s{i}"]["dial"], 0.85, out["dials"][f"A2_s{i}"]["se"], ">=")
          for i in (1, 2, 3)]
    rev = stats["A3_revival"]
    g3 = [three_state(rev["contrast"], 0.80, rev["se"], ">=")]
    g4 = []
    for seed in SEEDS:
        dc = stats[f"A4_seed{seed}_Dcontrast"]
        pd = stats[f"A4_seed{seed}_pair12dial"]
        g4.append(three_state(abs(dc["contrast"]), 0.10, dc["se"], "<="))
        g4.append(three_state(2 * pd["p"] - 1, 0.85, 2 * pd["se_p"], ">="))
    st = stats["A5_story"]
    g5 = [three_state(st["sorted_absX"], 0.70, st["se_sorted"], ">=")]
    receipt_ok = abs(st["unsorted_X"]) <= 3 * st["se_unsorted"]
    for name, subs in (("G1_threshold", g1), ("G2_control", g2), ("G3_revival", g3),
                       ("G4_custody", g4), ("G5_story", g5)):
        out["gates"][name] = {"subs": subs, "verdict": combine(subs)}
    out["A3_revival"] = rev
    out["A4"] = {f"seed{s}": {"Dcontrast": stats[f"A4_seed{s}_Dcontrast"],
                              "pair12dial": stats[f"A4_seed{s}_pair12dial"]} for s in SEEDS}
    out["A5_story"] = st
    out["A5_receipt_unsorted_flat_within_3sigma"] = bool(receipt_ok)
    verdicts = [out["gates"][g]["verdict"] for g in
                ("G1_threshold", "G2_control", "G3_revival", "G4_custody", "G5_story")]
    out["VERDICT"] = ("HOLDS" if all(v == "PASS" for v in verdicts)
                      else "DOES NOT HOLD" if any(v == "FAIL" for v in verdicts)
                      else "UNDERPOWERED")
    return out

def decode(job_id):
    sys.path.insert(0, SCRIPTS)
    from ibm_multi_account import multi_account_service
    job = None
    for svc in multi_account_service():
        try:
            job = svc.job(job_id); break
        except Exception:
            continue
    if job is None: sys.exit(f"job {job_id} not found in any account")
    res = job.result()
    pubs = build_pubs()
    stats = {}
    for p, r in zip(pubs, res):
        counts = r.data.c.get_counts() if hasattr(r.data, "c") else r.data.meas.get_counts()
        stats[p["name"]] = pub_stats(p, outcome_iter_counts(counts))
    out = grade(stats)
    out["job_id"] = job_id
    path = os.path.join(RESULTS, f"h10_a1_decode_{job_id}.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    for g in ("G1_threshold", "G2_control", "G3_revival", "G4_custody", "G5_story"):
        print(f"  {g:14s} {out['gates'][g]['verdict']:12s} subs={out['gates'][g]['subs']}")
    print(f"  receipt (unsorted flat within 3 sigma): {out['A5_receipt_unsorted_flat_within_3sigma']}")
    print(f"  VERDICT: {out['VERDICT']}\n-> {path}")

if __name__ == "__main__":
    if "--fly" in sys.argv:
        fly()
    elif "--decode" in sys.argv:
        decode(sys.argv[sys.argv.index("--decode") + 1])
    else:
        print("BUILD CHECK (KA fence, exact):")
        print("KA GATE:", "PASS — flight-ready pending Creator GO + Ember [3]" if ka_gate()
              else "FAIL")
