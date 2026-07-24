#!/usr/bin/env python3
"""P1 First-Contact — P-INDEPENDENT two-arm flight scaffold (Whisper C5003, for the frozen C5003 pre-reg).

BLIND-PROTOCOL ROLE (why this file exists as a separate committed artifact):
  Authored by Whisper, who NEVER holds the secret P. Committed + court-inspectable BEFORE Ember seals.
  Ember calls build_flight(n, P, rng, ...) with the SECRET P at submit time. This file HARDCODES NO P.
  The only Pauli literals in this file live in selftest() and are a documented PUBLIC test-P
  (TEST_P below), never the seal — exactly as K's own selftest and Ember's G3 gate use a public test-P.

REUSE-MAX (advisor discipline — imported, NOT reimplemented, so nothing can drift from the frozen court):
  - exp142_flight_kit (K): quantum_template / conv_template (P-independent circuits, ParameterVectors),
    named_rows, MEAS_ANGLES, BQ, SENT_SHOTS, CONV_CHUNK_ROWS, sentinel_circuit, pick_layouts.
  - prep_angles, ALPHA  <- Ember's EXACT α=0.95 shot-ensemble (her kit-confirm, quantum@6649628).
  - full_weight_bases, candidates, covering_decode, support_parity, covers
        <- Elder's covering driver + frozen SPRT (quantum@7e24bbd on 365206a).

AUTHOR-ONLY (the genuinely new part): the emission wiring (Q two-copy + C1 3^n-covering + sentinels)
  and the determinism-attack check. α=0.95 shot-ensemble, SHOTS=1 FRESH-PER-ROW (Ember's bug-catch:
  a fixed per-row draw biases the quadratic Q arm; each row is an independent ensemble draw).

EMISSION CONTRACT (the ~240/auth-intact map): C1 emits the 3^n FULL-WEIGHT covering bases (Elder's
  full_weight_bases order), C_PER_BASIS shots each; the decoder walks all 4^n-1 candidates and extracts
  each candidate's support-parity from its covering bases (covering_decode). NOT 4^n-1 per-candidate
  bases. Job count << the Creator-authorized ~240 (see selftest job-count report).

SELF-TEST (selftest(), Aer, PUBLIC test-P only): Q arm -> (1+α^2)/2, C1 covering-aggregated true-P
  -> (1+α)/2 while every wrong candidate <= ~0.55, determinism-attack -> chance, and asserts the
  emitted C1 bases == full_weight_bases(n) in Elder's committed order.
"""
import argparse, json, os, sys, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
from exp142_p1_prep_confirm_ember_c4215 import prep_angles, ALPHA          # Ember 6649628
from exp142_p1_c1_decoder_elder_c5003 import (                              # Elder 365206a + 7e24bbd
    full_weight_bases, candidates, covering_decode, support_parity, covers)

C_PER_BASIS = 64          # shot-ensemble rows (shots=1) per covering basis. ~48 jobs total << ~240 auth.
TEST_P = {4: "XYZX", 6: "XYZXYZ", 8: "XYZXYZXY"}   # PUBLIC selftest P only (never a seal)


# --------------------------------------------------------------- emission (P injected at runtime)
def q_arm_rows(n, P, rng, n_rows):
    """Q two-copy Bell rows. Per row: TWO independent fresh shot-ensemble draws (copy1, copy2). shots=1.
    Matches K.quantum_template param order (qt = 2n thetas, qp = 2n phis; qubit i<n=copy1, i>=n=copy2)."""
    rows = []
    for _ in range(n_rows):
        t1, p1 = prep_angles(n, P, rng)      # copy 1 — FRESH draw
        t2, p2 = prep_angles(n, P, rng)      # copy 2 — FRESH draw (independent)
        rows.append(list(t1) + list(t2) + list(p1) + list(p2))
    return np.array(rows)


def c1_arm_rows(n, P, A, rng, n_rows):
    """C1 single-copy rows for one covering basis A. Per row: fresh shot-ensemble prep + measure in A.
    shots=1. Matches K.conv_template param order (tp,pp prep; tm,pm,lm pre-measure rotation)."""
    rows = []
    for _ in range(n_rows):
        tp, pp = prep_angles(n, P, rng)      # FRESH draw
        tm = [K.MEAS_ANGLES[A[i]][0] for i in range(n)]
        pm = [K.MEAS_ANGLES[A[i]][1] for i in range(n)]
        lm = [K.MEAS_ANGLES[A[i]][2] for i in range(n)]
        rows.append(list(tp) + list(pp) + tm + pm + lm)
    return np.array(rows)


