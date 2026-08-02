#!/usr/bin/env python3
"""H10-C1 WINDING METER — FLIGHT, Amendment-3 protocol (Whisper C5017).
Prereg: docs/h10-c1-prereg-whisper-c5017.md (seals d1702ef7 / d6602cf2 / A2; Amendment 3
pending re-seal). Registered bars: results/h10_c1_prereg_bars_v2_c5017.json (v2 — the
Hadamard-test meter; v1 is superseded and kept for the record).

METER: C(g) = <Psi| B_R e^{igV} A_L |Psi>, A = Q(t) on L, B = Q(-t) on R, measured by an
ancilla Hadamard test (Re: plain; Im: S^dag on ancilla). CERTIFICATION (bars-v2, committed):
on the exact TFD this equals sum_S f(S) e^{igS} at 2e-15 — the meter provably reads the
winding distribution on the ideal state. Registered numbers are the estimator's noiseless
values on the FLOWN state (like-for-like at the state level).

Controlled pieces, priced:
  c-A: A = U X_L0 U^dag  -> circuit U^dag_L, CX(anc->L0), U_L (U-blocks uncontrolled)
  c-B: B = U^dag X_R0 U  -> circuit U_R, CX(anc->R0), U^dag_R
  c-e^{igV}: rank-1 trick per pair block — W_i eigenvalue +3 exactly on the pair's Phi+;
    e^{-igW_i/4} = e^{ig/4} [ I - (1-e^{-ig}) |Phi+><Phi+| ]. Bell-conjugate (CX, H) maps
    Phi+ -> |00>, X,X maps to |11>, then MCP(-g) on (anc, L_i, R_i). Ancilla phase P per
    block plus the V-constant — every factor verified by the KA walker, not by trust.

MANDATORY KA FENCE (prereg SS5.1 + Amendment 3): a 13-qubit instruction walker runs the
AS-BUILT pubs exactly; (K1) circuit-vs-operator cross-check of C(g) on the flown state at
1e-9 per grid point; (K2) end-to-end decode of walked pubs reproduces every registered v2
number at 1e-6; (K3) beta0 pubs decode to zero winding at 1e-6. Any non-completion = FAIL.
"""
import argparse, json, math, os, re, sys
import importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
SCRIPTS = os.path.join(HERE, "..", "scripts")
spec = importlib.util.spec_from_file_location("rt", os.path.join(SCRIPTS, "h10_c1_rhohalf_route_c5017.py"))
rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)

BARS = json.load(open(os.path.join(RESULTS, "h10_c1_prereg_bars_v2_c5017.json")))
ROUTE = json.load(open(os.path.join(RESULTS, "h10_c1_rhohalf_route_c5017.json")))
SEL = ROUTE["routeB_variational"][ROUTE["Lstar"]]
PARAMS = np.array(SEL["params"]); LAYERS = SEL["L"]
GSTAR = BARS["gstar_registered"]
PAIRS = rt.PAIRS; J = rt._Jc; HFLD = rt._hc; T = rt.T
G16 = [2 * np.pi * k / 16 for k in range(16)]
ANC = 12

# ---------------- circuit IR ----------------
def sweep_ops(gamma, side, reverse=False):
    off = 0 if side == 0 else 6
    ops = []
    for k, (i, j) in enumerate(PAIRS):
        a = 2 * gamma * J[k]
        ops += [("rxx", (off + i, off + j), a), ("ryy", (off + i, off + j), a),
                ("rzz", (off + i, off + j), a)]
    for i in range(6):
        ops.append(("rz", (off + i,), 2 * gamma * HFLD[i]))
    return list(reversed(ops)) if reverse else ops

def trotter_ops(t, side):
    ops = []
    for _ in range(2):
        dt = t / 2
        ops += sweep_ops(dt / 2, side)
        ops += sweep_ops(dt / 2, side, reverse=True)
    return ops

def prep_ops(params, layers):
    ops = []
    for i in range(6):
        ops += [("h", (i,), None), ("cx", (i, 6 + i), None)]
    k = 0
    for _ in range(layers):
        aX, aY, aZ = params[k:k + 3]; k += 3
        g = params[k]; k += 1
        for i in range(6):
            ops += [("rxx", (i, 6 + i), 2 * aX), ("ryy", (i, 6 + i), 2 * aY),
                    ("rzz", (i, 6 + i), 2 * aZ)]
        ops += sweep_ops(g, 0) + sweep_ops(g, 1)
    return ops

def c_eV_ops(g):
    """Controlled-e^{igV}: rank-1 per pair + ancilla phases (verified by KA, incl. constants)."""
    ops = []
    for i in range(6):
        ops += [("cx", (i, 6 + i), None), ("h", (i,), None),
                ("x", (i,), None), ("x", (6 + i,), None),
                ("mcp", (ANC, i, 6 + i), -g),
                ("x", (i,), None), ("x", (6 + i,), None),
                ("h", (i,), None), ("cx", (i, 6 + i), None),
                ("p", (ANC,), g / 4)]
    ops.append(("p", (ANC,), 4.5 * g))
    return ops

