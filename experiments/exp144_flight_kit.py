#!/usr/bin/env python3
"""Exp144 FLIGHT KIT (freeze candidate — sha256 recorded at freeze).

Blind-protocol shape (Exp142 lineage): the V = e^{-iHt} gadget depends on the hidden
instance, so EMBER builds/submits from the secret file. The manifest this script
emits is INSTANCE-INDEPENDENT (PUB layout, shots, layouts only). Decoders consume
outcome bitstrings + manifest, never circuit definitions.

Quantum arm per (n, k) instance — ONE co-batched SamplerV2 job:
  [sentinel_start (2q Bell, 400 shots),
   quantum PUB: n Bell pairs + V on system half + transversal Bell measure,
                FIXED circuit (no per-shot rows), shots = N_BELL_BUDGET[n],
   sentinel_end (2q Bell, 400 shots)]
Sign-block wave (AFTER decoders publish accepted support — support is public then):
   per accepted term: iQP-eigenstate prep + V + Q letter-basis measure, N_SIGN shots.
Conventional arm: candidate-sweep PUBs (§4): iQP'-eigenstate prep + V + Q measure,
   SPRT-metered by the decode side; wave-batched like Exp142 §4.

FULL-WEIGHT STRUCTURE = SECRET-INDEPENDENT CIRCUIT SHAPE: every term's rotation
gadget spans all n system qubits (basis-change layer + CNOT ladder + Rz + reverse),
so the transpiled STRUCTURE leaks nothing; the secret enters only via u/rz ANGLES.

Modes:
  --selftest       G2.1 LAW CHECK: StatevectorSampler through the REAL pub path
                   (C4747 A1 lesson) -> exp144_decode_meter.decode -> recover a
                   known instance end-to-end. FREE, no backend.
  --scan --n 8     transpile-free structure + duration estimate (fingerprint arm input)
"""
import argparse
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector

from exp144_decode_meter import shots_to_labels, decode, T_FROZEN

NS = (4, 6, 8)
KS = (1, 2, 3, 4, 5)
M = 3
N_BELL_BUDGET = {4: 5000, 6: 5000, 8: 5000}   # 5 x m_bell, FROZEN C6508
N_SIGN = 100                                   # per accepted term, per instance
SENT_SHOTS = 400
COEFF_GRID = (0.15, 0.20, 0.25)

# basis-change angles: rotate letter-basis -> Z basis (u(theta,phi,lam)), and back
TO_Z = {"X": (math.pi / 2, 0.0, math.pi), "Y": (math.pi / 2, 0.0, math.pi / 2),
        "Z": (0.0, 0.0, 0.0)}
FROM_Z = {"X": (math.pi / 2, 0.0, math.pi),                       # H self-inverse
          "Y": (math.pi / 2, math.pi / 2, math.pi),               # S H = u(pi/2,pi/2,pi)
          "Z": (0.0, 0.0, 0.0)}


def rotation_block(qc, qubits, letters, angle):
    """exp(-i angle/2 * P) on `qubits` with letter string `letters` (full weight):
    basis change to Z^n, CNOT ladder, RZ(angle) on last, un-ladder, un-change."""
    for q, c in zip(qubits, letters):
        t, p, l = TO_Z[c]
        qc.u(t, p, l, q)
    for a, b in zip(qubits[:-1], qubits[1:]):
        qc.cx(a, b)
    qc.rz(angle, qubits[-1])
    for a, b in reversed(list(zip(qubits[:-1], qubits[1:]))):
        qc.cx(a, b)
    for q, c in zip(qubits, letters):
        t, p, l = FROM_Z[c]
        qc.u(t, p, l, q)


def quantum_circuit(n, terms, thetas):
    """n Bell pairs (sys i, ref n+i); V = prod_j exp(-i theta_j P_j) on sys half;
    transversal Bell measure. theta_j = c_j * t."""
    qc = QuantumCircuit(2 * n, 2 * n)
    for i in range(n):
        qc.h(i); qc.cx(i, n + i)
    qc.barrier()
    for lab, th in zip(terms, thetas):
        rotation_block(qc, list(range(n)), lab, 2 * th)   # exp(-i th P): RZ(2*th)
    qc.barrier()
    for i in range(n):
        qc.cx(i, n + i); qc.h(i)
    qc.measure(range(2 * n), range(2 * n))
    return qc


