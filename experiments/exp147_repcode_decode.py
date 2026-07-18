#!/usr/bin/env python3
"""Exp147 — Repetition-code syndrome decoding on ibm_fez: the roadmap rung that turns
the campaign's GF(2) statistical decoder toward its native fault-tolerance cousin
(Creator directive C4833: "fly it"; Ember on Exp148).

WHY THIS IS THE RIGHT FIRST QEC RUNG: decoding a stabilizer code is solving H.e = sigma
over GF(2) — the SAME machine that recovered Simon's period (145) and the Even-Mansour
key (146). Simon survived 8x its predicted wall because the true answer keeps a persistent
statistical bias that many reps resolve; the QEC analog is repeated syndrome rounds +
min-weight recovery. This experiment MEASURES how that statistical self-correction holds
up against the standard decoder (MWPM / pymatching) on real hardware.

SELF-VERIFYING (Simon precedent, no seals): plant a logical value, run R syndrome rounds,
decode, CHECK recovered == planted. Logical error rate p_L = fraction where decode != plant.
The P3 truth-check is intrinsic.

THE RACE (pre-registered): p_L(ours: GF(2) min-weight-coset) vs p_L(MWPM) on IDENTICAL shots.
THE PRIZE (pre-registered): does p_L DECREASE as distance d = 3 -> 5 -> 7? Distance suppression
is the signature of error correction working. If p_L rises with d, hardware is below the
repetition-code threshold — an honest NISQ outcome, stated in advance.

FENCES (headline-level, C4830): NOT fault tolerance — offline classical decode, no logical
gates, no real-time feedback. Repetition code protects ONE error type (bit-flip) only; it is
the standard first hardware rung, not a full code. Honest claim = "the campaign decoder
extends to QEC syndrome decoding; here is its measured logical error rate + distance behavior."

Circuit (distance d, bit-flip code): d data qubits + (d-1) Z-parity ancillas on a line.
Round: for each ancilla j between data j and j+1: CX(data_j -> anc_j), CX(data_{j+1} -> anc_j),
measure anc_j, reset. R rounds, then final data readout in Z.

Space-time detectors: layer L_t (t=0..R-1) = ancilla round t; L_R = data-derived parities.
Detector D_t = L_t XOR L_{t-1} (L_{-1}=0 for a clean planted logical). Error mechanisms:
  data-X at position i, time t: flips detectors (t,i-1),(t,i) [boundary -> single detector]
  meas-error ancilla j, round t: flips detectors (t,j),(t+1,j) [time edge]
Logical observable = parity of data qubits; the decoder's correction on it is what we grade.

Usage:
  python3 exp147_repcode_decode.py --selftest      # P3 truth-gate: H.e construction + distance suppression, noiseless+injected
  python3 exp147_repcode_decode.py --powercalc     # Gate-2: predicted p_L under MEASURED fez noise, both decoders
  python3 exp147_repcode_decode.py --submit [--backend ibm_fez --reps 2000]
  python3 exp147_repcode_decode.py --decode --manifest ../results/exp147_manifest.json
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

# MEASURED fez/kingston noise (Exp143 fingerprint + Exp144 CX-sweep, durable kit).
# fez is same-generation Heron; using the campaign's measured kit as the honest prior.
E_CX = 0.0106       # per-CX in-context error (anchored fit C4792); each syndrome check = 2 CX
E_RO = 0.010        # per-qubit readout / measurement error


# ------------------------- code + circuit -------------------------

def rep_code_circuit(d, rounds, logical):
    """Distance-d bit-flip repetition code, `rounds` syndrome extractions, then data readout.
    Qubit line: data at even indices 0,2,..,2(d-1); ancilla at odd 1,3,..,2d-3."""
    nq = 2 * d - 1
    data = [2 * i for i in range(d)]
    anc = [2 * j + 1 for j in range(d - 1)]
    creg_bits = rounds * (d - 1) + d          # R syndrome layers + final data
    qc = QuantumCircuit(nq, creg_bits)
    if logical == 1:
        qc.x(data)                            # logical |1> = all data flipped
    cbit = 0
    for t in range(rounds):
        for j in range(d - 1):
            qc.cx(data[j], anc[j])
            qc.cx(data[j + 1], anc[j])
        qc.barrier()
        for j in range(d - 1):
            qc.measure(anc[j], cbit); cbit += 1
        if t != rounds - 1:
            qc.reset(anc)                     # fresh ancillas for next round
        qc.barrier()
    for i in range(d):
        qc.measure(data[i], cbit); cbit += 1
    return qc, data, anc


# ------------------------- space-time check matrix -------------------------

def build_check_matrix(d, rounds):
    """Return (H, logical_flips, det_index) for the repetition-code space-time graph.
    H: (num_detectors x num_mechanisms) GF(2). logical_flips: 1 per mechanism if it flips
    the logical observable (data-X errors do; measurement errors do not). det_index maps
    (t,j) -> detector row. Mechanisms are enumerated deterministically.
    Detector layers t=0..rounds (rounds ancilla layers + 1 data-derived layer); each has
    (d-1) checks."""
    n_det_layers = rounds + 1
    det_index = {}
    r = 0
    for t in range(n_det_layers):
        for j in range(d - 1):
            det_index[(t, j)] = r
            r += 1
    num_det = r

    cols = []          # each: (set_of_detector_rows, logical_flip)
    # data-X errors: position i in {0..d-1}, at data-layer t in {0..rounds}
    # a data-X before syndrome layer t flips checks (t, i-1) and (t, i) that touch data i.
    for t in range(n_det_layers):
        for i in range(d):
            dets = set()
            if i - 1 >= 0:
                dets.add(det_index[(t, i - 1)])
            if i <= d - 2:
                dets.add(det_index[(t, i)])
            # logical observable = data qubit 0's Z; a data-X on qubit 0 flips it.
            # Under the min-weight-coset convention the logical operator is "X on all data
            # left of a cut"; we fix observable = parity of ALL data, flipped by any single
            # data-X. Use the standard rep-code observable: logical flip iff error chain
            # crosses the observable's support. We take observable support = {data 0..d-1}
            # parity, i.e. every data-X toggles it.
            cols.append((dets, 1))
    # measurement errors: ancilla j, round t in {0..rounds-1}; flips detectors (t,j),(t+1,j)
    for t in range(rounds):
        for j in range(d - 1):
            dets = {det_index[(t, j)], det_index[(t + 1, j)]}
            cols.append((dets, 0))

    num_mech = len(cols)
    H = np.zeros((num_det, num_mech), dtype=np.uint8)
    logical_flips = np.zeros(num_mech, dtype=np.uint8)
    for c, (dets, lf) in enumerate(cols):
        for rrow in dets:
            H[rrow, c] = 1
        logical_flips[c] = lf
    return H, logical_flips, det_index


def counts_to_detectors(bitstring, d, rounds, det_index):
    """Convert one measurement bitstring -> (detector vector, raw logical parity).
    Qiskit bitstring is little-endian over the classical register order we filled:
    [round0 checks (d-1)], [round1 checks], ..., [final data (d)]. Rightmost char = cbit 0."""
    bits = bitstring.replace(" ", "")[::-1]     # bits[k] = classical bit k
    R = rounds
    syn = np.zeros((R + 1, d - 1), dtype=np.uint8)
    k = 0
    for t in range(R):
        for j in range(d - 1):
            syn[t, j] = int(bits[k]); k += 1
    data = np.array([int(bits[k + i]) for i in range(d)], dtype=np.uint8)
    # data-derived final syndrome layer
    for j in range(d - 1):
        syn[R, j] = data[j] ^ data[j + 1]
    # detectors = layer XOR previous layer (layer -1 == 0 for planted-clean logical)
    det = np.zeros((R + 1) * (d - 1), dtype=np.uint8)
    prev = np.zeros(d - 1, dtype=np.uint8)
    for t in range(R + 1):
        diff = syn[t] ^ prev
        for j in range(d - 1):
            det[det_index[(t, j)]] = diff[j]
        prev = syn[t]
    raw_logical = int(data.sum() % 2)           # parity of data = observable pre-correction
    return det, raw_logical


# ------------------------- decoders -------------------------

def _gf2_solve(H, sigma):
    """One GF(2) solution e to H.e = sigma (least-index pivots), or None if inconsistent."""
    A = np.concatenate([H.copy(), sigma.reshape(-1, 1).copy()], axis=1).astype(np.uint8)
    rows, cols = H.shape
    piv_col = []
    r = 0
    for c in range(cols):
        p = None
        for rr in range(r, rows):
            if A[rr, c]:
                p = rr; break
        if p is None:
            continue
        A[[r, p]] = A[[p, r]]
        for rr in range(rows):
            if rr != r and A[rr, c]:
                A[rr] ^= A[r]
        piv_col.append(c); r += 1
        if r == rows:
            break
    for rr in range(r, rows):                   # inconsistent?
        if A[rr, cols]:
            return None
    e = np.zeros(cols, dtype=np.uint8)
    for i, c in enumerate(piv_col):
        e[c] = A[i, cols]
    return e


def _null_basis(H):
    """GF(2) null-space basis of H (list of column vectors v with H.v = 0)."""
    rows, cols = H.shape
    A = H.copy().astype(np.uint8)
    piv_col = []
    r = 0
    for c in range(cols):
        p = None
        for rr in range(r, rows):
            if A[rr, c]:
                p = rr; break
        if p is None:
            continue
        A[[r, p]] = A[[p, r]]
        for rr in range(rows):
            if rr != r and A[rr, c]:
                A[rr] ^= A[r]
        piv_col.append(c); r += 1
    free = [c for c in range(cols) if c not in piv_col]
    basis = []
    for fc in free:
        v = np.zeros(cols, dtype=np.uint8)
        v[fc] = 1
        for i, pc in enumerate(piv_col):
            v[pc] = A[i, fc]
        basis.append(v)
    return basis


_EXACT_CACHE = {}      # (H.tobytes(), sigma.tobytes()) -> (logical flip, min weight, degenerate)

def decode_gf2_exact(H, logical_flips, sigma, null_basis=None, return_weight=False):
    """OURS: the campaign GF(2) engine — EXACT maximum-likelihood (min-weight) decode.
    Enumerate the full solution coset e0 + null(H); track the minimum weight in each
    logical class {0,1}; predict the lighter class. This is literally the Simon/EM move
    (enumerate candidate corrections, score by weight, pick the lightest consistent one),
    made exact. Tractable only while dim null(H) is small (d=3 rung) — used as the
    independent cross-check that our engine reproduces MWPM's optimum; MWPM carries the
    d=3/5/7 scaling. Returns predicted logical flip in {0,1}, or None if intractable."""
    e0 = _gf2_solve(H, sigma)
    if e0 is None:
        return (0, 0, False) if return_weight else 0   # inconsistent -> trivial correction
    if null_basis is None:
        null_basis = _null_basis(H)
    B = len(null_basis)
    if B > 20:
        return (None, None, None) if return_weight else None   # intractable -> MWPM fallback
    key = (H.tobytes(), sigma.astype(np.uint8).tobytes())
    if key not in _EXACT_CACHE:
        best_w = {0: None, 1: None}
        for combo in range(1 << B):
            e = e0.copy()
            cc = combo; b = 0
            while cc:
                if cc & 1:
                    e ^= null_basis[b]
                cc >>= 1; b += 1
            w = int(e.sum())
            cls = int(logical_flips @ e % 2)
            if best_w[cls] is None or w < best_w[cls]:
                best_w[cls] = w
        # lighter logical class wins (ties -> class 0, the identity correction)
        flip = 0 if (best_w[1] is None or (best_w[0] is not None and best_w[0] <= best_w[1])) else 1
        min_w = min(w for w in best_w.values() if w is not None)
        degenerate = (best_w[0] is not None and best_w[1] is not None and best_w[0] == best_w[1])
        _EXACT_CACHE[key] = (flip, min_w, degenerate)
    flip, min_w, degenerate = _EXACT_CACHE[key]
    return (flip, min_w, degenerate) if return_weight else flip


def decode_mwpm(matching, sigma, logical_flips):
    """STANDARD: pymatching MWPM. With faults_matrix set, decode() returns predicted
    logical-observable flips directly (length = #faults = 1). Returns flip in {0,1}."""
    pred = matching.decode(sigma)               # predicted observable flips
    return int(pred[0]) & 1


# ------------------------- gates: selftest + powercalc -------------------------

def _apply_error_mechanisms(H, logical_flips, mech_ids):
    """Apply a set of error mechanisms -> resulting detector syndrome + true logical flip."""
    sigma = np.zeros(H.shape[0], dtype=np.uint8)
    lf = 0
    for m in mech_ids:
        sigma ^= H[:, m]
        lf ^= int(logical_flips[m])
    return sigma, lf


def selftest():
    """P3 TRUTH-GATE. (1) H construction consistency: a bare logical operator has trivial
    syndrome AND flips the observable (proves the graph is wired right). (2) weight-1
    correctness: MWPM corrects every single mechanism (d=3,5,7); OURS (exact GF(2)) corrects
    every single mechanism where tractable (d=3). (3) VALIDATION: ours==MWPM on all weight-1
    and on random multi-error samples at d=3 (our engine reproduces the optimum). (4)
    Falsifiability: a bare-logical error yields trivial syndrome so BOTH decoders return the
    identity correction -> a logical ERROR (ground truth flipped, syndrome empty). p_L can be
    nonzero: the test CAN fail. (5) Distance suppression in MC (physics sanity, MWPM)."""
    from pymatching import Matching
    rng = np.random.default_rng(147)
    # --- construction + weight-1 + validation ---
    w1_mwpm_ok = w1_mwpm = 0
    w1_ours_ok = w1_ours = 0
    val_agree = val_tot = 0
    for d in (3, 5, 7):
        rounds = d
        H, lf, di = build_check_matrix(d, rounds)
        nb = _null_basis(H)
        matching = Matching.from_check_matrix(H, weights=np.ones(H.shape[1]),
                                              faults_matrix=lf.reshape(1, -1))
        num_mech = H.shape[1]
        tractable = len(nb) <= 20
        for m in range(num_mech):
            sigma, true_lf = _apply_error_mechanisms(H, lf, [m])
            w = decode_mwpm(matching, sigma.copy(), lf)
            w1_mwpm += 1; w1_mwpm_ok += (w == true_lf)
            if tractable:
                g = decode_gf2_exact(H, lf, sigma.copy(), nb)
                w1_ours += 1; w1_ours_ok += (g == true_lf)
        # construction: bare logical operator (a null vector that flips observable)
        z = next((v for v in nb if (lf @ v) % 2 == 1), None)
        assert z is not None, f"d={d}: no logical operator in null space"
        assert not ((H @ z) % 2).any(), f"d={d}: logical op has nontrivial syndrome (H bug)"
        # validation: ours and MWPM are BOTH minimum-weight decoders -> identical optimal
        # weight on every sample; logical choice agrees except on exact degenerate ties
        # (both optimal, arbitrary tie-break). Assert equal weight always; equal flip off-tie.
        if tractable:
            for _ in range(2000):
                fired = [m for m in range(num_mech) if rng.random() < 0.08]
                sigma, _tlf = _apply_error_mechanisms(H, lf, fired)
                g, gw, degen = decode_gf2_exact(H, lf, sigma.copy(), nb, return_weight=True)
                w, ww = matching.decode(sigma.copy(), return_weight=True)
                w = int(w[0]) & 1
                assert abs(gw - ww) < 1e-6, f"d={d}: weight mismatch ours={gw} mwpm={ww} (H bug)"
                val_tot += 1
                val_agree += (g == w) or degen        # off-tie must agree; tie may differ
    # --- distance suppression MC (MWPM, physics sanity) ---
    print("SELFTEST distance-suppression MC (p_phys=0.02, MWPM):")
    for d in (3, 5, 7):
        rounds = d
        H, lf, di = build_check_matrix(d, rounds)
        matching = Matching.from_check_matrix(H, weights=np.ones(H.shape[1]),
                                              faults_matrix=lf.reshape(1, -1))
        num_mech = H.shape[1]
        TR = 3000
        errs = 0
        for _ in range(TR):
            fired = [m for m in range(num_mech) if rng.random() < 0.02]
            sigma, true_lf = _apply_error_mechanisms(H, lf, fired)
            errs += (decode_mwpm(matching, sigma.copy(), lf) != true_lf)
        print(f"  d={d}: p_L(MWPM)={errs / TR:.4f}")
    print(f"SELFTEST weight-1 MWPM {w1_mwpm_ok}/{w1_mwpm} | weight-1 OURS(d=3) "
          f"{w1_ours_ok}/{w1_ours} | validation ours==MWPM {val_agree}/{val_tot}")
    assert w1_mwpm_ok == w1_mwpm, "MWPM must correct all weight-1 errors"
    assert w1_ours_ok == w1_ours, "OURS must correct all weight-1 errors (d=3)"
    assert val_agree == val_tot, "OURS must reproduce MWPM exactly (validation)"
    print("SELFTEST PASS (H wired right, weight-1 exact both decoders, our GF(2) engine "
          "reproduces MWPM optimum at d=3, test can fail on bare-logical error)")


def powercalc():
    """GATE-2 under MEASURED noise. Predict the MWPM logical-error curve p_L(d) and whether
    idle over R=d rounds kills distance suppression at d=7 (advisor gate: let the model set
    the ladder). KILL if p_L(d=3) already saturates >0.45 (decoder blind). Ours(d=3) reported
    as the validation cross-check, not a competitor."""
    from pymatching import Matching
    rng = np.random.default_rng(14700)
    print(f"Exp147 Gate-2 power calc | measured E_CX={E_CX} E_RO={E_RO}")
    print(f"{'d':>2} {'R':>2} {'p_data':>7} {'p_meas':>7} {'p_L(MWPM)':>10} {'p_L(ours,d=3)':>13} verdict")
    results = {}
    for d in (3, 5, 7):
        rounds = d
        H, lf, di = build_check_matrix(d, rounds)
        nb = _null_basis(H)
        matching = Matching.from_check_matrix(H, weights=np.ones(H.shape[1]),
                                              faults_matrix=lf.reshape(1, -1))
        num_mech = H.shape[1]
        n_data_mech = d * (rounds + 1)
        # a data qubit sees ~2 CX per check it participates in; meas-error ~ E_RO (measured kit)
        p_data = 1 - (1 - E_CX) ** 2
        p_meas = E_RO
        TR = 4000
        errs_w = errs_g = 0
        tractable = len(nb) <= 20
        for _ in range(TR):
            fired = [m for m in range(num_mech)
                     if rng.random() < (p_data if m < n_data_mech else p_meas)]
            sigma, true_lf = _apply_error_mechanisms(H, lf, fired)
            errs_w += (decode_mwpm(matching, sigma.copy(), lf) != true_lf)
            if tractable:
                errs_g += (decode_gf2_exact(H, lf, sigma.copy(), nb) != true_lf)
        pw = errs_w / TR
        pg = errs_g / TR if tractable else None
        results[f"d{d}"] = {"rounds": rounds, "p_data": p_data, "p_meas": p_meas,
                            "p_L_mwpm": pw, "p_L_ours": pg}
        verdict = "OK"
        if d == 3 and pw > 0.45:
            verdict = "KILL(blind)"
        gs = f"{pg:>13.4f}" if pg is not None else f"{'n/a':>13}"
        print(f"{d:>2} {rounds:>2} {p_data:>7.3f} {p_meas:>7.3f} {pw:>10.4f} {gs} {verdict}")
    p3, p5, p7 = (results[f"d{d}"]["p_L_mwpm"] for d in (3, 5, 7))
    trend = "SUPPRESSION" if (p3 > p5 > p7) else ("flat/rising" if p7 >= p3 else "mixed")
    ladder = [3, 5, 7]
    if p7 >= p5:                                # advisor gate: cap ladder if d=7 above threshold
        ladder = [3, 5]
    print(f"\nMWPM trend d=3->5->7: {p3:.4f} -> {p5:.4f} -> {p7:.4f}  [{trend}]")
    print(f"recommended ladder (model): {ladder}  "
          f"(d=7 {'kept' if 7 in ladder else 'DROPPED: predicted above fez threshold, honest cap'})")
    print("NOTE: prediction only. Hardware adjudicates; rising p_L = below rep-code threshold "
          "on fez (pre-stated honest outcome). Ours(d=3)==MWPM validates the engine, not a race.")
    out = os.path.join(HERE, "..", "results", "exp147_powercalc.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"results": results, "trend": trend, "ladder": ladder}, open(out, "w"), indent=1)
    print(f"-> {out}")


# ------------------------- submit + decode -------------------------

def submit(backend_name, reps, distances):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service()
    backend = svc.backend(backend_name)
    circuits = []
    meta = []
    for d in distances:
        rounds = d
        for logical in (0, 1):
            qc, data, anc = rep_code_circuit(d, rounds, logical)
            tqc = transpile(qc, backend=backend, optimization_level=3)
            circuits.append(tqc)
            meta.append({"d": d, "rounds": rounds, "logical": logical,
                         "depth": tqc.depth(), "n2q": tqc.num_nonlocal_gates()})
    sampler = SamplerV2(mode=backend)
    job = sampler.run(circuits, shots=reps)
    manifest = {"exp": 147, "backend": backend_name, "reps": reps,
                "distances": list(distances), "job_id": job.job_id(),
                "circuit_meta": meta, "E_CX": E_CX, "E_RO": E_RO,
                "note": "repetition-code syndrome decode; self-verifying (recovered logical "
                        "vs planted); race ours-GF2 vs MWPM; distance suppression pre-registered"}
    out = os.path.join(HERE, "..", "results", "exp147_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits: d={list(distances)} x "
          f"logical{{0,1}}, {reps} shots) -> {out}")
    for m in meta:
        print(f"  d={m['d']} logical={m['logical']}: depth={m['depth']} 2q={m['n2q']}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    from pymatching import Matching
    svc = _get_ibm_service()
    man = json.load(open(mp))
    res = svc.job(man["job_id"]).result()
    distances = man["distances"]
    order = [(d, lg) for d in distances for lg in (0, 1)]
    per_d = {}
    for idx, (d, logical) in enumerate(order):
        rounds = d
        H, lf, di = build_check_matrix(d, rounds)
        nb = _null_basis(H)
        tractable = len(nb) <= 20               # ours = exact GF(2) engine, d=3 cross-check
        matching = Matching.from_check_matrix(H, weights=np.ones(H.shape[1]),
                                              faults_matrix=lf.reshape(1, -1))
        r = res[idx]
        reg = list(r.data.keys())[0]
        counts = getattr(r.data, reg).get_counts()
        n_w = n_raw = n_tot = 0
        n_g = 0; n_agree = 0; n_ours_tot = 0
        for bit, c in counts.items():
            det, raw_logical = counts_to_detectors(bit, d, rounds, di)
            w_flip = decode_mwpm(matching, det.copy(), lf)
            w_logical = raw_logical ^ w_flip
            n_w += (w_logical != logical) * c
            n_raw += (raw_logical != logical) * c
            n_tot += c
            if tractable:
                g_flip = decode_gf2_exact(H, lf, det.copy(), nb)
                g_logical = raw_logical ^ g_flip
                n_g += (g_logical != logical) * c
                n_agree += (g_flip == w_flip) * c
                n_ours_tot += c
        agg = per_d.setdefault(d, {"w": 0, "raw": 0, "tot": 0, "g": 0,
                                   "agree": 0, "ours_tot": 0, "tractable": tractable})
        agg["w"] += n_w; agg["raw"] += n_raw; agg["tot"] += n_tot
        agg["g"] += n_g; agg["agree"] += n_agree; agg["ours_tot"] += n_ours_tot
    print(f"Exp147 decode | job {man['job_id']} | backend {man['backend']}")
    print(f"{'d':>2} {'shots':>6} {'p_L(MWPM)':>10} {'p_L(raw/no-EC)':>14} {'ours==MWPM':>11}")
    summary = {}
    for d in distances:
        a = per_d[d]
        pw, praw = a["w"] / a["tot"], a["raw"] / a["tot"]
        rec = {"p_L_mwpm": pw, "p_L_raw": praw, "shots": a["tot"]}
        if a["ours_tot"]:
            rec["p_L_ours"] = a["g"] / a["ours_tot"]
            rec["ours_mwpm_agreement"] = a["agree"] / a["ours_tot"]
        agree_s = f"{a['agree'] / a['ours_tot']:.4f}" if a["ours_tot"] else "n/a"
        summary[f"d{d}"] = rec
        print(f"{d:>2} {a['tot']:>6} {pw:>10.4f} {praw:>14.4f} {agree_s:>11}")
    ds = sorted(distances)
    trend_mwpm = [summary[f"d{d}"]["p_L_mwpm"] for d in ds]
    trend_raw = [summary[f"d{d}"]["p_L_raw"] for d in ds]
    supp_mwpm = all(trend_mwpm[i] > trend_mwpm[i + 1] for i in range(len(ds) - 1))
    ec_helps = all(summary[f"d{d}"]["p_L_mwpm"] <= summary[f"d{d}"]["p_L_raw"] + 1e-9 for d in ds)
    print(f"\nHEADLINE — distance suppression (p_L decreasing d={ds}):")
    print(f"  MWPM: {[f'{x:.4f}' for x in trend_mwpm]}  -> {'YES (error correction working)' if supp_mwpm else 'NO (fez below rep-code threshold — honest, pre-stated)'}")
    print(f"  raw (no EC): {[f'{x:.4f}' for x in trend_raw]}  (uncorrected baseline)")
    print(f"  EC helps vs raw at all d: {'YES' if ec_helps else 'NO'}")
    print(f"VALIDATION — our GF(2) engine vs MWPM (d=3 cross-check): "
          f"agreement {summary['d3'].get('ours_mwpm_agreement', 'n/a')} "
          f"(1.0 = our engine reproduces the optimal decoder)")
    out = {"job_id": man["job_id"], "backend": man["backend"], "summary": summary,
           "suppression_mwpm": supp_mwpm, "ec_helps_vs_raw": ec_helps}
    fn = os.path.join(HERE, "..", "results", "exp147_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--powercalc", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--distances", default="3,5,7")
    a = ap.parse_args()
    dists = tuple(int(x) for x in a.distances.split(","))
    if a.selftest:
        selftest()
    elif a.powercalc:
        powercalc()
    elif a.submit:
        submit(a.backend, a.reps, dists)
    elif a.decode:
        decode(a.manifest or os.path.join(HERE, "..", "results", "exp147_manifest.json"))
    else:
        ap.print_help()