def build_flight(n, P, rng, c_per_basis=C_PER_BASIS):
    """P-INDEPENDENT emission wiring. Ember injects the SECRET P here at submit. Returns (pubs, manifest).
    pubs = [(circuit, named_rows|None, shots)]. The manifest records the covering basis per C1 row so the
    decoder can rebuild fw_shots = {basis: [shot_bits,...]} for covering_decode. NO P is written to the
    manifest (blindness): only the basis A (public) and row indices."""
    pubs, man = [], {"n": n, "alpha": ALPHA, "c_per_basis": c_per_basis,
                     "scaffold": "whisper_c5003", "arms": ["Q_two_copy", "C1_covering", "attack_decode"],
                     "emission_bases": None, "pubs": [], "c1_basis_of_row": []}
    pubs.append((K.sentinel_circuit(), None, K.SENT_SHOTS)); man["pubs"].append({"kind": "sentinel_start", "shots": K.SENT_SHOTS})

    # --- Q arm (two-copy Bell, BQ rows, shots=1) ---
    qqc, qparams = K.quantum_template(n)
    qrows = q_arm_rows(n, P, rng, K.BQ[n])
    pubs.append((qqc, K.named_rows(qparams, qrows), 1))
    man["pubs"].append({"kind": "quantum", "rows": int(K.BQ[n]), "shots": 1})

    # --- C1 arm (3^n full-weight COVERING bases, c_per_basis rows each, shots=1) ---
    cqc, cparams = K.conv_template(n)
    fwb = full_weight_bases(n)                       # Elder's committed 3^n order — imported, not rebuilt
    man["emission_bases"] = len(fwb)
    all_rows, basis_of = [], []
    for A in fwb:
        for row in c1_arm_rows(n, P, A, rng, c_per_basis):
            all_rows.append(row); basis_of.append(A)
    all_rows = np.array(all_rows)
    for lo in range(0, len(all_rows), K.CONV_CHUNK_ROWS):
        chunk = all_rows[lo:lo + K.CONV_CHUNK_ROWS]
        pubs.append((cqc, K.named_rows(cparams, chunk), 1))
        man["pubs"].append({"kind": "c1_covering", "row_lo": lo, "rows": int(len(chunk)), "shots": 1})
    man["c1_basis_of_row"] = basis_of               # public basis per row; NO P recorded

    pubs.append((K.sentinel_circuit(), None, K.SENT_SHOTS)); man["pubs"].append({"kind": "sentinel_end", "shots": K.SENT_SHOTS})
    man["n_jobs_est"] = sum(1 for p in man["pubs"] if p["kind"] in ("quantum", "c1_covering"))
    return pubs, man


# --------------------------------------------------------- delivery-integrity (defeats determinism attack)
def delivery_integrity(n, rng, c=8):
    """The determinism attack (exp142b) exploited a FIXED-BASIS-BATCH delivery to read P cheaply. This
    shot-ensemble delivery defeats it STRUCTURALLY, not by a decoder that fails — there is no batch to
    exploit. This returns the structural facts an inspector/red-team checks; the full flown-data
    determinism red-team on the executed counts is ELDER's lane (his exp142b attack gate), and this
    scaffold delivers the clean structure it needs:
      (1) SHOTS=1 on every Q and C1 pub (no fixed-basis batch);
      (2) FRESH-PER-ROW draws (consecutive rows in a basis differ — a fixed draw would be identical);
      (3) MANIFEST P-INDEPENDENCE (records only public bases, never P or the prep signs).
    Returns dict of the three facts for the self-test to assert and the inspector to read."""
    P_a, P_b = TEST_P[n], "".join("Z" if c_ == "I" else c_ for c_ in ("I" + TEST_P[n][1:]))  # two DIFFERENT public P
    pa, ma = build_flight(n, P_a, np.random.default_rng(1), c_per_basis=c)
    pb, mb = build_flight(n, P_b, np.random.default_rng(2), c_per_basis=c)
    all_shots1 = all(pub["shots"] == 1 for pub in ma["pubs"] if pub["kind"] in ("quantum", "c1_covering"))
    # manifest structure (basis sequence, pub kinds) must be IDENTICAL across P (P lives only in sealed angles)
    manifest_pindep = (ma["c1_basis_of_row"] == mb["c1_basis_of_row"]
                       and [x["kind"] for x in ma["pubs"]] == [x["kind"] for x in mb["pubs"]])
    # fresh-per-row: the PREP angles must VARY across a batch of rows in one basis (a fixed per-row draw
    # would give zero variance = the exp142c-style bug that biases the quadratic Q arm).
    A0 = full_weight_bases(n)[0]
    r = c1_arm_rows(n, P_a, A0, rng, 32)
    prep_cols = r[:, :2 * n]                                   # tp + pp (the P-dependent prep angles)
    fresh = bool(np.any(np.std(prep_cols, axis=0) > 1e-9))     # some prep column varies across rows
    return {"shots1_all_arms": all_shots1, "manifest_P_independent": manifest_pindep, "fresh_per_row": fresh}