def signblock_circuit(n, terms, thetas, target_idx, probe, prep_letters, prep_signs):
    """Single-copy: prep product eigenstate of iQP (letters+signs precomputed by
    the decode side), apply V, measure probe Q in its letter basis."""
    qc = QuantumCircuit(n, n)
    PREP = {("Z", 0): (0.0, 0.0), ("Z", 1): (math.pi, 0.0),
            ("X", 0): (math.pi / 2, 0.0), ("X", 1): (math.pi / 2, math.pi),
            ("Y", 0): (math.pi / 2, math.pi / 2), ("Y", 1): (math.pi / 2, -math.pi / 2)}
    for i, (c, s) in enumerate(zip(prep_letters, prep_signs)):
        if c == "I":
            continue
        t, p = PREP[(c, s)]
        qc.u(t, p, 0.0, i)
    qc.barrier()
    for lab, th in zip(terms, thetas):
        rotation_block(qc, list(range(n)), lab, 2 * th)
    qc.barrier()
    for i, c in enumerate(probe):
        if c != "I":
            t, p, l = TO_Z[c]
            qc.u(t, p, l, i)
    qc.measure(range(n), range(n))
    return qc


def sentinel_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


# ------------------------------------------------- conventional arm (§4) — F1
# Pauli single-qubit products with phase: sa*sb = phase * sc
_PROD = {("X", "Y"): ("Z", 1j), ("Y", "X"): ("Z", -1j),
         ("Y", "Z"): ("X", 1j), ("Z", "Y"): ("X", -1j),
         ("Z", "X"): ("Y", 1j), ("X", "Z"): ("Y", -1j)}


def pauli_prod_phase(a, b):
    """(label, phase) of the string product a*b, phase in {1,-1,i,-i}."""
    lab, ph = [], 1 + 0j
    for x, y in zip(a, b):
        if x == "I": lab.append(y)
        elif y == "I": lab.append(x)
        elif x == y: lab.append("I")
        else:
            c, p = _PROD[(x, y)]
            lab.append(c); ph *= p
    return "".join(lab), ph


def prep_for_iqp(probe, cand):
    """Product eigenstate of iQP (+1), by ALGEBRA (public, decoder-reproducible;
    matrix-free — the selftest cross-checks this against matrices, per the
    known-answer-vs-ground-truth rule). Returns (letters S, sign_bits)."""
    S, ph = pauli_prod_phase(probe, cand)
    coef = 1j * ph                     # iQP = coef * S; {Q,P}=0 -> coef real +-1
    assert abs(coef.imag) < 1e-12, "probe must anticommute with candidate"
    signs = [0] * len(S)
    if coef.real < 0:
        signs[next(i for i, c in enumerate(S) if c != "I")] = 1
    return S, signs


def conv_candidates(n, seed=None):
    """SEALED-SEEDED candidate order (F2b, chair ruling C4776 option (a)):
    all 3^n full-weight strings, lexicographic then shuffled by the PER-RUNG
    seed Ember seals as exp144-convseed-commit-v1 (revealed with the rest —
    a verifiable pre-commitment, not a post-hoc claim). seed=None is the
    SELFTEST-ONLY deterministic fallback tag."""
    import hashlib as _h
    cands = ["".join(p) for p in itertools.product("XYZ", repeat=n)]
    if seed is None:                      # selftest fallback, never flown
        seed = int.from_bytes(
            _h.sha256(f"exp144|conv-order-selftest|{n}".encode()).digest()[:8], "big")
    rng = np.random.default_rng(int(seed))
    rng.shuffle(cands)
    return cands


