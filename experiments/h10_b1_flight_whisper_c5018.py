#!/usr/bin/env python3
"""H10-B1 FLIGHT — The Time Flip vs the definite-time-direction ceiling (Whisper C5018).
Prereg: docs/h10-b1-prereg-whisper-c5018.md — seal chain DERIVED AT MANIFEST-WRITE TIME
(Elder #3722: identifiers are derived from the artifact, never transcribed; SEAL_PREFIXES
is the one unavoidable transcription and an assert refuses submission if the spec outgrows
it). Governing bands per A4/A5: G4a [0.78,0.89], G4b [0.69,0.75], KA 1e-9 exact-fraction
targets. Gated on: seal at chain head + Creator GO + KA + depth HOLD 150 + calibration
0.5% + pool re-read.

Arms (compiled-access fence per SS1: circuits consume the public (U,V) matrices, never the
class label; the flip's controlled gate collapsing to +/-I is the game's own theorem):
  F  2q:  H(c); W0=U^T V on target (1q unitary); Z(c) iff W1 W0^dag == -I (evaluated from
          the matrices; == +/-I exactly by the promise); H(c); measure c.
          win: M+ reads 0, M- reads 1. Ideal 1 per pair.
  P  4q:  Bell(0,1), Bell(2,3); U on 0, V on 2; FIXED 4q Helstrom rotation (eigenbasis of
          p+rho+ - p-rho-); measure all; outcome in S+ -> guess M+. Ideal 0.857143.
  S  3q:  Bell(t=0, anc=1), control=2 in |+>; UV on t; c-[(UV)^dag VU] (controlled 1q);
          FIXED 3q Helstrom rotation; measure all. Ideal 15/21 exactly.
KA fence: exact walker over AS-BUILT pubs reproduces per-pair F wins = 1 and aggregate
P/S values at 1e-9 before any submission.

LOAD-BEARING DEPENDENCY (Elder coordination#3692, written down at his ask): since
Amendment 4 widened G4a's upper edge to the parallel ceiling, G4a NO LONGER independently
backstops the WRONG-STRATEGY fault (an arm that is not purely product-measurement reading
into (0.87, 0.89]). That fault is covered by THIS KA FENCE — a compilation that entangles
the two probe blocks moves the frozen expected value (dev 1.4e-7) and fails pre-flight.
DO NOT weaken, loosen, or skip this fence without restoring a tight G4a upper edge:
the fence acquired a second job on 2026-08-02 and this line is how you know.
"""
import argparse, json, os, sys
import importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
SCRIPTS = os.path.join(HERE, "..", "scripts")
spec = importlib.util.spec_from_file_location("bp", os.path.join(SCRIPTS, "h10_b1_pairs_c5018.py"))
bp = importlib.util.module_from_spec(spec); spec.loader.exec_module(bp)
PAIRS = bp.PAIRS
SPEC = os.path.join(HERE, "..", "docs", "h10-b1-prereg-whisper-c5018.md")
SEAL_PREFIXES = [7117, 9253, 11779, 14364, 17583, 24146, 30801]  # guard fired 2026-08-03 on the stale list; updated consciously

def derived_chain():
    """Chain citation DERIVED from the artifact at call time — cannot go stale silently:
    if the spec grows past SEAL_PREFIXES[-1] the assert fires and nothing submits."""
    import hashlib
    raw = open(SPEC, "rb").read()
    assert len(raw) == SEAL_PREFIXES[-1], (
        f"spec is {len(raw)} B but SEAL_PREFIXES ends at {SEAL_PREFIXES[-1]} — the seal "
        f"chain grew; update SEAL_PREFIXES before flying")
    return [{"prefix_bytes": n, "sha256_16": hashlib.sha256(raw[:n]).hexdigest()[:16]}
            for n in SEAL_PREFIXES]
PPLUS = [p for p in PAIRS if p[3] == "M+"]; PMIN = [p for p in PAIRS if p[3] == "M-"]
p_plus, p_min = 13 / 21, 8 / 21
PHI = np.zeros(4, complex); PHI[0] = PHI[3] = 1 / np.sqrt(2)
SHOTS = 500

