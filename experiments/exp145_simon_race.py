#!/usr/bin/env python3
"""Exp145 — Simon's problem on ibm_kingston: the campaign's first COMPUTATIONAL
quantum-advantage flight (Creator directive C482x: "Fly it!").

WHY THIS IS DIFFERENT FROM Exp142/144: those were LEARNING advantages (recover a
secret encoded in a quantum state you physically hold). Simon's is a COMPUTATIONAL
query-complexity advantage: classical needs Theta(2^{n/2}) oracle queries to find
the hidden period s (birthday/collision bound); quantum needs O(n). Same GF(2)-
parity decoder family as Exp142 (verified: exp142 decoder core is the symplectic
GF(2) inner product) — pointed at a Simon oracle instead of a planted Pauli.

WHY NO BLINDNESS / SEALS: Simon correctness is CLASSICALLY SELF-VERIFYING. We plant
s, build the oracle, run the algorithm, recover s', and CHECK s'==s AND that every
measured y satisfies y.s'==0. The P3 truth-check is intrinsic — the answer proves
itself. This is exactly what makes it "computational" rather than "learning".

CRYPTO FRAMING (honest fence): the exponential advantage here is for the HIDDEN-
LINEAR-STRUCTURE class (Simon / hidden-subgroup over GF(2)^n) — Simon is the direct
ancestor of Shor. The crypto it naturally BREAKS is quantum crypto built on hidden
stabilizer/linear structure, NOT classical RSA/ECC (that needs fault-tolerant Shor,
a different machine). Stated up front to avoid framing-over-reach (C4713-16).

Circuit: 2n qubits. H on input[0..n-1]; oracle U_f (period-s linear map); H on
input; measure input -> y with y.s = 0 (mod 2). Collect n-1 independent y -> solve
GF(2) nullspace -> s.

Usage:
  python3 exp145_simon_race.py --selftest          # P3 truth-gate: recover planted s, noiseless
  python3 exp145_simon_race.py --powercalc         # Gate-2: recovery prob under MEASURED kingston noise
  python3 exp145_simon_race.py --submit --n 4 [--reps 40]
  python3 exp145_simon_race.py --decode --manifest ../results/exp145_manifest.json
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

# MEASURED kingston noise (Exp143 fingerprint + Exp144 A1(0b) CX-sweep, durable kit):
E_CX = 0.0106       # per-CX in-context label error (anchored fit, C4792) — 8x published
E_RO = 0.010        # per-qubit readout (Exp143 reference-arm SPAM ~ per qubit)


def simon_oracle(n, s):
    """Period-s 2-to-1 linear oracle on 2n qubits (input 0..n-1, output n..2n-1).
    out_j = x_j XOR (s_j AND x_i0), i0 = first set bit of s. Verified period-s."""
    qc = QuantumCircuit(2 * n, name=f"U_f[s={s}]")
    for i in range(n):
        qc.cx(i, n + i)                      # copy x -> output (f=x, injective)
    if any(s):
        i0 = s.index(1)                      # designated control bit
        for j in range(n):
            if s[j] == 1:
                qc.cx(i0, n + j)             # inject period pattern
    return qc


def simon_circuit(n, s):
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n))
    qc.barrier()
    qc.compose(simon_oracle(n, s), inplace=True)
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def gf2_nullspace_vector(ys, n):
    """Given measured y's (each y.s=0), find the unique nonzero s in the null space.
    Returns s as a list, or None if the y's don't pin a 1-dim solution."""
    M = np.array(ys, dtype=np.int64) % 2
    # Gaussian elimination over GF(2)
    M = M.copy()
    rows, cols = M.shape
    pivots = []
    r = 0
    for c in range(cols):
        piv = None
        for rr in range(r, rows):
            if M[rr, c]:
                piv = rr
                break
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        for rr in range(rows):
            if rr != r and M[rr, c]:
                M[rr] ^= M[r]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    free = [c for c in range(cols) if c not in pivots]
    if len(free) != 1:
        return None                          # not a unique 1-dim null space
    # s: free var = 1, back-substitute pivots
    s = [0] * cols
    fc = free[0]
    s[fc] = 1
    for i, pc in enumerate(pivots):
        s[pc] = int(M[i, fc])
    return s


def verify(s_hat, s, ys):
    """Truth-check: recovered s matches planted AND is consistent with all y."""
    if s_hat is None:
        return False, "no unique nullspace"
    exact = (s_hat == s)
    consistent = all((np.dot(y, s_hat) % 2) == 0 for y in ys)
    return exact and consistent, f"exact={exact} consistent={consistent}"


def _sample_ys(counts, n, drop_zero=True):
    ys = []
    for bit, c in counts.items():
        y = [int(x) for x in bit.replace(" ", "")[::-1][:n]]
        if drop_zero and not any(y):
            continue
        ys.extend([y] * c)
    return ys


def selftest():
    """P3 TRUTH-GATE (noiseless): the algorithm MUST recover planted s. A test that
    cannot fail is decoration (C4195) — so we also assert it FAILS on a wrong-s guess."""
    from qiskit.primitives import StatevectorSampler
    sampler = StatevectorSampler(seed=145)
    rng = np.random.default_rng(1450)
    passed = 0
    trials = 0
    for n in (3, 4, 5):
        for _ in range(4):
            s = [0] * n
            while not any(s):
                s = list(rng.integers(0, 2, n))
            s = [int(x) for x in s]
            qc = simon_circuit(n, s)
            res = sampler.run([qc], shots=200).result()[0]
            reg = list(res.data.keys())[0]
            counts = getattr(res.data, reg).get_counts()
            # every measured y must satisfy y.s=0 in the noiseless case
            all_orth = all((np.dot([int(x) for x in b[::-1][:n]], s) % 2) == 0
                           for b in counts)
            ys = _sample_ys(counts, n)
            s_hat = gf2_nullspace_vector(list({tuple(y) for y in ys}), n)
            ok, why = verify(s_hat, s, ys)
            trials += 1
            passed += ok
            assert all_orth, f"n={n} s={s}: noiseless y not orthogonal to s"
            assert ok, f"n={n} s={s}: recovery FAILED noiseless ({why}) s_hat={s_hat}"
    # falsifiability: a deliberately WRONG s_hat must fail verify
    bad = verify([1] + [0] * 2, [0, 1, 1], [[1, 0, 0]])
    assert not bad[0], "verify() cannot fail — decoration!"
    print(f"SELFTEST {passed}/{trials} PASS (noiseless recovery exact); "
          f"falsifiability check PASS")


def _noisy_y(n, s, rng):
    """One Simon shot's y under measured noise: each CX flips output parity w.p.
    ~E_CX, readout flips each measured bit w.p. E_RO. Ideal y is uniform over
    s-orthogonal complement; noise pushes it off. Returns a possibly-corrupted y."""
    # ideal: draw uniform y with y.s = 0
    comp = [v for v in itertools.product((0, 1), repeat=n) if np.dot(v, s) % 2 == 0]
    y = list(comp[rng.integers(len(comp))])
    # noise: n_cx CX gates each contribute a small chance of flipping a measured bit
    n_cx = n + sum(s)                       # copy + period CX count
    p_flip = 1 - (1 - E_CX) ** n_cx         # aggregate per-run corruption channel
    for i in range(n):
        if rng.random() < p_flip / n:       # spread corruption across bits
            y[i] ^= 1
        if rng.random() < E_RO:
            y[i] ^= 1
    return y


def powercalc():
    """GATE-2 under MEASURED noise: predict P(recover s) vs n, with a per-run
    consistency filter (keep only y that could be clean via majority self-check).
    Strategy: oversample R runs, keep y's, take the MOST-CONSISTENT (n-1)-rank set
    by trying the majority nullspace. KILL if P(recover) < 0.9 at feasible reps."""
    rng = np.random.default_rng(14500)
    print(f"Exp145 Gate-2 power calc | measured E_CX={E_CX} E_RO={E_RO}")
    print(f"{'n':>2} {'CX':>3} {'reps':>5} {'P(clean y)':>11} {'P(recover s)':>13} verdict")
    results = {}
    for n in (3, 4, 5, 6):
        s = [1] + [0] * (n - 2) + [1]        # representative weight-2 s
        n_cx = n + sum(s)
        p_clean = (1 - E_CX) ** n_cx * (1 - E_RO) ** n
        for reps in (4 * n, 8 * n, 16 * n):
            succ = 0
            TR = 400
            for _ in range(TR):
                ys = [tuple(_noisy_y(n, s, rng)) for _ in range(reps)]
                ys = [y for y in ys if any(y)]
                # majority approach: find s_hat maximizing # of y orthogonal to it
                best_s, best_score = None, -1
                cand = set(ys)
                # try nullspace of every rank-(n-1) subset is expensive; instead
                # score each nonzero candidate s' by orthogonality count (cheap, n<=6)
                for sc in itertools.product((0, 1), repeat=n):
                    if not any(sc):
                        continue
                    score = sum(1 for y in ys if np.dot(y, sc) % 2 == 0)
                    if score > best_score:
                        best_score, best_s = score, list(sc)
                succ += (best_s == s)
            p_rec = succ / TR
            verdict = "PASS" if p_rec >= 0.9 else ("marg" if p_rec >= 0.5 else "KILL")
            results[f"n{n}_r{reps}"] = {"p_clean": p_clean, "p_recover": p_rec,
                                        "n_cx": n_cx, "reps": reps}
            print(f"{n:>2} {n_cx:>3} {reps:>5} {p_clean:>11.3f} {p_rec:>13.3f} {verdict}")
        print()
    out = os.path.join(HERE, "..", "results", "exp145_powercalc.json")
    json.dump(results, open(out, "w"), indent=1)
    print(f"-> {out}")


def submit(n, reps, backend_name):
    from exp142_flight_kit import pick_layouts  # reuse fingerprint-gated layout
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    rng = np.random.default_rng(1451)
    s = [0] * n
    while not any(s):
        s = [int(x) for x in rng.integers(0, 2, n)]
    svc = _get_ibm_service()
    backend = svc.backend(backend_name)
    qc = simon_circuit(n, s)
    tqc = transpile(qc, backend=backend, optimization_level=3)
    sampler = SamplerV2(mode=backend)
    job = sampler.run([tqc], shots=reps)
    manifest = {"exp": 145, "n": n, "reps": reps, "backend": backend_name,
                "planted_s": s, "job_id": job.job_id(),
                "note": "Simon self-verifying; planted_s recorded for grading, "
                        "verification is s_hat==planted_s AND all y.s_hat==0"}
    out = os.path.join(HERE, "..", "results", "exp145_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} (Simon n={n}, {reps} reps) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp))
    n, s = man["n"], man["planted_s"]
    res = svc.job(man["job_id"]).result()[0]
    reg = list(res.data.keys())[0]
    counts = getattr(res.data, reg).get_counts()
    ys = _sample_ys(counts, n)
    uniq = list({tuple(y) for y in ys})
    # noise-robust: score every candidate s' by orthogonality count (n<=6 exhaustive)
    best_s, best = None, -1
    for sc in itertools.product((0, 1), repeat=n):
        if not any(sc):
            continue
        score = sum(1 for y in ys if np.dot(y, sc) % 2 == 0)
        if score > best:
            best, best_s = score, list(sc)
    frac = best / len(ys)
    ok, why = verify(best_s, s, ys)
    print(f"Simon n={n}: recovered s_hat={best_s} (orthogonality {frac:.2f}) | "
          f"planted s={s} | RECOVERED={'YES' if best_s == s else 'NO'} ({why})")
    out = {"n": n, "planted_s": s, "recovered_s": best_s, "orthogonality_frac": frac,
           "recovered": best_s == s, "n_unique_y": len(uniq), "n_total_y": len(ys)}
    fn = os.path.join(HERE, "..", "results", "exp145_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--powercalc", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.powercalc:
        powercalc()
    elif a.submit:
        submit(a.n, a.reps, a.backend)
    elif a.decode:
        decode(a.manifest or os.path.join(HERE, "..", "results", "exp145_manifest.json"))
    else:
        ap.print_help()