def hadamard_pub_ops(g, part, params, layers):
    ops = prep_ops(params, layers)
    ops.append(("h", (ANC,), None))
    ops += trotter_ops(-T, 0) + [("cx", (ANC, 0), None)] + trotter_ops(T, 0)      # c-A
    ops += c_eV_ops(g)
    ops += trotter_ops(T, 1) + [("cx", (ANC, 6), None)] + trotter_ops(-T, 1)      # c-B
    if part == "im":
        ops.append(("sdg", (ANC,), None))
    ops += [("h", (ANC,), None), ("measure_read", (ANC,), None)]
    return ops

# ---------------- 13-qubit exact walker ----------------
I2, X, Y, Z = rt.I2, rt.X, rt.Y, rt.Z
H1 = (X + Z) / np.sqrt(2)
SDG = np.diag([1, -1j]).astype(complex)
CX01 = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], complex)
_G2MEMO = {}
def g2(name, a):
    key = (name, float(a))
    if key in _G2MEMO: return _G2MEMO[key]
    G = {"rxx": np.kron(X, X), "ryy": np.kron(Y, Y), "rzz": np.kron(Z, Z)}[name]
    w, v = np.linalg.eigh(G)
    u = (v * np.exp(-1j * a / 2 * w)) @ v.conj().T
    _G2MEMO[key] = u
    return u

def a1(psi, u, q, n=13):
    t = psi.reshape([2] * n)
    t = np.moveaxis(np.tensordot(u, t, axes=([1], [q])), 0, q)
    return t.reshape(-1)

def a2(psi, u4, q1, q2, n=13):
    t = psi.reshape([2] * n)
    t = np.moveaxis(np.tensordot(u4.reshape(2, 2, 2, 2), t, axes=([2, 3], [q1, q2])),
                    [0, 1], [q1, q2])
    return t.reshape(-1)

def walk(ops):
    psi = np.zeros(2 ** 13, complex); psi[0] = 1.0
    for name, q, p in ops:
        if name == "h": psi = a1(psi, H1, q[0])
        elif name == "x": psi = a1(psi, X, q[0])
        elif name == "sdg": psi = a1(psi, SDG, q[0])
        elif name == "p": psi = a1(psi, np.diag([1, np.exp(1j * p)]), q[0])
        elif name == "rz": psi = a1(psi, np.diag([np.exp(-1j*p/2), np.exp(1j*p/2)]), q[0])
        elif name in ("rxx", "ryy", "rzz"): psi = a2(psi, g2(name, p), q[0], q[1])
        elif name == "cx": psi = a2(psi, CX01, q[0], q[1])
        elif name == "mcp":
            t = psi.reshape([2] * 13)
            idx = [slice(None)] * 13
            for qq in q: idx[qq] = 1
            t[tuple(idx)] = t[tuple(idx)] * np.exp(1j * p)
            psi = t.reshape(-1)
        elif name == "measure_read":
            t = psi.reshape([2] * 13)
            i0 = [slice(None)] * 13; i0[q[0]] = 0
            i1 = [slice(None)] * 13; i1[q[0]] = 1
            p0 = float(np.vdot(t[tuple(i0)].reshape(-1), t[tuple(i0)].reshape(-1)).real)
            p1 = float(np.vdot(t[tuple(i1)].reshape(-1), t[tuple(i1)].reshape(-1)).real)
            return p0 - p1
        else:
            raise ValueError(name)
    raise RuntimeError("no measure_read")

# ---------------- decode (frozen v2 arithmetic) ----------------
def decode(Cvals):
    fh = {S: sum(Cvals[k] * np.exp(-1j * G16[k] * S) for k in range(16)) / 16 for S in range(7)}
    ph = np.unwrap([np.angle(fh[S]) for S in (1, 2, 3, 4)])
    Am = np.vstack([[1, 2, 3, 4], np.ones(4)]).T
    alpha = float(-(np.linalg.pinv(Am) @ ph)[0] / 2)
    C = lambda g: abs(sum(fh[S] * np.exp(1j * g * S) for S in fh))
    return {"alpha_4pt": alpha, "R_unwind": float(C(GSTAR) / C(0)), "R_wrong": float(C(-GSTAR) / C(0)),
            "C0": float(C(0)), "lambda_hat": float(C(0) / BARS["registered"]["C0"]),
            "fhat": {str(S): [fh[S].real, fh[S].imag] for S in fh}}