def choi(U): return np.kron(U, np.eye(2)) @ PHI

def helstrom_basis(states_plus, states_min):
    """Returns (V, plus_mask): measurement = rotate by V^dag, outcome k guesses M+ iff
    plus_mask[k] (eigenvalue of p+rho+ - p-rho- positive)."""
    rp = sum(np.outer(v, v.conj()) for v in states_plus) / len(states_plus)
    rm = sum(np.outer(v, v.conj()) for v in states_min) / len(states_min)
    w, V = np.linalg.eigh(p_plus * rp - p_min * rm)
    return V, (w > 0)

# fixed measurement bases (committed pairs — public data). Amendment 3: the P arm uses
# the LOCAL product measurement (marginal-Helstrom bases + Bayes mask) from the committed
# artifact — 6/7 exact, ~8 2q gates; the joint 4q rotation (190 transpiled 2q) tripped the
# depth HOLD and is retired.
LOCP = json.load(open(os.path.join(RESULTS, "h10_b1_localP_c5018.json")))
B1L = np.array(LOCP["B1_re"]) + 1j * np.array(LOCP["B1_im"])
B2L = np.array(LOCP["B2_re"]) + 1j * np.array(LOCP["B2_im"])
MASKP = np.array(LOCP["bayes_mask_plus"], dtype=bool).reshape(-1)   # index a*4+b
VP = None  # retired (joint rotation)
def switch_state(U, V):
    a = np.kron(choi(U @ V), np.array([1, 0], complex))
    b = np.kron(choi(V @ U), np.array([0, 1], complex))
    return (a + b) / np.sqrt(2)
SP3 = [switch_state(U, V) for _, U, V, _ in PPLUS]
SM3 = [switch_state(U, V) for _, U, V, _ in PMIN]
VS, MASKS = helstrom_basis(SP3, SM3)

# ---------------- pub construction (explicit unitaries; walker == circuit) ----------------
def flip_pub(name, U, V, lab):
    W0 = U.T @ V
    s = (U @ V.T) @ W0.conj().T
    is_minus = np.allclose(s, -np.eye(2), atol=1e-10)
    assert is_minus or np.allclose(s, np.eye(2), atol=1e-10), f"promise broken {name}"
    return {"arm": "F", "name": name, "label": lab, "W0": W0, "zc": bool(is_minus),
            "win_outcome": ("1" if lab == "M-" else "0")}

def par_pub(name, U, V, lab):
    return {"arm": "P", "name": name, "label": lab, "U": U, "V": V}

def sw_pub(name, U, V, lab):
    G = (U @ V).conj().T @ (V @ U)
    return {"arm": "S", "name": name, "label": lab, "UV": U @ V, "G": G}

def build_pubs():
    out = []
    for name, U, V, lab in PAIRS:
        out += [flip_pub(name, U, V, lab), par_pub(name, U, V, lab), sw_pub(name, U, V, lab)]
    return out

# ---------------- exact walker (states are tiny; build final vectors directly) ----------------
def ideal_win(pub):
    lab = pub["label"]
    if pub["arm"] == "F":
        # |+>|0> -> W0 on target, Z on control iff zc -> H(c) -> P(win_outcome)
        c = np.array([1, 1], complex) / np.sqrt(2)
        if pub["zc"]: c = np.diag([1, -1]) @ c
        Hh = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        c = Hh @ c
        p0, p1 = abs(c[0]) ** 2, abs(c[1]) ** 2
        return p1 if lab == "M-" else p0
    if pub["arm"] == "P":
        a = np.abs(B1L.conj().T @ choi(pub["U"])) ** 2
        b = np.abs(B2L.conj().T @ choi(pub["V"])) ** 2
        joint = np.outer(a, b).reshape(-1)
        return float(sum(pr for pr, m in zip(joint, MASKP) if m == (lab == "M+")))
    if pub["arm"] == "S":
        v = np.kron(choi(pub["UV"]), np.array([1, 0], complex)) * 0  # placeholder replaced below
        # build via the CIRCUIT: Bell(t,anc) x |+>_c; UV on t; c-G; then VS^dag; masks
        st = np.kron(PHI, np.array([1, 1], complex) / np.sqrt(2))    # (t,anc) x c, c fastest
        st = st.reshape(4, 2)
        st[:, 0] = (np.kron(pub["UV"], np.eye(2)) @ st[:, 0])
        st[:, 1] = (np.kron(pub["UV"] @ pub["G"], np.eye(2)) @ st[:, 1])
        v = st.reshape(-1)
        # reorder to (t, anc, c) with c slowest to match VS basis (t x anc x c? our switch_state
        # built kron(choi, control) => control fastest) — VS was built on kron(4, 2) = c fastest ✓
        amps = VS.conj().T @ v
        return float(sum(abs(a) ** 2 for a, m in zip(amps, MASKS) if m == (lab == "M+")))
    raise ValueError