def conv_probe(cand, wave, site_stride=1):
    """Deterministic single-site sweep probe for candidate (wave-rotated site &
    letter — the §4 randomization across waves). Detection only; coeff
    refinement uses constrained probes post-identification."""
    n = len(cand)
    site = (wave - 1) % n
    letters = [c for c in "XYZ" if c != cand[site]]
    q = ["I"] * n
    q[site] = letters[(wave - 1) // n % 2]
    return "".join(q)


def conv_template(n):
    """Parameterized: prep u(tp,pp,0) per qubit + V blocks (concrete secret
    angles baked at build) + pre-measure u(tm,pm,lm) per qubit + measure.
    Rows bound BY NAME (C4747 A1 — never positional)."""
    from qiskit.circuit import ParameterVector
    qc = QuantumCircuit(n, n)
    tp = ParameterVector("tp", n); pp = ParameterVector("pp", n)
    tm = ParameterVector("tm", n); pm = ParameterVector("pm", n)
    lm = ParameterVector("lm", n)
    for i in range(n):
        qc.u(tp[i], pp[i], 0.0, i)
    qc.barrier()
    return qc, (tp, pp, tm, pm, lm)


def build_conv_circuit(n, terms, thetas):
    qc, (tp, pp, tm, pm, lm) = conv_template(n)
    for lab, th in zip(terms, thetas):
        rotation_block(qc, list(range(n)), lab, 2 * th)
    qc.barrier()
    for i in range(n):
        qc.u(tm[i], pm[i], lm[i], i)
    qc.measure(range(n), range(n))
    return qc, list(tp) + list(pp) + list(tm) + list(pm) + list(lm)


PREP_U = {("Z", 0): (0.0, 0.0), ("Z", 1): (math.pi, 0.0),
          ("X", 0): (math.pi / 2, 0.0), ("X", 1): (math.pi / 2, math.pi),
          ("Y", 0): (math.pi / 2, math.pi / 2), ("Y", 1): (math.pi / 2, -math.pi / 2),
          ("I", 0): (0.0, 0.0), ("I", 1): (0.0, 0.0)}


def conv_param_row(n, cand, wave):
    """One named row: prep iQP'(+1) eigenstate, measure probe letters.
    GAUGE RANDOMIZATION (C6514 fix): the +1 eigenspace has sign-pattern freedom —
    any EVEN-weight flip of non-I site signs preserves the iQP eigenvalue while
    flipping cross-term expectations. Randomizing it per (cand, wave) averages
    cross-term contamination to zero (the debug data showed sign-flipping planted
    signals and strong per-wave NULL signals without it); the target
    −sin(2ct)·⟨iQP⟩ is gauge-invariant. Same trick, same reason as Exp142's
    random_even_parity_bits."""
    probe = conv_probe(cand, wave)
    S, signs = prep_for_iqp(probe, cand)
    import hashlib as _h
    seed = int.from_bytes(_h.sha256(f"gauge|{cand}|{wave}".encode()).digest()[:8], "big")
    grng = np.random.default_rng(seed)
    sites = [i for i, c in enumerate(S) if c != "I"]
    flip = grng.integers(0, 2, size=len(sites))
    if flip.sum() % 2:
        flip[grng.integers(0, len(sites))] ^= 1
    for i, f in zip(sites, flip):
        signs[i] ^= int(f)
    tp = [PREP_U[(c, s)][0] for c, s in zip(S, signs)]
    pp = [PREP_U[(c, s)][1] for c, s in zip(S, signs)]
    tm = [TO_Z[c][0] if c != "I" else 0.0 for c in probe]
    pm = [TO_Z[c][1] if c != "I" else 0.0 for c in probe]
    lm = [TO_Z[c][2] if c != "I" else 0.0 for c in probe]
    return tp + pp + tm + pm + lm, probe


# --- AMENDMENT A2 (Elder C6526, chair C4789b): constants SYNCED to frozen §5 ---
# (F-B fix: the freeze carried pre-MC-v2 values here; §5 prose was normative.
#  Old: CONV_WAVE_SHOTS=12, S1_SHOTS=30, S2_FAMILY=8, S2_SHOTS=48.
#  New hash recorded in exp144_amendment_a2_elder_c6526.md; P1 sibling-verified.)
CONV_WAVE_SHOTS = 60   # stage-1 SPRT wave size/candidate (accumulate, cap S1_CAP)
CONV_CHUNK_ROWS = 4096
S1_SHOTS = 60          # per-wave stage-1 shots (SPRT alpha=.05 beta=.01 decode-side)
S1_CAP = 800           # max cumulative stage-1 shots/candidate (== frozen §5 line 228; A2-rev1 fix, sibling-verify catch C4790)
S2_FAMILY = 12         # stage-2 probe family size (frozen §5 / MC v2)
S2_SHOTS = 500         # stage-2 shots per (survivor, probe) (frozen §5 / MC v2)


def conv_stage1_row(n, cand):
    """Stage-1 CONSERVATION row: prep +1 product eigenstate of the candidate
    itself, evolve V, measure the candidate in its letter basis. Outcome
    (product of letter bits) = +1 EXACTLY iff [cand, H] = 0 (noiseless) —
    deterministic, contamination-free (two-stage detector, C6515 2-of-2 algebra)."""
    tp = [PREP_U[(c, 0)][0] for c in cand]
    pp = [PREP_U[(c, 0)][1] for c in cand]
    tm = [TO_Z[c][0] for c in cand]
    pm = [TO_Z[c][1] for c in cand]
    lm = [TO_Z[c][2] for c in cand]
    return tp + pp + tm + pm + lm


def build_conv_stage1_job(n, k, terms, coeffs, t=T_FROZEN, seed=None):
    """One co-batched stage-1 job: every candidate in sealed-seeded order,
    S1_SHOTS each. Rejects the anticommuting ~7/8 cheaply and exactly."""
    thetas = [c * t for c in coeffs]
    cands = conv_candidates(n, seed)
    qc, params = build_conv_circuit(n, terms, thetas)
    pubs = [(sentinel_circuit(), None, SENT_SHOTS)]
    manifest = {"n": n, "k": k, "arm": "conv_stage1",
                "pubs": [{"kind": "sentinel_start", "shots": SENT_SHOTS}]}
    row_meta = []
    for lo in range(0, len(cands), CONV_CHUNK_ROWS):
        chunk = cands[lo:lo + CONV_CHUNK_ROWS]
        rows = [conv_stage1_row(n, c) for c in chunk]
        pubs.append((qc, named_rows(params, rows), S1_SHOTS))
        manifest["pubs"].append({"kind": "conv_stage1", "rows": len(chunk),
                                 "shots": S1_SHOTS})
        row_meta.extend({"cand": c} for c in chunk)
    pubs.append((sentinel_circuit(), None, SENT_SHOTS))
    manifest["pubs"].append({"kind": "sentinel_end", "shots": SENT_SHOTS})
    return pubs, manifest, row_meta


def named_rows(params, rows):
    """Bind by NAME (C4747 A1: raw ndarrays coerce positionally — the wave-1
    binding-scramble class)."""
    arr = np.asarray(rows, dtype=float)
    return {p.name: arr[:, i] for i, p in enumerate(params)}


def build_conv_job(n, k, terms, coeffs, wave=1, alive=None, t=T_FROZEN, seed=None):
    """(pubs, manifest, row_meta). alive = candidate subset for top-up waves
    (SPRT-open only); wave 1 = full sealed-seeded order (per-rung seed, C4776)."""
    thetas = [c * t for c in coeffs]
    cands = alive if alive is not None else conv_candidates(n, seed)
    qc, params = build_conv_circuit(n, terms, thetas)
    pubs, manifest, row_meta = [], {"n": n, "k": k, "arm": "conventional",
                                    "wave": wave, "pubs": []}, []
    pubs.append((sentinel_circuit(), None, SENT_SHOTS))
    manifest["pubs"].append({"kind": "sentinel_start", "shots": SENT_SHOTS})
    for lo in range(0, len(cands), CONV_CHUNK_ROWS):
        chunk = cands[lo:lo + CONV_CHUNK_ROWS]
        rows, probes = [], []
        for cnd in chunk:
            r, probe = conv_param_row(n, cnd, wave)
            rows.append(r); probes.append(probe)
        pubs.append((qc, named_rows(params, rows), CONV_WAVE_SHOTS))
        manifest["pubs"].append({"kind": f"conv_wave{wave}", "rows": len(chunk),
                                 "shots": CONV_WAVE_SHOTS})
        row_meta.extend({"cand": c, "probe": p} for c, p in zip(chunk, probes))
    pubs.append((sentinel_circuit(), None, SENT_SHOTS))
    manifest["pubs"].append({"kind": "sentinel_end", "shots": SENT_SHOTS})
    return pubs, manifest, row_meta


def build_quantum_job(n, terms, coeffs, t=T_FROZEN):
    """(pubs, manifest) for one instance's quantum-arm job. Manifest is
    instance-independent: layout + shots only."""
    thetas = [c * t for c in coeffs]
    pubs = [(sentinel_circuit(), None, SENT_SHOTS),
            (quantum_circuit(n, terms, thetas), None, N_BELL_BUDGET[n]),
            (sentinel_circuit(), None, SENT_SHOTS)]
    manifest = {"n": n, "arm": "quantum",
                "pubs": [{"kind": "sentinel_start", "shots": SENT_SHOTS},
                         {"kind": "bell", "shots": N_BELL_BUDGET[n]},
                         {"kind": "sentinel_end", "shots": SENT_SHOTS}]}
    return pubs, manifest


def duration_estimate(n, backend_1q_ns=32, backend_2q_ns=68, ro_ns=1500):
    """Gate-count duration estimate for the fingerprint-arm selection (§8):
    per term: 2n u + 2(n-1) cx + 1 rz(virtual); 3 terms; + Bell prep/measure."""
    oneq = 2 * n * M + 2 * n + 2 * n        # basis changes + bell prep/meas H's
    twoq = 2 * (n - 1) * M + 2 * n          # ladders + bell prep/meas CXs
    ns = oneq * backend_1q_ns + twoq * backend_2q_ns + ro_ns
    return {"n": n, "1q": oneq, "2q": twoq, "est_us": round(ns / 1000, 2)}


# ------------------------------------------------------------------- selftest
def selftest():
    """G2.1: the REAL pub path (StatevectorSampler coerces pubs exactly like
    runtime SamplerV2) -> real decode_meter -> known instance recovered."""
    from qiskit.primitives import StatevectorSampler
    rng = np.random.default_rng(20260717)
    ok_all = True
    # known commuting mult-independent full-weight instance at n=4
    cases = [(4, ["XXXX", "XXYY", "XXZZ"], [0.15, -0.20, 0.25]),
             (4, ["YYYY", "YYXX", "YYZZ"], [-0.25, 0.15, 0.20])]
    sampler = StatevectorSampler(seed=7)
    for n, terms, coeffs in cases:
        thetas = [c * T_FROZEN for c in coeffs]
        pubs, _ = build_quantum_job(n, terms, coeffs)
        job = sampler.run(pubs, shots=None)
        res = job.result()
        bell = res[1].data.c.get_bitstrings() if hasattr(res[1].data, "c") else \
            res[1].data.meas.get_bitstrings()
        labels = shots_to_labels(bell, n)
        dec = decode(labels, n, len(bell))
        want = sorted(terms)
        got = sorted(dec["support"])
        sup_ok = got == want
        mag_ok = sup_ok and all(
            abs(dec["abs_coeffs"][lab] - abs(c)) <= 0.03
            for lab, c in zip(terms, coeffs))
        grp_ok = dec["off_group_mass"] < 0.005
        cons_ok = all(c["ok"] for c in dec["consistency"])
        ok = sup_ok and mag_ok and grp_ok and cons_ok
        ok_all &= ok
        print(f"  n={n} {terms} c={coeffs}: support {'OK' if sup_ok else got} "
              f"| |c| max err {max(abs(dec['abs_coeffs'][l] - abs(c)) for l, c in zip(terms, coeffs)) if sup_ok else float('nan'):.4f} "
              f"| off-group {dec['off_group_mass']:.4f} | consistency "
              f"{'OK' if cons_ok else 'FAIL'} -> {'PASS' if ok else 'FAIL'}")
    # sign block law: planted term readout = -sin(2 theta) via the REAL circuit
    n, terms, coeffs = cases[0]
    thetas = [c * T_FROZEN for c in coeffs]
    # probe for term 0 (XXXX): anticommute with it, commute with XXYY, XXZZ.
    # ZZII: vs XXXX 2 anti (even->commute) — need odd. YXII: vs XXXX qubit0 anti
    # -> 1 anti (odd, anticommutes); vs XXYY qubit0 anti only -> anticommutes. Bad.
    # Use ZYZY: vs XXXX 4 anti (comm). Systematic search instead:
    def commutes(a, b):
        return sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y) % 2 == 0
    probe = next("".join(p) for p in itertools.product("IXYZ", repeat=n)
                 if set(p) != {"I"}
                 and not commutes("".join(p), terms[0])
                 and all(commutes("".join(p), tt) for tt in terms[1:]))
    # prep letters/signs for +1 eigenstate of iQP computed via matrix (selftest only)
    import functools
    I2 = np.eye(2, dtype=complex)
    PM = {"I": I2, "X": np.array([[0, 1], [1, 0]], complex),
          "Y": np.array([[0, -1j], [1j, 0]], complex),
          "Z": np.array([[1, 0], [0, -1]], complex)}
    kron = lambda s: functools.reduce(np.kron, [PM[c] for c in s])
    R = 1j * kron(probe) @ kron(terms[0])
    Slab, coef = None, None
    for p in itertools.product("IXYZ", repeat=n):
        s = "".join(p)
        tr = np.trace(kron(s).conj().T @ R) / 2 ** n
        if abs(abs(tr) - 1) < 1e-9:
            Slab, coef = s, float(np.real(tr)); break
    signs = [0] * n
    if coef < 0:
        signs[next(i for i, c in enumerate(Slab) if c != "I")] = 1
    qc = signblock_circuit(n, terms, thetas, 0, probe, Slab, signs)
    res = sampler.run([(qc, None, 20000)]).result()
    bits = res[0].data.c.get_bitstrings() if hasattr(res[0].data, "c") else \
        res[0].data.meas.get_bitstrings()
    vals = []
    for s in bits:
        b = s[::-1]
        v = 1
        for i, c in enumerate(probe):
            if c != "I":
                v *= (1 - 2 * int(b[i]))
        vals.append(v)
    got = float(np.mean(vals))
    want = -math.sin(2 * thetas[0])
    sign_ok = abs(got - want) < 0.02
    ok_all &= sign_ok
    print(f"  sign block (term XXXX, probe {probe}, prep {Slab}): <Q(t)> = {got:+.4f} "
          f"vs -sin(2th) = {want:+.4f} -> {'PASS' if sign_ok else 'FAIL'}")
    # ---------------- conventional arm through the REAL chunked-row pub path (F1)
    print("  conv arm (§4): full n=4 sweep, 81 candidates, frozen-seeded order...")
    from exp144_decode_meter import ConvSPRT, probe_outcomes
    import functools
    n, terms, coeffs = cases[0]
    # algebra-vs-matrix cross-check of prep_for_iqp (ground-truth rule, C6513)
    PM2 = {"I": I2, "X": PM["X"], "Y": PM["Y"], "Z": PM["Z"]}
    kron2 = lambda s: functools.reduce(np.kron, [PM2[c] for c in s])
    rngx = np.random.default_rng(5)
    for _ in range(20):
        cnd = "".join(rngx.choice(list("XYZ"), n))
        pr = conv_probe(cnd, int(rngx.integers(1, 9)))
        S, sg = prep_for_iqp(pr, cnd)
        Rm = 1j * kron2(pr) @ kron2(cnd)
        eig = {"I": np.array([1, 0], complex),
               "X": np.array([1, 1], complex) / np.sqrt(2),
               "Y": np.array([1, 1j], complex) / np.sqrt(2),
               "Z": np.array([1, 0], complex)}
        eigm = {"X": np.array([1, -1], complex) / np.sqrt(2),
                "Y": np.array([1, -1j], complex) / np.sqrt(2),
                "Z": np.array([0, 1], complex)}
        v = np.array([1.0 + 0j])
        for c, s in zip(S, sg):
            v = np.kron(v, eig[c] if (c == "I" or s == 0) else eigm[c])
        val = np.real(v.conj() @ Rm @ v)
        assert abs(val - 1) < 1e-9, f"prep algebra != matrix for {pr},{cnd}"
    print("    prep_for_iqp algebra vs MATRIX ground truth: 20/20 PASS")
    # TWO-STAGE DETECTOR (C6515 design, 2-of-2 algebra C4778)
    def commutes_l0(a, b):
        return sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y) % 2 == 0
    all_cands = conv_candidates(n)
    conserved_truth = [c for c in all_cands if all(commutes_l0(c, tt) for tt in terms)]
    meter = 0
    # stage 1: conservation pre-filter, one job, exact rejection of anticommuters
    pubs, _, meta = build_conv_stage1_job(n, 1, terms, coeffs)
    res = sampler.run(pubs).result()
    d1 = res[1].data
    arr = (d1.c if hasattr(d1, "c") else d1.meas).get_bitstrings()
    per_row = len(arr) // len(meta)
    meter += len(arr)
    survivors = []
    for i, m in enumerate(meta):
        mean = float(np.mean(probe_outcomes(arr[i * per_row:(i + 1) * per_row],
                                            m["cand"])))
        if mean > 0.9:                      # noiseless: conserved reads exactly +1
            survivors.append(m["cand"])
    s1_ok = sorted(survivors) == sorted(conserved_truth)
    print(f"    stage-1: {len(meta)} candidates -> {len(survivors)} survivors "
          f"(truth {len(conserved_truth)}): {'EXACT' if s1_ok else 'MISMATCH'}")
    # stage 2: median over rotated probe family, gauge-randomized rows
    per_probe_mean = {c: [] for c in survivors}
    for wave in range(1, S2_FAMILY + 1):
        pubs, _, meta = build_conv_job(n, 1, terms, coeffs, wave=wave,
                                       alive=survivors)
        res = sampler.run([(pubs[1][0], pubs[1][1], 400)]).result()
        d2 = res[0].data
        arr = (d2.c if hasattr(d2, "c") else d2.meas).get_bitstrings()
        per_row = len(arr) // len(survivors)
        meter += len(survivors) * S2_SHOTS   # flight-shot accounting (sim used 400)
        for i, m in enumerate(meta):
            outs = probe_outcomes(arr[i * per_row:(i + 1) * per_row], m["probe"])
            per_probe_mean[m["cand"]].append(float(np.mean(outs)))
    CUT2 = 0.10
    accepted = [c for c, v in per_probe_mean.items()
                if abs(float(np.median(v))) >= CUT2]
    conv_sup_ok = sorted(accepted) == sorted(terms)
    # chair caution (C4777): EXHAUSTIVE check on the conserved-NON-planted class
    non_planted = [c for c in survivors if c not in terms]
    false_pos = [c for c in non_planted if c in accepted]
    cons_rej = not false_pos
    print(f"    stage-2 (median over {S2_FAMILY} probes, cut {CUT2}): accepted "
          f"{sorted(accepted)}; conserved-non-planted class ({len(non_planted)} "
          f"members, EXHAUSTIVE) false-positives: {len(false_pos)}")
    # coeff refinement with constrained probes (support now known to conv arm)
    def commutes_l(a, b):
        return sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y) % 2 == 0
    ref_ok = True
    for j, (lab, c) in enumerate(zip(terms, coeffs)):
        others = [x for x in terms if x != lab]
        pq = next("".join(p) for p in itertools.product("IXYZ", repeat=n)
                  if set(p) != {"I"} and not commutes_l("".join(p), lab)
                  and all(commutes_l("".join(p), o) for o in others))
        S, sg = prep_for_iqp(pq, lab)
        qc = signblock_circuit(n, terms, [cc * T_FROZEN for cc in coeffs], j, pq, S, sg)
        rr = sampler.run([(qc, None, 4000)]).result()[0].data
        bb = (rr.c if hasattr(rr, "c") else rr.meas).get_bitstrings()
        meter += 4000
        mval = float(np.mean(probe_outcomes(bb, pq)))
        chat = -math.asin(max(-1, min(1, mval))) / (2 * T_FROZEN)
        ref_ok &= abs(chat - c) <= 0.03
    ok_conv = s1_ok and conv_sup_ok and cons_rej and ref_ok
    ok_all &= ok_conv
    print(f"    two-stage verdict: support {'OK' if conv_sup_ok else sorted(accepted)}"
          f" | stage-1 exact: {s1_ok} | class-exhaustive clean: {cons_rej}"
          f" | refine |c-hat - c|<=tau: {ref_ok}")
    print(f"    conv meter (n=4, sim): {meter} shots -> {'PASS' if ok_conv else 'FAIL'}")
    print("SELFTEST (G2.1 law check, REAL pub path, both arms):",
          "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--n", type=int, default=8)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.scan:
        for n in NS:
            d = duration_estimate(n)
            print(f"n={n}: ~{d['1q']} 1q + {d['2q']} 2q gates, "
                  f"est duration ~{d['est_us']} us (fingerprint-arm input, §8)")
        return 0
    print("submit modes are EMBER's (sealed-committer); this kit ships build+selftest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