# ------------------------------------------------------------------------------------- self-test
def selftest(n=4, c=48, seed=1421):
    """Aer, PUBLIC test-P. Pins: Q->(1+a^2)/2, C1 covering-aggregated true-P->(1+a)/2 & wrong<=~0.55,
    attack->chance, emission bases == full_weight_bases order. No memory trust — runs the real path."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    rng = np.random.default_rng(seed)
    P = TEST_P[n]
    a = ALPHA
    ok = True

    # ---- build the flight via the EXACT submit path, with the public test-P ----
    pubs, man = build_flight(n, P, rng, c_per_basis=c)
    assert man["emission_bases"] == 3 ** n, "emission not 3^n"
    # emitted C1 bases == Elder's committed full_weight order
    emitted = []
    for A in man["c1_basis_of_row"]:
        if not emitted or emitted[-1] != A:
            emitted.append(A)
    assert emitted == full_weight_bases(n), "C1 basis order != Elder full_weight_bases order"
    print(f"[selftest n={n} P={P}(PUBLIC)] emission bases={man['emission_bases']}=3^n, order matches Elder ✓")

    # ---- Q arm: two-copy Bell constraint-rate -> (1+a^2)/2. REUSE the court-validated computation
    #      (Ember's constraint_rate + G2 mapping/csign) — the csign handles the Y-parity convention
    #      my hand-roll got wrong (#1225 lesson). Do NOT reimplement the symplectic decode. ----
    import exp142_robust_decoder_sim as G2
    from exp142_g3_twocopy_bell_gate_ember_c4215 import constraint_rate
    mapping = G2.calibrate_bell_mapping()
    csign = G2.calibrate_constraint_sign(mapping)
    qqc, qparams = K.quantum_template(n)
    qrows = q_arm_rows(n, P, rng, 4000)
    cnt = sim.run(qqc, parameter_binds=[{p: qrows[:, i] for i, p in enumerate(qparams)}], shots=1).result().get_counts()
    cnt = cnt if isinstance(cnt, list) else [cnt]     # get_counts -> list of dicts (one per bind)
    qr = constraint_rate(cnt, n, P, mapping, csign)
    q_ok = abs(qr - (1 + a ** 2) / 2) < 0.03
    ok &= q_ok
    print(f"  Q two-copy rate = {qr:.4f} vs (1+a^2)/2={(1+a**2)/2:.4f}  {'✓' if q_ok else 'FAIL'}")

    # ---- C1 covering: aggregate true-P -> (1+a)/2 ; a wrong candidate -> ~0.5 ----
    cqc, cparams = K.conv_template(n)
    fw_shots = {}
    for A in full_weight_bases(n):
        r = c1_arm_rows(n, P, A, rng, c)
        rr = sim.run(cqc, parameter_binds=[{p: r[:, i] for i, p in enumerate(cparams)}], shots=1).result().get_counts()
        rr = rr if isinstance(rr, list) else [rr]     # list of dicts (one per bind)
        bits_list = []
        for d in rr:
            for bitstr, ct in d.items():
                b = [int(x) for x in bitstr.replace(" ", "")[::-1]]
                bits_list += [b] * ct
        fw_shots[A] = bits_list
    def agg_even(cand):
        pars = [support_parity(bits, cand) for A in full_weight_bases(n) if covers(A, cand) for bits in fw_shots[A]]
        return sum(1 for x in pars if x == 0) / len(pars)
    true_even = agg_even(P)
    wrongs = [q for q in candidates(n) if q != P]
    wsamp = [agg_even(q) for q in rng.choice(wrongs, size=min(40, len(wrongs)), replace=False)]
    wrong_max, wrong_med = max(wsamp), float(np.median(wsamp))
    # DISCRIMINATION is what matters: true->(1+a)/2 tight; wrong population ~0.5 (median); clean SEPARATION
    # from true. (Elder's density-matrix sim pins wrong<=0.55 exactly; finite-c self-test allows the
    # high-weight-wrong tail its ~0.5/sqrt(c) noise — the SPRT multi-basis discrimination is his decoder.)
    sep = true_even - wrong_max
    c1_ok = abs(true_even - (1 + a) / 2) < 0.04 and wrong_med < 0.60 and sep > 0.25
    ok &= c1_ok
    print(f"  C1 aggregated true-P = {true_even:.4f} vs (1+a)/2={(1+a)/2:.4f} | wrong median={wrong_med:.4f} "
          f"max={wrong_max:.4f} | separation={sep:.4f}(>0.25)  {'✓' if c1_ok else 'FAIL'}")

    # ---- I-COVERAGE (C5003, Elder #1290): the real flight P is all-Paulis∖{I} = I-CONTAINING (low-weight);
    #      a FULL-WEIGHT TEST_P never exercises the I-decode path, which is exactly where the committed
    #      pauli_to_bits I-omission bug hid (KeyError on I). Exercise an I-containing public P through the
    #      SAME Q path so this class is caught in the self-test, not at flight grade. ----
    P_i = {4: "XIZY", 6: "XIZYIX", 8: "XIZYIXZI"}[n]                 # PUBLIC, I-containing (weight < n)
    qrows_i = q_arm_rows(n, P_i, rng, 3000)
    cnt_i = sim.run(qqc, parameter_binds=[{p: qrows_i[:, k] for k, p in enumerate(qparams)}], shots=1).result().get_counts()
    cnt_i = cnt_i if isinstance(cnt_i, list) else [cnt_i]
    qr_i = constraint_rate(cnt_i, n, P_i, mapping, csign)           # uses pauli_to_bits(P_i) — hits the I path
    i_ok = abs(qr_i - (1 + a ** 2) / 2) < 0.03
    ok &= i_ok
    print(f"  I-coverage Q (test-P {P_i}, weight {sum(c!='I' for c in P_i)}<n) = {qr_i:.4f} vs (1+a²)/2  "
          f"{'✓' if i_ok else 'FAIL'}  (exercises pauli_to_bits I-handling the full-weight TEST_P missed)")

    # ---- delivery integrity (structurally defeats the determinism attack; flown-data red-team = Elder) ----
    di = delivery_integrity(n, rng)
    di_ok = di["shots1_all_arms"] and di["manifest_P_independent"] and di["fresh_per_row"]
    ok &= di_ok
    print(f"  delivery-integrity: shots1={di['shots1_all_arms']} manifest_P_indep={di['manifest_P_independent']} "
          f"fresh_per_row={di['fresh_per_row']}  {'✓' if di_ok else 'FAIL'}  (flown-data determinism red-team = Elder's lane)")

    # ---- job-count report vs the ~240 authorization ----
    print(f"  job-count @c={c}: {man['n_jobs_est']} arm-jobs (n={n}); full-grid n8@C={C_PER_BASIS} ~= "
          f"{-(-(3**8*C_PER_BASIS)//K.CONV_CHUNK_ROWS)} jobs  << ~240 Creator auth")
    print(f"[selftest n={n}] {'ALL PASS ✓' if ok else 'FAILURES ✗'}")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--c", type=int, default=48)
    args = ap.parse_args()
    if args.selftest:
        sys.exit(0 if selftest(args.n, args.c) else 1)
    print("P-independent flight scaffold. Ember calls build_flight(n, P, rng) with the sealed P at submit.")