# ---------------- KA gate ----------------
def circuit_C(params, layers, gs=G16):
    out = []
    for g in gs:
        re = walk(hadamard_pub_ops(g, "re", params, layers))
        im = walk(hadamard_pub_ops(g, "im", params, layers))
        out.append(complex(re, im))
    return np.array(out)

def ka_gate():
    Cw = circuit_C(PARAMS, LAYERS)
    Cop = np.array([complex(a, b) for a, b in BARS["Cmeas_flown_grid"]])
    k1 = float(np.max(np.abs(Cw - Cop)))
    dec = decode(Cw)
    reg = BARS["registered"]
    k2 = max(abs(dec["alpha_4pt"] - reg["alpha_4pt"]), abs(dec["R_unwind"] - reg["R_unwind"]),
             abs(dec["R_wrong"] - reg["R_wrong"]), abs(dec["C0"] - reg["C0"]))
    Cb = circuit_C(PARAMS * 0, LAYERS)
    dec0 = decode(Cb)
    k3 = abs(dec0["alpha_4pt"])
    ok = k1 < 1e-9 and k2 < 1e-6 and k3 < 1e-6
    print(f"KA: K1 circuit-vs-operator {k1:.2e} | K2 decode-vs-registered {k2:.2e} | "
          f"K3 beta0 alpha {k3:.2e}  -> {'PASS' if ok else 'FAIL'}")
    return ok

# ---------------- qiskit + submission ----------------
def to_qiskit(ops):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import MCPhaseGate
    qc = QuantumCircuit(13, 1)
    for name, q, p in ops:
        if name == "h": qc.h(q[0])
        elif name == "x": qc.x(q[0])
        elif name == "sdg": qc.sdg(q[0])
        elif name == "p": qc.p(p, q[0])
        elif name == "rz": qc.rz(p, q[0])
        elif name == "rxx": qc.rxx(p, q[0], q[1])
        elif name == "ryy": qc.ryy(p, q[0], q[1])
        elif name == "rzz": qc.rzz(p, q[0], q[1])
        elif name == "cx": qc.cx(q[0], q[1])
        elif name == "mcp": qc.append(MCPhaseGate(p, 2), [q[0], q[1], q[2]])
        elif name == "measure_read": qc.measure(q[0], 0)
    return qc

def build_stage_pubs(stage):
    pubs = []
    if stage == "S0":
        for part, n in (("re", 15000), ("im", 15000)):
            pubs.append((f"s0_g0_{part}", hadamard_pub_ops(0.0, part, PARAMS, LAYERS), n,
                         {"g": 0.0, "part": part, "arm": "pilot"}))
    elif stage == "S1":
        for k, g in enumerate(G16):
            if k == 0: continue
            for part in ("re", "im"):
                pubs.append((f"s1_g{k}_{part}", hadamard_pub_ops(g, part, PARAMS, LAYERS), 15000,
                             {"g": g, "part": part, "arm": "meter"}))
    elif stage == "S2":
        for k, g in enumerate(G16):
            for part in ("re", "im"):
                pubs.append((f"s2_g{k}_{part}", hadamard_pub_ops(g, part, PARAMS * 0, LAYERS), 10000,
                             {"g": g, "part": part, "arm": "beta0"}))
    return pubs

def alt2_service():
    # c4217_018 class fix (Elder's shared module): EXPLICITLY NAMED account, REFUSES fallback.
    # The old inline loader returned token=None on a missing env line -> silent default
    # instance -- a write that defaults GOES SOMEWHERE. Now it raises instead.
    sys.path.insert(0, SCRIPTS)
    from ibm_multi_account import service_for_submission
    return service_for_submission("IBMQ_ALT2")

def choose_backend(svc, need=13):
    cands = []
    for b in svc.backends():
        st = b.status()
        if not st.operational or b.configuration().n_qubits < need: continue
        cands.append((st.pending_jobs, b))
    cands.sort(key=lambda x: x[0])
    for pending, b in cands:
        props = b.properties()
        edges = {}
        for gate in props.gates:
            if len(gate.qubits) == 2:
                for p in gate.parameters:
                    if p.name == "gate_error":
                        e = tuple(sorted(gate.qubits))
                        edges[e] = min(edges.get(e, 1.0), p.value)
        if not edges: continue
        best = min(edges, key=edges.get)
        chain = list(best); used = set(chain)
        while len(chain) < need:
            exts = []
            for end, pos in ((chain[0], 0), (chain[-1], 1)):
                for e, err in edges.items():
                    if end in e:
                        nq = e[0] if e[1] == end else e[1]
                        if nq not in used: exts.append((err, nq, pos))
            if not exts: break
            exts.sort()
            err, nq, pos = exts[0]
            chain.insert(0, nq) if pos == 0 else chain.append(nq)
            used.add(nq)
        if len(chain) < need: continue
        errs = [edges[tuple(sorted((chain[i], chain[i+1])))] for i in range(need - 1)]
        med = float(np.median(errs))
        print(f"  {b.name}: pending={pending} median2q={med:.4f} max={max(errs):.4f}")
        if med <= 0.01:
            return b, chain, med, max(errs)
    return None, None, None, None

