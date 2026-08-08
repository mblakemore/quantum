#!/usr/bin/env python3
"""Exp142 Stage-1 FLIGHT KIT — Whisper C4746. FROZEN at prereg freeze (sha256 recorded).

Blind-protocol shape: state prep depends on the hidden P, so EMBER (sealed-committer)
runs this script with their secret file and submits the jobs. Whisper/Elder consume only
(a) outcome bitstrings and (b) the P-INDEPENDENT shot manifest this script emits
(arm, n, basis label index or 'bell', b strings, PUB layout). Honor protocol: decoders
never read the circuit definitions inside retrieved jobs (same-host blindness is honor
+ auditability, per Ember sealer commitments).

Modes:
  --selftest                      ideal-sim verification of angle tables + decoders (FREE)
  --scan --n 8                    build + transpile + count 2q + budget estimate (FREE)
  --submit-wave1 --n 8            EMBER ONLY: build from secret P, submit job
  --submit-wave2 --n 8 --alive f  EMBER ONLY: top-up PUBs for SPRT-uncrossed bases

Secret file (Ember's, chmod 600, off-git): ~/.ember-exp142-secrets.json
  {"fullweight_eps1": {"4": {"P": "XZYX", "salt_hex": "..."}, ...}}

Per-n job layout (ONE SamplerV2 job, co-batched, same window by construction):
  [sentinel_start(2q Bell, 400 shots),
   cal_block: 3 known Paulis x 100 shots (basis-matched) -> q_hat(n) source,
   quantum arm: 1 parameterized PUB, param rows = B_q shot-rows, shots=1,
   conventional wave1: parameterized PUB(s) chunked, 3^n basis rows, shots=12,
   sentinel_end(2q Bell, 400 shots)]
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter, ParameterVector

PAULIS = "XYZ"
WAVE1_SHOTS = 12
CAL_PAULIS = 3
CAL_SHOTS = 100
SENT_SHOTS = 400
# B_q(n) = 5 x m99_ideal(n), FREEZE-FILL from Gate-2 results:
BQ = {4: 60, 6: 80, 8: 90, 10: 110}  # FROZEN C4746
CONV_CHUNK_ROWS = 8192  # max param rows per PUB (payload safety)

# --------------------------------------------------------------- angle tables
# u(theta, phi, 0)|0> = cos(t/2)|0> + e^{i phi} sin(t/2)|1>
PREP_ANGLES = {  # (pauli, sign_bit) -> (theta, phi)
    ("Z", 0): (0.0, 0.0), ("Z", 1): (np.pi, 0.0),
    ("X", 0): (np.pi / 2, 0.0), ("X", 1): (np.pi / 2, np.pi),
    ("Y", 0): (np.pi / 2, np.pi / 2), ("Y", 1): (np.pi / 2, -np.pi / 2),
}
# pre-measure rotation mapping pauli-basis -> Z basis, as u(theta, phi, lam):
# X: H = u(pi/2, 0, pi); Y: H Sdg = u(pi/2, 0, pi/2); Z: I = u(0,0,0)
MEAS_ANGLES = {"X": (np.pi / 2, 0.0, np.pi), "Y": (np.pi / 2, 0.0, np.pi / 2),
               "Z": (0.0, 0.0, 0.0)}


def random_even_parity_bits(n, rng):
    b = rng.integers(0, 2, size=n)
    if b.sum() % 2:
        b[rng.integers(0, n)] ^= 1
    return b

# ------------------------------------------------------- parameterized circuits
def conv_template(n):
    """Prep u(tp,pp,0) per qubit + pre-measure u(tm,pm,lm) per qubit + measure."""
    qc = QuantumCircuit(n, n)
    tp = ParameterVector("tp", n); pp = ParameterVector("pp", n)
    tm = ParameterVector("tm", n); pm = ParameterVector("pm", n)
    lm = ParameterVector("lm", n)
    for i in range(n):
        qc.u(tp[i], pp[i], 0.0, i)
    qc.barrier()
    for i in range(n):
        qc.u(tm[i], pm[i], lm[i], i)
    qc.measure(range(n), range(n))
    params = list(tp) + list(pp) + list(tm) + list(pm) + list(lm)
    return qc, params


def conv_param_rows(P, bases, rng):
    """Rows for the conventional PUB: one row per candidate basis; per-row fresh even b.
    Returns (rows array, b_strings list)."""
    n = len(P)
    rows, bstrs = [], []
    for A in bases:
        b = random_even_parity_bits(n, rng)
        tp = [PREP_ANGLES[(P[i], int(b[i]))][0] for i in range(n)]
        pp = [PREP_ANGLES[(P[i], int(b[i]))][1] for i in range(n)]
        tm = [MEAS_ANGLES[A[i]][0] for i in range(n)]
        pm = [MEAS_ANGLES[A[i]][1] for i in range(n)]
        lm = [MEAS_ANGLES[A[i]][2] for i in range(n)]
        rows.append(tp + pp + tm + pm + lm)
        bstrs.append("".join(map(str, b)))
    return np.array(rows), bstrs


def quantum_template(n):
    """Two copies prep (parameterized u per qubit) + transversal Bell measure."""
    qc = QuantumCircuit(2 * n, 2 * n)
    tp = ParameterVector("qt", 2 * n); pp = ParameterVector("qp", 2 * n)
    for i in range(2 * n):
        qc.u(tp[i], pp[i], 0.0, i)
    qc.barrier()
    for i in range(n):
        qc.cx(i, n + i)
        qc.h(i)
    qc.measure(range(2 * n), range(2 * n))
    return qc, list(tp) + list(pp)


def quantum_param_rows(P, n_rows, rng):
    n = len(P)
    rows, bstrs = [], []
    for _ in range(n_rows):
        b1 = random_even_parity_bits(n, rng)
        b2 = random_even_parity_bits(n, rng)
        bb = np.concatenate([b1, b2])
        tp = [PREP_ANGLES[(P[i % n], int(bb[i]))][0] for i in range(2 * n)]
        pp = [PREP_ANGLES[(P[i % n], int(bb[i]))][1] for i in range(2 * n)]
        rows.append(tp + pp)
        bstrs.append("".join(map(str, b1)) + "|" + "".join(map(str, b2)))
    return np.array(rows), bstrs


def sentinel_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


# ----------------------------------------------------- calibration-gated layout
def pick_layouts(backend, n):
    """Quantum arm = n DISJOINT low-cost edges (Bell pairs never interact);
    conventional arm = n min-readout qubits. Greedy, calibration-gated
    (F57/F58 lineage, exp138 pick_chain5 adapted)."""
    target = backend.target
    twoq = "cz" if "cz" in target.operation_names else "ecr"
    ro = {}
    for (q,) in target["measure"].keys():
        ro[q] = target["measure"][(q,)].error or 0.0
    edge_cost = []
    for (a, b), inst in target[twoq].items():
        e = getattr(inst, "error", None)
        if e is None:
            continue
        edge_cost.append((e + ro.get(a, 0) + ro.get(b, 0), a, b))
    edge_cost.sort()
    used, pairs = set(), []
    for cost, a, b in edge_cost:
        if a in used or b in used:
            continue
        pairs.append((a, b))
        used.update((a, b))
        if len(pairs) == n:
            break
    # quantum layout: copy-1 qubit i -> pairs[i][0], copy-2 qubit n+i -> pairs[i][1]
    q_layout = [p[0] for p in pairs] + [p[1] for p in pairs]
    conv_layout = sorted(ro, key=ro.get)[:n]
    return q_layout, conv_layout, pairs

# ------------------------------------------------------------------- self-test
def selftest():
    """Ideal-sim checks catching any angle-table error (no memory trust)."""
    from qiskit_aer import AerSimulator
    import exp142_robust_decoder_sim as g2
    rng = np.random.default_rng(1421)
    sim = AerSimulator()
    n = 4
    P = "XZYY"
    # 1) conventional: true basis parity ALWAYS even (rel. to b); wrong basis ~uniform
    qc, params = conv_template(n)
    bases = [P, "XZYX", "ZZZZ"]
    rows, bstrs = conv_param_rows(P, bases, rng)
    for k, A in enumerate(bases):
        bound = qc.assign_parameters(dict(zip(params, rows[k])))
        counts = sim.run(bound, shots=400).result().get_counts()
        b = np.array([int(c) for c in bstrs[k]])
        odd = sum(v for key, v in counts.items()
                  if (np.array([int(c) for c in key.replace(' ', '')[::-1]]).sum()
                      - b.sum()) % 2 == 1)
        rate = odd / 400
        if A == P:
            assert rate == 0.0, f"true basis odd rate {rate}"
        else:
            assert 0.35 < rate < 0.65, f"wrong basis {A} odd rate {rate}"
    print("  selftest 1 (conventional angle table): PASS")
    # 2) quantum arm: Gate-2 ML decoder recovers P from ideal parameterized circuits
    mapping = g2.calibrate_bell_mapping()
    csign = g2.calibrate_constraint_sign(mapping)
    qqc, qparams = quantum_template(n)
    rows, _ = quantum_param_rows(P, 40, rng)
    shots_bits = []
    for r in rows:
        bound = qqc.assign_parameters(dict(zip(qparams, r)))
        res = sim.run(bound, shots=1, memory=True).result().get_memory()[0]
        shots_bits.append(g2.outcome_to_bits(res, n, mapping))
    cands, cand_M, ypar = g2.candidate_matrix(n)
    curve = g2.decode_success_curve(
        np.array(shots_bits), cands.index(tuple(P)), cand_M, ypar, csign, n,
        grid=[20, 30, 40])
    assert curve[40] == 1, f"quantum decoder failed: {curve}"
    print("  selftest 2 (quantum arm + Gate-2 decoder on parameterized circuits): PASS")
    # 3) AMENDMENT A1 (C4747) regression: bindings through the REAL pub-tuple path.
    # StatevectorSampler coerces pubs exactly like runtime SamplerV2; a positional
    # (raw-ndarray) binding scrambles angles and fails these deterministic checks.
    from qiskit.primitives import StatevectorSampler
    sv = StatevectorSampler(seed=7)
    # 3a) conventional/cal: true-basis parity must be even for every shot
    r_true, bs_true = conv_param_rows(P, [P], rng)
    res = sv.run([(qc, named_rows(params, r_true), 200)]).result()[0]
    reg = list(res.data.keys())[0] if hasattr(res.data, "keys") else "c"
    bits = getattr(res.data, reg).get_bitstrings()
    b = np.array([int(c) for c in bs_true[0]])
    odd = sum((np.array([int(c) for c in s.replace(' ', '')[::-1][:n]]).sum()
               - b.sum()) % 2 for s in bits)
    assert odd == 0, f"pub-path true-basis odd rate {odd}/200 (binding scramble?)"
    # 3b) quantum: per-row deterministic Bell bits. X qubit -> clbit i == b1^b2
    # (XX correlation); Z qubit -> clbit n+i == b1^b2 (ZZ correlation). A qt/qp
    # swap turns X preps computational and drops Z sign bits -> both checks fail.
    qqc2, qparams2 = quantum_template(n)
    qrows2, qbstrs2 = quantum_param_rows(P, 20, rng)
    res2 = sv.run([(qqc2, named_rows(qparams2, qrows2), 4)]).result()[0]
    reg2 = list(res2.data.keys())[0] if hasattr(res2.data, "keys") else "c"
    bits2 = getattr(res2.data, reg2).get_bitstrings()
    for row_i, bstr in enumerate(qbstrs2):
        b1, b2 = bstr.split("|")
        expect = [int(b1[i]) ^ int(b2[i]) for i in range(n)]
        for s in bits2[row_i * 4:(row_i + 1) * 4]:
            v = s.replace(" ", "")[::-1]  # v[k] = clbit k
            for i in range(n):
                if P[i] == "X":
                    assert int(v[i]) == expect[i], \
                        f"row {row_i} qubit {i} X-corr mismatch (binding scramble?)"
                elif P[i] == "Z":
                    assert int(v[n + i]) == expect[i], \
                        f"row {row_i} qubit {i} Z-corr mismatch (binding scramble?)"
    print("  selftest 3 (REAL pub-tuple binding path via StatevectorSampler): PASS")
    print("SELFTEST PASS")


# ------------------------------------------------------------------ job builder
def named_rows(params, rows):
    """AMENDMENT A1 (C4747): bind parameter rows BY NAME, never positionally.

    Raw ndarrays in a SamplerV2 pub tuple are coerced positionally against
    circuit.parameters, which is sorted ALPHABETICALLY (lm,pm,pp,tm,tp) — not
    template order (tp,pp,tm,pm,lm). Wave-1 flew with that scramble: every
    parameterized circuit had wrong angles (cal q_hat=0.70, deterministic-flip
    signatures on hardware; sentinels clean because parameterless). Dict-keyed
    BindingsArray binds by name and is order-immune."""
    return {tuple(p.name for p in params): rows}


def build_job(n, P, rng, alive_bases=None, wave=1):
    """Returns (pubs, manifest). PUB = (circuit, named_rows|None, shots)."""
    pubs, manifest = [], {"n": n, "wave": wave, "pubs": []}
    if wave == 1:
        pubs.append((sentinel_circuit(), None, SENT_SHOTS))
        manifest["pubs"].append({"kind": "sentinel_start", "shots": SENT_SHOTS})
        # calibration block: known Paulis, basis-matched (q_hat source)
        cal_paulis = ["".join(rng.choice(list(PAULIS), size=n)) for _ in range(CAL_PAULIS)]
        qc, params = conv_template(n)
        cal_rows, cal_b = conv_param_rows(cal_paulis[0], [cal_paulis[0]], rng)
        for cp in cal_paulis:
            r, bs = conv_param_rows(cp, [cp], rng)
            pubs.append((qc, named_rows(params, r), CAL_SHOTS))
            manifest["pubs"].append({"kind": "cal", "pauli": cp, "b": bs[0],
                                     "shots": CAL_SHOTS})
        # quantum arm
        qqc, qparams = quantum_template(n)
        qrows, qb = quantum_param_rows(P, BQ[n], rng)
        pubs.append((qqc, named_rows(qparams, qrows), 1))
        manifest["pubs"].append({"kind": "quantum", "rows": BQ[n], "b": qb, "shots": 1})
        bases = ["".join(t) for t in itertools.product(PAULIS, repeat=n)]
    else:
        bases = alive_bases
    # conventional arm (wave 1 = all bases; wave 2 = alive only)
    qc, cparams = conv_template(n)
    rows, bstrs = conv_param_rows(P, bases, rng)
    for lo in range(0, len(rows), CONV_CHUNK_ROWS):
        chunk = rows[lo:lo + CONV_CHUNK_ROWS]
        pubs.append((qc, named_rows(cparams, chunk), WAVE1_SHOTS))
        manifest["pubs"].append({"kind": f"conv_wave{wave}", "row_lo": lo,
                                 "rows": len(chunk), "shots": WAVE1_SHOTS})
    manifest["conv_bases_order"] = "itertools.product XYZ repeat=n" if wave == 1 \
        else f"alive list ({len(bases)})"
    manifest["conv_b_strings"] = bstrs
    if wave == 1:
        pubs.append((sentinel_circuit(), None, SENT_SHOTS))
        manifest["pubs"].append({"kind": "sentinel_end", "shots": SENT_SHOTS})
    return pubs, manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit-wave1", action="store_true")
    ap.add_argument("--submit-wave2", action="store_true")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--alive", type=str, help="json file of alive bases (wave2)")
    ap.add_argument("--backend", default="ibm_marrakesh")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return 0

    n = args.n
    if BQ[n] is None:
        print("FLIGHT KIT NOT FROZEN: BQ unfilled from Gate-2")
        return 2
    rng = np.random.default_rng()  # flight randomness: OS entropy fine here

    if args.scan:
        P = "".join(np.random.default_rng(0).choice(list(PAULIS), size=n))  # dummy
        pubs, manifest = build_job(n, P, rng)
        tot = sum((p[2] * (1 if p[1] is None else len(p[1]))) for p in pubs)
        print(f"n={n}: {len(pubs)} PUBs, total shots {tot} (dummy P; FREE scan)")
        return 0

    # EMBER-ONLY paths below
    sec_path = os.path.expanduser("~/.ember-exp142-secrets.json")
    with open(sec_path) as f:
        P = json.load(f)["fullweight_eps1"][str(n)]["P"]
    alive = None
    if args.submit_wave2:
        with open(args.alive) as f:
            alive = json.load(f)["alive_bases"]
    wave = 2 if args.submit_wave2 else 1
    pubs, manifest = build_job(n, P, rng, alive_bases=alive, wave=wave)

    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2, QiskitRuntimeService
    # ── C4262: explicit account pin (Ember). This module's own __main__ path had a bare
    # service one import deep — the defect that put six exp142 jobs on a flagged
    # accepts-but-never-runs account on 2026-08-08. Same guard as the exp142c submit path,
    # applied here rather than argued to be unreachable: "reachable but not executed" is a
    # control-flow claim the AST cannot check and I should not be trusted to assert.
    import re as _re
    PAID_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
                "a/65155eedeb8b464eadf55d101fb3c931:27609585-d5b2-43cb-808d-2d47aeb87c05::")
    _tok = None
    for _line in open("/droid/repos/DC15W/.env"):
        _m = _re.match(r"^IBMQ_TOKEN=(.+)$", _line.strip())
        if _m:
            _tok = _m.group(1).strip().strip('"').strip("'"); break
    if not _tok:
        raise SystemExit("REFUSE: IBMQ_TOKEN not found")
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=_tok,
                               instance=PAID_CRN)
    _u = svc.usage()
    if _u["instance_id"] != PAID_CRN or _u["usage_limit_reached"]:
        raise SystemExit(f"REFUSE G-CRN: {_u['instance_id'][-24:]} "
                         f"flagged={_u['usage_limit_reached']}")
    backend = svc.backend(args.backend)
    if backend.name != "ibm_fez":
        raise SystemExit(f"REFUSE G-BACKEND: {backend.name}, exp142's venue is ibm_fez")
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    q_layout, conv_layout, bell_pairs = pick_layouts(backend, n)
    print(f"Layouts: quantum Bell pairs {bell_pairs}, conventional {conv_layout}")
    manifest["bell_pairs"] = bell_pairs
    manifest["conv_layout"] = conv_layout
    tpubs = []
    for (qc, rows, shots), meta in zip(pubs, manifest["pubs"]):
        kind = meta["kind"]
        if kind == "quantum":
            il = q_layout
        elif kind.startswith("conv") or kind == "cal":
            il = conv_layout
        else:
            il = list(bell_pairs[0])  # sentinel on the best edge
        tqc = transpile(qc, backend, initial_layout=il,
                        optimization_level=1, seed_transpiler=142)
        tpubs.append((tqc, rows, shots) if rows is not None else (tqc, None, shots))
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, r, s) if r is not None else (t, None, s)
                       for t, r, s in tpubs])
    jid = job.job_id()
    manifest["job_id"] = jid
    manifest["backend"] = args.backend
    outp = os.path.join(HERE, "..", "results",
                        f"exp142_wave{wave}_n{n}_manifest.json")
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"Submitted wave{wave} n={n}: job_id={jid}\nManifest -> {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