def circuit_win(pub):
    """End-to-end through the AS-BUILT qiskit circuit (statevector), using the SAME
    outcome-index rule the decode applies — closes the endianness class the fence exists for."""
    from qiskit.quantum_info import Statevector
    qc = to_qiskit(pub)
    qc.remove_final_measurements(inplace=True)
    probs = np.abs(Statevector.from_instruction(qc).data) ** 2
    lab = pub["label"]
    if pub["arm"] == "F":
        # creg bit = q1 (control): outcome index bit1
        p1 = float(sum(pr for k, pr in enumerate(probs) if (k >> 1) & 1))
        return p1 if pub["win_outcome"] == "1" else 1 - p1
    MASK = MASKP if pub["arm"] == "P" else MASKS
    return float(sum(pr for k, pr in enumerate(probs) if MASK[k] == (lab == "M+")))

def ka_gate():
    # Amendment 5: targets are EXACT FRACTIONS (6/7, 15/21, 1) and the tolerance is the
    # ORIGINAL registered 1e-9 on every arm — nothing loosened, the A5 constant-fix made
    # the registered condition satisfiable as written. (The flown-once 1e-6 accommodated
    # 6-decimal literals; that flight is graded EXPLORATORY in the record.)
    pubs = build_pubs()
    def agg(arm, fn): return float(np.mean([fn(p) for p in pubs if p["arm"] == arm]))
    kF_m = max(abs(1 - ideal_win(p)) for p in pubs if p["arm"] == "F")
    kP_m = abs(agg("P", ideal_win) - 6 / 7)
    kS_m = abs(agg("S", ideal_win) - 15 / 21)
    kF_c = max(abs(1 - circuit_win(p)) for p in pubs if p["arm"] == "F")
    kP_c = abs(agg("P", circuit_win) - 6 / 7)
    kS_c = abs(agg("S", circuit_win) - 15 / 21)
    ok = all(v < 1e-9 for v in (kF_m, kF_c, kP_m, kS_m, kP_c, kS_c))
    print(f"KA matrix : F {kF_m:.2e} | P dev {kP_m:.2e} | S dev {kS_m:.2e}")
    print(f"KA circuit: F {kF_c:.2e} | P dev {kP_c:.2e} | S dev {kS_c:.2e}  -> "
          f"{'PASS' if ok else 'FAIL'}")
    return ok

# ---------------- qiskit build ----------------
def to_qiskit(pub):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    if pub["arm"] == "F":
        qc = QuantumCircuit(2, 1)          # q0 target, q1 control
        qc.h(1)
        qc.append(UnitaryGate(pub["W0"]), [0])
        if pub["zc"]: qc.z(1)
        qc.h(1)
        qc.measure(1, 0)
        return qc
    if pub["arm"] == "P":
        # qubit assignment matches the matrix index (sysU MSB): q3=sysU q2=ancU q1=sysV q0=ancV;
        # qiskit little-endian => UnitaryGate(VP^dag) on [q0..q3] has q0 least significant =
        # ancV = the matrix minor; int(bitstring,2) = q3*8+q2*4+q1*2+q0 = the matrix index.
        qc = QuantumCircuit(4, 4)
        qc.h(3); qc.cx(3, 2); qc.h(1); qc.cx(1, 0)
        qc.append(UnitaryGate(pub["U"]), [3]); qc.append(UnitaryGate(pub["V"]), [1])
        # Amendment 3: LOCAL rotations. B1 acts on (sysU=q3 MSB, ancU=q2) -> qiskit [q2,q3];
        # B2 on (sysV=q1, ancV=q0) -> [q0,q1]. Measured int = (B1 idx)*4 + (B2 idx) = mask idx.
        qc.append(UnitaryGate(B1L.conj().T), [2, 3])
        qc.append(UnitaryGate(B2L.conj().T), [0, 1])
        qc.measure(range(4), range(4))
        return qc
    if pub["arm"] == "S":
        # q2=target (matrix MSB), q1=anc, q0=control (matrix minor)
        qc = QuantumCircuit(3, 3)
        qc.h(2); qc.cx(2, 1); qc.h(0)
        qc.append(UnitaryGate(pub["UV"]), [2])
        qc.append(UnitaryGate(pub["G"]).control(1), [0, 2])
        qc.append(UnitaryGate(VS.conj().T), [0, 1, 2])
        qc.measure(range(3), range(3))
        return qc

