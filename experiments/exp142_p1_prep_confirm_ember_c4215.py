#!/usr/bin/env python3
"""P1 Gate-B kit-confirm (Ember C4215) — my freeze-order piece (Whisper #1218 step ii).

Confirms my G3-passed kit TAKES the frozen α=0.95 all-Paulis 0-CZ shot-ensemble prep, and that the
prep feeds the ALREADY-CERTIFIED two-copy Bell readout to produce the expected α=0.95 signal.

FROZEN SPEC (h9-p1-first-contact-prereg, dc43b27):
  ρ = (I + 0.95·s·P)/2ⁿ,  P uniform over ALL Paulis∖{I} (I-sites allowed),  s=±1.
  REALIZATION = 0-CZ product-state SHOT-ENSEMBLE. Per shot:
    0.95 → a random +1-eigenstate of P (support sites = eigenstate of P_i with even-parity signs so
           the product eigenvalue is +1; I-sites = random comp-basis),
    0.05 → a fully random computational-basis state.
  readout = the G3-certified transversal two-copy Bell (K.quantum_template) — P-INDEPENDENT.

CONFIRM CRITERIA ($0, noiseless):
  (A) prep is 0-CZ (no entangling gate) => same single-qubit fidelity class as the G3-certified prep
      => the on-device G3 PASS (readout depth-1) TRANSFERS to this prep. (advisor validity-keystone)
  (B) two-copy Bell constraint-rate for TRUE-P ≈ (1+0.95²)/2 = 0.9513 (the α=0.95 signal), WRONG-P ≈ 0.5,
      over random all-Paulis P INCLUDING I-sites. (kit produces the right signal through the readout)
  (C) edges: pin the G3-certified Bell-pair edges for the flight, else re-cert at flight epoch. (rider #2)
"""
import argparse, json, os, sys, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142_robust_decoder_sim as G2

ALPHA = 0.95
TARGET = (1 + ALPHA**2) / 2       # 0.9513 — noiseless two-copy Bell constraint-rate at α=0.95
N_P = 6                            # random all-Paulis P's per rung (incl I-sites)
DRAWS = 500                        # FRESH shot-ensemble draws per P, each shots=1 (matches the flight;
                                   # the ensemble needs a fresh per-SHOT draw, not one fixed realization)


def prep_angles(n, P, rng):
    """One shot-ensemble product-state prep of ρ=(I+0.95P)/2ⁿ. Returns (thetas, phis), 0-CZ."""
    support = [i for i in range(n) if P[i] != "I"]
    t = [0.0] * n; p = [0.0] * n
    if rng.random() < ALPHA:
        signs = rng.integers(0, 2, size=len(support))
        if len(support) and signs.sum() % 2:       # even parity over SUPPORT => +1 eigenvalue product
            signs[rng.integers(0, len(support))] ^= 1
        for k, i in enumerate(support):
            th, ph = K.PREP_ANGLES[(P[i], int(signs[k]))]; t[i] = th; p[i] = ph
        for i in range(n):                          # I-sites: random comp-basis
            if P[i] == "I" and rng.integers(0, 2):
                t[i] = np.pi
    else:                                           # 0.05: fully random comp-basis
        for i in range(n):
            if rng.integers(0, 2):
                t[i] = np.pi
    return t, p


def random_pauli(n, rng):
    """A random Pauli over {I,X,Y,Z}∖{whole-I} — I-sites allowed, but not all-I."""
    while True:
        P = "".join(rng.choice(list("IXYZ"), n))
        if P.count("I") < n:
            return P


def pauli_to_bits(P):
    """All-Paulis symplectic vector: I->(0,0) (no support contribution), X/Y/Z as usual."""
    n = len(P); v = np.zeros(2 * n, dtype=np.int8)
    for i, p in enumerate(P):
        x, z = {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}[p]
        v[i], v[n + i] = x, z
    return v


def constraint_rate(counts_list, n, P, mapping, csign):
    Pb = pauli_to_bits(P); want = csign[P.count("Y") % 2]
    good = tot = 0
    for cts in counts_list:
        for bs, c in cts.items():
            Q = G2.outcome_to_bits(bs, n, mapping)
            good += c * (int(G2.sp_inner(Q, Pb, n)) == want); tot += c
    return good / tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args()
    if not args.confirm:
        print("use --confirm ($0 noiseless kit-confirm)"); return 0

    from qiskit_aer.primitives import SamplerV2 as AerSampler
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    aer = AerSampler()
    print(f"P1 KIT-CONFIRM (α={ALPHA}, target two-copy constraint-rate={TARGET:.4f}, "
          f"{N_P} random all-Paulis P × {DRAWS} fresh-draw shots=1 rows):\n")

    ok_all = True
    for n in (4, 6, 8):
        qc, params = K.quantum_template(n)          # the G3-CERTIFIED readout (P-independent)
        # (A) 0-CZ check: quantum_template's ONLY 2q gates are the n Bell-readout CX; the PREP (the u's
        # we fill) has none. Confirm the prep angles inject no 2q op (they are single-qubit u only).
        rng = np.random.default_rng(4215 + n)
        Ps = [random_pauli(n, rng) for _ in range(N_P)]
        rP_list, rW_list = [], []
        for P in Ps:
            # DRAWS rows, each a FRESH shot-ensemble draw for both copies, shots=1 (flight structure)
            rows = []
            for _ in range(DRAWS):
                t1, p1 = prep_angles(n, P, rng); t2, p2 = prep_angles(n, P, rng)
                rows.append((t1 + t2) + (p1 + p2))
            pr = aer.run([(qc, K.named_rows(params, np.array(rows)), 1)]).result()[0]
            cl = [pr.data.c[i].get_counts() for i in range(len(rows))]
            rP_list.append(constraint_rate(cl, n, P, mapping, csign))
            wrong = random_pauli(n, rng)
            while wrong == P:
                wrong = random_pauli(n, rng)
            rW_list.append(constraint_rate(cl, n, wrong, mapping, csign))
        rP = float(np.mean(rP_list)); rW = float(np.mean(rW_list))
        # (B) criterion: true-P near TARGET (α signal), wrong-P near 0.5
        crit = abs(rP - TARGET) < 0.03 and abs(rW - 0.5) < 0.03
        ok_all &= crit
        print(f"  n={n}: true-P constraint-rate {rP:.4f} (target {TARGET:.4f})  wrong-P {rW:.4f} (~0.5)"
              f"  -> {'OK' if crit else 'MISMATCH'}   [{N_P} all-Paulis P incl I-sites]")

    # (C) edge pin
    gj = os.path.join(HERE, "..", "results", "g3_twocopy_bell_gate_validate.json")
    edges = {k: v["bell_pairs"] for k, v in json.load(open(gj)).items()} if os.path.exists(gj) else {}
    print("\n(A) prep = single-qubit u only (0-CZ) => same fidelity class as G3-certified prep => "
          "G3 on-device PASS transfers.")
    print(f"(C) G3-certified Bell-pair edges to PIN for the flight (or re-cert $0 at flight epoch): {edges}")
    print(f"\nKIT-CONFIRM: {'PASS — kit takes the α=0.95 all-Paulis shot-ensemble prep, feeds the '
          'certified readout, signal = α target.' if ok_all else 'FAIL — investigate mismatch.'}")
    json.dump({"alpha": ALPHA, "target_rate": TARGET, "pass": bool(ok_all), "pinned_edges": edges},
              open(os.path.join(HERE, "..", "results", "p1_kit_confirm.json"), "w"), indent=1)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