def fly(stage):
    if not ka_gate():
        sys.exit("KA GATE FAILED — NO SUBMISSION")
    svc = alt2_service()
    u = svc.usage()
    print(f"POOL RE-READ (ALT2): remaining {u['usage_remaining_seconds']}s of {u['usage_limit_seconds']}")
    backend, chain, med, mx = choose_backend(svc)
    if backend is None:
        sys.exit("CALIBRATION HOLD: no 13q chain passes 1% median 2q")
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    pubs = build_stage_pubs(stage)
    qcs = [to_qiskit(ops) for _, ops, _, _ in pubs]
    # ancilla at chain center (it must reach L0, R0 and all pair blocks)
    layout = {i: chain[2 * i + (0 if i < 3 else 1)] for i in range(6)}
    order = chain[:]
    anc_phys = order[len(order)//2]
    rest = [qq for qq in order if qq != anc_phys]
    init = {q: rest[q] for q in range(12)}; init[ANC] = anc_phys
    tq = transpile(qcs, backend, optimization_level=3, seed_transpiler=1104,
                   initial_layout=[init[q] for q in range(13)])
    n2q = [sum(1 for inst in t.data if len(inst.qubits) == 2) for t in tq]
    print(f"transpiled 2q counts: min {min(n2q)} median {int(np.median(n2q))} max {max(n2q)}")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, sh) for t, (_, _, sh, _) in zip(tq, pubs)])
    man = {"experiment": "h10_c1_winding_meter", "stage": stage, "cycle": "C5017",
           "protocol": "Amendment 3 Hadamard test",
           "bars": "results/h10_c1_prereg_bars_v2_c5017.json",
           "go": "Creator 'fly them' (ALT2)", "account": "ALT2 open-instance",
           "pool_remaining_at_submit_s": u["usage_remaining_seconds"],
           "backend": backend.name, "chain": chain, "anc_phys": anc_phys,
           "chain_2q_median": med, "chain_2q_max": mx,
           "pubs": [{"tag": tg, "shots": sh, **mt} for tg, _, sh, mt in pubs],
           "transpiled_2q_counts": n2q, "job_id": job.job_id(),
           "committer": "Whisper (DC15W)"}
    path = os.path.join(RESULTS, f"h10_c1_flight_{stage}_manifest.json")
    json.dump(man, open(path, "w"), indent=1)
    print(f"SUBMITTED {stage}: {job.job_id()} -> {path}")

def decode_stage(stage, job_id):
    svc = alt2_service()
    res = svc.job(job_id).result()
    man = json.load(open(os.path.join(RESULTS, f"h10_c1_flight_{stage}_manifest.json")))
    vals = {}
    for pub, pr in zip(man["pubs"], res):
        bits = pr.data.c.get_bitstrings()
        v = np.array([1 if s[-1] == "0" else -1 for s in bits])
        vals[(pub["g"], pub["part"])] = (float(v.mean()), math.sqrt(max(0.0, 1 - v.mean() ** 2) / len(v)))
    out = {"job_id": job_id, "stage": stage,
           "raw": {f"{g:.4f}_{p}": vals[(g, p)] for (g, p) in vals}}
    if stage == "S0":
        C0 = complex(vals[(0.0, "re")][0], vals[(0.0, "im")][0])
        se = math.hypot(vals[(0.0, "re")][1], vals[(0.0, "im")][1])
        lam = abs(C0) / BARS["registered"]["C0"]
        out.update({"C0_measured": [C0.real, C0.imag], "abs_C0": abs(C0),
                    "lambda_hat": lam, "se_lambda": se / BARS["registered"]["C0"],
                    "gate": ("FLY registered shots" if lam >= 0.35 else
                             f"RESCALE x{(0.35/lam)**2:.2f} (pool-gated)" if lam >= 0.15 else "NO-FLY")})
    path = os.path.join(RESULTS, f"h10_c1_flight_{stage}_decode.json")
    json.dump(out, open(path, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "raw"}, indent=1)); print("->", path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ka", action="store_true")
    ap.add_argument("--fly", choices=["S0", "S1", "S2"])
    ap.add_argument("--decode", nargs=2, metavar=("STAGE", "JOB_ID"))
    a = ap.parse_args()
    if a.ka: sys.exit(0 if ka_gate() else 1)
    if a.fly: fly(a.fly); sys.exit(0)
    if a.decode: decode_stage(a.decode[0], a.decode[1]); sys.exit(0)
    ap.print_help()