def apply_dd(tq, backend):
    """Amendment 6 (B1b): ALAP scheduling + X-X dynamical decoupling in idle windows.
    Identity at the logical level. HOLD if the pass cannot apply — the NAME B1b asserts
    the hardening; flying without it would mislabel the experiment."""
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling
    from qiskit.circuit.library import XGate
    try:
        durations = backend.target.durations()
        pm = PassManager([ALAPScheduleAnalysis(durations),
                          PadDynamicalDecoupling(durations, [XGate(), XGate()])])
        out = pm.run(tq)
    except Exception as e:
        sys.exit(f"DD HOLD (Amendment 6): scheduling/DD pass failed — {e}")
    x_before = sum(sum(1 for i in t.data if i.operation.name == "x") for t in tq)
    x_after = sum(sum(1 for i in t.data if i.operation.name == "x") for t in out)
    if x_after <= x_before:
        sys.exit(f"DD HOLD (Amendment 6): no DD pulses were inserted (x {x_before} -> {x_after})")
    print(f"DD applied: X pulses {x_before} -> {x_after}")
    return out

def fly(dd=False):
    if not ka_gate(): sys.exit("KA FENCE FAILED — NO SUBMISSION")
    sys.path.insert(0, SCRIPTS)
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT2")
    u = svc.usage()
    print(f"POOL RE-READ (ALT2): remaining {u['usage_remaining_seconds']}s of {u['usage_limit_seconds']}")
    best = None
    for b in svc.backends():
        st = b.status()
        if st.operational and b.configuration().n_qubits >= 4:
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
    qcs = [to_qiskit(p) for p in pubs]
    tq = transpile(qcs, backend, optimization_level=3, seed_transpiler=1104)
    if dd:
        tq = apply_dd(tq, backend)
    n2q = [sum(1 for inst in t.data if len(inst.qubits) == 2) for t in tq]
    print(f"transpiled 2q counts: min {min(n2q)} median {int(np.median(n2q))} max {max(n2q)}")
    if max(n2q) > 150: sys.exit(f"DEPTH HOLD: max transpiled 2q {max(n2q)} > 150")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, SHOTS) for t in tq])
    man = {"experiment": "h10_b1b_time_flip_dd" if dd else "h10_b1_time_flip", "cycle": "C5018",
           "hardening": "ALAP + X-X dynamical decoupling (Amendment 6)" if dd else None,
           "prereg": "docs/h10-b1-prereg-whisper-c5018.md",
           "prereg_seal_chain_derived": derived_chain(),
           "go": "RE-FLY: Creator general#3719 'Go B1' (2026-08-02, fresh GO post-EXPLORATORY); first flight general#3674",
           "account": "ALT2", "pool_remaining_at_submit_s": u["usage_remaining_seconds"],
           "backend": backend.name, "chain_2q_median": med,
           "pubs": [{"arm": p["arm"], "name": p["name"], "label": p["label"], "shots": SHOTS}
                    for p in pubs],
           "transpiled_2q_counts": n2q, "job_id": job.job_id(),
           "committer": "Whisper (DC15W)"}
    # Ember #3738: a file recording a specific execution carries that execution's id in
    # its NAME, or the next execution inherits its filename. Same rule as the decode.
    path = os.path.join(RESULTS, f"h10_b1_flight_manifest_{job.job_id()}.json")
    json.dump(man, open(path, "w"), indent=1)
    print(f"SUBMITTED: {job.job_id()} -> {path}")

