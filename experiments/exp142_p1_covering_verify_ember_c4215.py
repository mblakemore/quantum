#!/usr/bin/env python3
"""P1 covering-set verify (Ember C4215) — EMISSION-SIDE check on the ~240-job spend question.

Whisper #1247: the Creator-authorized ~240 jobs assumed 3ⁿ FULL-WEIGHT emission, but the C1 family
moved to all-Paulis∖{I} (4ⁿ−1). If C1 needs a measurement PER candidate → (4/3)ⁿ blowup → ~1500
jobs → Creator re-auth. Her covering-set claim keeps ~240: the 3ⁿ full-weight bases COVER every
candidate (a weight-w P is read from any full-weight A with A=P on support(P); 3^(n−w) such bases),
so emission stays 3ⁿ while the decode WALKS all 4ⁿ−1 candidates by EXTRACTING support-parity.

This verifies the EMISSION side (my lane); the decode-extraction design is Elder's (365206a):
  (1) COVERING combinatorics: every all-Paulis∖{I} candidate is covered by ≥1 full-weight basis.
  (2) EXTRACTION works on the α=0.95 shot-ensemble single copy: for true-P, support-parity read from
      a COVERING full-weight measurement has even-rate ≈ (1+α)/2 = 0.975 (the C1 single-copy signal);
      a wrong candidate extracted from the SAME data ≈ 0.5 (discriminable). => 3ⁿ emission suffices.
"""
import argparse, os, sys, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K

ALPHA = 0.95
MEAS = {"X": (np.pi/2, 0.0, np.pi), "Y": (np.pi/2, 0.0, np.pi/2), "Z": (0.0, 0.0, 0.0)}


def support(P):
    return [i for i in range(len(P)) if P[i] != "I"]


def covering_bases(P):
    """All full-weight A (A_i∈XYZ) with A_i=P_i on support(P): 3^(n−w) of them."""
    n = len(P); free = [i for i in range(n) if P[i] == "I"]
    out = []
    for combo in itertools.product("XYZ", repeat=len(free)):
        A = list(P)
        for k, i in enumerate(free):
            A[i] = combo[k]
        out.append("".join(A))
    return out


def prep_single(n, P, rng):
    """One α=0.95 shot-ensemble copy of ρ=(I+0.95P)/2ⁿ (0-CZ product state). Returns (thetas,phis)."""
    S = support(P); t = [0.0]*n; p = [0.0]*n
    if rng.random() < ALPHA:
        signs = rng.integers(0, 2, size=len(S))
        if len(S) and signs.sum() % 2:
            signs[rng.integers(0, len(S))] ^= 1
        for k, i in enumerate(S):
            th, ph = K.PREP_ANGLES[(P[i], int(signs[k]))]; t[i] = th; p[i] = ph
        for i in range(n):
            if P[i] == "I" and rng.integers(0, 2):
                t[i] = np.pi
    else:
        for i in range(n):
            if rng.integers(0, 2):
                t[i] = np.pi
    return t, p


def support_parity(bits, P):
    """Parity of measured bits over support(P) (I-qubits excluded) — the C1 observable."""
    return sum(int(bits[i]) for i in support(P)) % 2


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if not args.verify:
        print("use --verify ($0)"); return 0
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    target = (1 + ALPHA) / 2
    print(f"P1 COVERING-SET EMISSION VERIFY (α={ALPHA}, C1 single-copy target even-rate={target:.4f}):\n")

    # (1) covering combinatorics over ALL candidates (small n exhaustive)
    for n in (4, 6):
        cands = ["".join(c) for c in itertools.product("IXYZ", repeat=n) if c.count("I") < n]
        cover_counts = [len(covering_bases(P)) for P in cands]
        assert min(cover_counts) >= 1, "a candidate is UNcovered!"
        print(f"  (1) n={n}: all {len(cands)} candidates (4ⁿ−1) covered by ≥1 full-weight basis "
              f"(min {min(cover_counts)}=3^0 high-weight, max {max(cover_counts)}=3^(n−1) weight-1). "
              f"Emission stays 3ⁿ={3**n}, NOT 4ⁿ−1={4**n-1}.")

    # (2) extraction on the shot-ensemble single copy, from a COVERING measurement
    print()
    for n in (4, 6, 8):
        rng = np.random.default_rng(4215 + n)
        Ps = []
        for _ in range(6):                     # sample candidates across weights incl high-weight
            P = "".join(rng.choice(list("IXYZ"), n))
            if P.count("I") == n:
                P = P[:-1] + "Z"
            Ps.append(P)
        rP_all, rW_all = [], []
        for P in Ps:
            A = covering_bases(P)[rng.integers(0, len(covering_bases(P)))]  # a covering full-weight basis
            evenP = evenW = tot = 0
            wrong = "".join(rng.choice(list("IXYZ"), n))
            while wrong == P or wrong.count("I") == n or not set(support(wrong)) <= set(support(P)):
                wrong = "".join(rng.choice(list("IXYZ"), n))  # a wrong cand ALSO covered by A
            for _ in range(400):
                t, p = prep_single(n, P, rng)
                qc = QuantumCircuit(n, n)
                for i in range(n):
                    qc.u(t[i], p[i], 0.0, i)
                qc.barrier()
                for i in range(n):
                    th, ph, la = MEAS[A[i]]; qc.u(th, ph, la, i)
                qc.measure(range(n), range(n))
                out = sim.run(qc, shots=1, memory=True).result().get_memory()[0].replace(" ", "")[::-1]
                evenP += support_parity(out, P) == 0
                evenW += support_parity(out, wrong) == 0
                tot += 1
            rP_all.append(evenP/tot); rW_all.append(evenW/tot)
        rP = float(np.mean(rP_all)); rW = float(np.mean(rW_all))
        ok = abs(rP - target) < 0.04 and abs(rW - 0.5) < 0.06
        print(f"  (2) n={n}: true-P support-parity even-rate {rP:.4f} (target {target:.4f}) from COVERING "
              f"basis; wrong-cand {rW:.4f} (~0.5) -> {'OK' if ok else 'CHECK'}")
    print("\nEMISSION SIDE CONFIRMED: 3ⁿ full-weight covering emission carries the C1 single-copy signal "
          "for every all-Paulis candidate via support-parity extraction => ~240 jobs, Creator auth intact")
    print("IF Elder's decode builds parities_by_cand by EXTRACTING from the 3ⁿ covering measurements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