def decode(job_id):
    sys.path.insert(0, SCRIPTS)
    from ibm_multi_account import service_for_job
    svc, acct = service_for_job(job_id)
    print(f"job on {acct}")
    res = svc.job(job_id).result()
    man = json.load(open(os.path.join(RESULTS, "h10_b1_flight_manifest.json")))
    pubs = build_pubs()
    wins = {"F": [], "P": [], "S": []}
    per_pair = {}
    for p, meta, pr in zip(pubs, man["pubs"], res):
        cnt = pr.data.c.get_counts()
        n = sum(cnt.values())
        if p["arm"] == "F":
            w = cnt.get(p["win_outcome"], 0) / n
        else:
            MASK = MASKP if p["arm"] == "P" else MASKS
            w = 0.0
            for s, c in cnt.items():
                k = int(s, 2)
                if MASK[k] == (p["label"] == "M+"): w += c / n
        wins[p["arm"]].append(w)
        per_pair[f"{p['arm']}_{p['name']}"] = w
    out = {"job_id": job_id, "per_pair": per_pair}
    N = SHOTS * 21
    for arm in ("F", "P", "S"):
        m = float(np.mean(wins[arm]))
        se = float(np.sqrt(max(m * (1 - m), 1e-12) / N))
        out[arm] = {"win": m, "se": se}
    pF, seF = out["F"]["win"], out["F"]["se"]
    pP, seP = out["P"]["win"], out["P"]["se"]
    pS, seS = out["S"]["win"], out["S"]["se"]
    out["G1"] = {"pass": bool((pF - 0.919746) / seF >= 5), "sig": (pF - 0.919746) / seF}
    out["G2"] = {"pass": bool((pF - pP) / np.hypot(seF, seP) >= 5),
                 "sig": (pF - pP) / float(np.hypot(seF, seP))}
    out["G3"] = {"pass": bool((pP - pS) / np.hypot(seP, seS) >= 5),
                 "sig": (pP - pS) / float(np.hypot(seP, seS))}
    out["G4a"] = {"pass": bool(0.78 <= pP <= 0.89), "value": pP}
    out["G4b"] = {"pass": bool(0.69 <= pS <= 0.75), "value": pS}
    # A6.1: the A5.2 fault-zone edge is the EVALUATED formula, printed before any zone read.
    zone_edge = 0.665897 + 3 * seS   # A6.1: un-rounded SDP fault base (Elder #3804)
    out["A5_2_zone"] = {"evaluated_fault_edge": float(zone_edge),
                        "reading": pS,
                        "zone": ("FAULT" if pS <= zone_edge else
                                 "ATTENUATION-CONSISTENT" if pS < 0.69 else
                                 "PASS-BAND" if pS <= 0.75 else "WRONG-STRATEGY"),
                        "sigma_from_edge": float((pS - zone_edge) / seS)}
    allpass = all(out[g]["pass"] for g in ("G1", "G2", "G3", "G4a", "G4b"))
    out["VERDICT"] = "HOLDS" if allpass else "DOES NOT HOLD"
    # Elder #3731: flights are append-only events; the decode path binds to its job so a
    # successor can never overwrite its predecessor (the exploratory decode survived only
    # in git history when this was one mutable path).
    path = os.path.join(RESULTS, f"h10_b1_decode_{job_id}.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("F", "P", "S", "G1", "G2", "G3", "G4a", "G4b",
                                           "VERDICT")}, indent=1, default=float))
    print("->", path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ka", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--fly-b1b", action="store_true", dest="flyb1b")
    ap.add_argument("--decode")
    a = ap.parse_args()
    if a.ka: sys.exit(0 if ka_gate() else 1)
    if a.fly: fly(); sys.exit(0)
    if a.flyb1b: fly(dd=True); sys.exit(0)
    if a.decode: decode(a.decode); sys.exit(0)
    ap.print_help()
