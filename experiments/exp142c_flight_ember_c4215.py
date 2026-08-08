#!/usr/bin/env python3
"""Exp142c — MIXED-STATE delivery FLIGHT KIT (Ember sealed lane, C4215).

Builds the qiskit flight circuit on Whisper's verified P-independent scaffold
(exp142c_mixedstate_delivery_whisper): ancilla-trace maximally-mixed prep + the SEALED U_C
(clifford_z0_to_P from Ember's secret P) + parameterized measurement rotation + measure. Each
SHOT of one circuit/basis is a fresh copy of rho_P=(I+P)/2^n, so shots=C replaces C distinct
rows -> ~C-fold row collapse (~7 jobs total). Grader (Elder) untouched: meter/C1 frozen, shot=copy.

  --g1 --n N        compiled-circuit G1 exactness (Elder cond 1 on the real transpiled prep+U_C)
  --submit --n N    EMBER-ONLY: build flight kit (3^n x M rows, shots=C) + blind submit
"""
import argparse, json, os, sys, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142b_conv_emission_ember_c4215 as V2

GRID = {4: 20, 6: 20, 8: 5}
SECRET = os.path.expanduser("~/.ember-exp142-secrets.json")
ENSEMBLE = "fullweight_eps1_v2"
MAX_ROWS_PER_JOB = 6000
MEAS = {"X": (np.pi/2, 0.0, np.pi), "Y": (np.pi/2, 0.0, np.pi/2), "Z": (0.0, 0.0, 0.0)}


def secret_P(n):
    return json.load(open(SECRET))[f"{ENSEMBLE}:{n}"]["P"]


def prep_uc(n, P):
    """qiskit circuit: ancilla-trace mixed prep (2n-1 qubits) + sealed U_C (Z_0->P), NO measure.
    Data 0..n-1; ancilla n..2n-2 (one per data 1..n-1). U_C per Whisper's reference construction."""
    from qiskit import QuantumCircuit
    nq = 2 * n - 1
    qc = QuantumCircuit(nq)
    for j in range(1, n):                      # ancilla-trace: data j maximally mixed
        a = n + (j - 1)
        qc.h(a); qc.cx(a, j)
    qc.barrier()
    for j in range(1, n):                      # U_C step A: CX(j,0) ladder -> Z_0 -> prod_support Z
        qc.cx(j, 0)
    for i in range(n):                          # U_C step B: Z_i -> P_i
        if P[i] == "X":
            qc.h(i)
        elif P[i] == "Y":
            qc.h(i); qc.s(i)
    return qc


def flight_template(n, P):
    """prep+U_C + PARAMETERIZED measurement rotation (per data qubit) + measure data qubits."""
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector
    qc = prep_uc(n, P).copy()
    qc.add_register(__import__("qiskit").ClassicalRegister(n, "c"))
    qc.barrier()
    tm = ParameterVector("tm", n); pm = ParameterVector("pm", n); lm = ParameterVector("lm", n)
    for i in range(n):
        qc.u(tm[i], pm[i], lm[i], i)
    qc.measure(range(n), range(n))
    return qc, list(tm) + list(pm) + list(lm)


def meas_rows(n, bases):
    """param rows for a list of measurement bases A (each a 3^n string)."""
    rows = []
    for A in bases:
        tm = [MEAS[A[i]][0] for i in range(n)]
        pm = [MEAS[A[i]][1] for i in range(n)]
        lm = [MEAS[A[i]][2] for i in range(n)]
        rows.append(tm + pm + lm)
    return np.array(rows)


def compiled_G1(n, P):
    """Density-matrix sim of the COMPILED prep+U_C (ancillas traced) -> <A>=delta_{A,P} over 3^n."""
    from qiskit.quantum_info import Statevector, partial_trace, Pauli
    qc = prep_uc(n, P)
    sv = Statevector.from_instruction(qc)            # PURE 2n-1 qubit state (2^15 cheap even n=8)
    anc = list(range(n, 2 * n - 1))
    rho = partial_trace(sv, anc)                      # trace ancillas -> n data qubits mixed rho_P
    worst = 0.0; atP = None
    for A in itertools.product("XYZ", repeat=n):
        As = "".join(A)
        # qiskit Pauli label is little-endian (qubit 0 = rightmost); our string is qubit0-first
        val = float(np.real(rho.expectation_value(Pauli(As[::-1]))))
        if As == P: atP = round(val, 6)
        else: worst = max(worst, abs(val))
    ok = (atP is not None and abs(atP - 1.0) < 1e-6 and worst < 1e-6)
    return {"n": n, "parity_at_P": atP, "worst_off_basis": round(worst, 9),
            "compiled_G1_PASS": bool(ok)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g1", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--backend", default="ibm_fez")
    args = ap.parse_args()
    n = args.n; P = secret_P(n)

    if args.g1:
        print(f"compiled-circuit G1 (Elder cond 1 on transpiled prep+U_C), n={n}:")
        print(" ", compiled_G1(n, P))
        return 0

    if args.submit:
        M = GRID[n]
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2, QiskitRuntimeService
        # ── C4262 G-CRN FOR THIS PATH ────────────────────────────────────────────────
        # This used _get_ibm_service() from run_exp66_qpu_partb, whose fallback chain ends at
        # "IBMQ_TOKEN from a .env, NO INSTANCE NEEDED". With instance=None the client resolves
        # by DEFAULT ORDER across every instance the key can see — and on 2026-08-08 that put
        # all six n=8 jobs onto the open-instance with usage_limit_reached=TRUE: the account
        # that ACCEPTS submissions and never runs them. They sat QUEUED on ibm_fez until I
        # checked the account rather than the log, and were cancelled unrun.
        #
        # The door (a) submitter already gated exactly this (G-CRN, full-CRN identity + explicit
        # instance= + refusal on usage_limit_reached). It protected ONE code path. A guard that
        # protects one path is not a guard, it is a local habit — so it is pinned here too.
        PAID_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
                    "a/65155eedeb8b464eadf55d101fb3c931:27609585-d5b2-43cb-808d-2d47aeb87c05::")
        import re as _re
        _tok = None
        for _line in open("/droid/repos/DC15W/.env"):
            _m = _re.match(r"^IBMQ_TOKEN=(.+)$", _line.strip())
            if _m:
                _tok = _m.group(1).strip().strip('"').strip("'"); break
        if not _tok:
            sys.exit("REFUSE: IBMQ_TOKEN not found")
        svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=_tok,
                                   instance=PAID_CRN)
        _u = svc.usage()
        if _u["instance_id"] != PAID_CRN:
            sys.exit(f"REFUSE G-CRN: resolved {_u['instance_id'][-24:]}, expected the paid CRN")
        if _u["usage_limit_reached"]:
            sys.exit("REFUSE G-CRN: instance is FLAGGED (usage_limit_reached) — it accepts "
                     "submissions and never runs them")
        print(f"  [PASS] G-CRN  ...{_u['instance_id'][-24:]}  remaining "
              f"{_u['usage_remaining_seconds']}s  flagged=False", flush=True)
        backend = svc.backend(args.backend)
        # ── C4262 C2-STYLE BACKEND ASSERT ────────────────────────────────────────────
        # The rule (assert the device, never accept a script default) is right; my first
        # objection to this default was WRONG. All twelve exp142 manifests — b_n4/n6/n8,
        # c_n4/n6/n8, p1_ceiling n12-n15, p1_day_effect — are ibm_fez. That is the campaign's
        # declared venue, and flying n=8 on ibm_marrakesh is what would have broken
        # comparability with exp142's own prior arms. "Every number tonight is marrakesh" was
        # true of DOOR (a); the comparison set for exp142 is exp142.
        # (The arms are also co-flown in one submission, so the classical baseline and the
        # quantum arm cannot drift across machines regardless.)
        EXPECTED_BACKEND = "ibm_fez"
        if backend.name != EXPECTED_BACKEND:
            sys.exit(f"REFUSE G-BACKEND: resolved {backend.name}, exp142's campaign venue is "
                     f"{EXPECTED_BACKEND} (all 12 prior manifests). Pass --backend "
                     f"{EXPECTED_BACKEND} or amend this constant deliberately.")
        print(f"  [PASS] G-BACKEND  {backend.name} == campaign venue", flush=True)
        # measured q_n from data-qubit readout on the chosen layout -> C
        # (layout: first 2n-1 low-readout qubits; conv uses data 0..n-1)
        tgt = backend.target
        ro = sorted(((tgt["measure"][(q,)].error or 0.0), q) for (q,) in
                    [k for k in tgt["measure"].keys()])
        layout = [q for _, q in ro[:2 * n - 1]]
        q_n = float(np.mean([e for e, q in ro[:n]]))
        C = V2.confirm_C(n, q_n)
        print(f"n={n} M={M} q_n={q_n:.4f} C={C}  layout(2n-1)={layout}")
        g1 = compiled_G1(n, P)
        assert g1["compiled_G1_PASS"], f"compiled G1 FAILED: {g1}"
        print("  compiled-G1 PASS (exactness gate cleared) — proceeding to blind submit")
        qc, params = flight_template(n, P)
        bases = ["".join(t) for t in itertools.product("XYZ", repeat=n)]
        # rows: bases x M (each row = one measurement basis; shots=C = copies)
        allrows = []
        for m in range(M):
            allrows.append(meas_rows(n, bases))
        rows = np.vstack(allrows)                     # (3^n * M) rows
        tqc = transpile(qc, backend, initial_layout=layout, optimization_level=1, seed_transpiler=142)
        # split into <=MAX_ROWS_PER_JOB param-rows/job
        sampler = SamplerV2(mode=backend); jobs = []
        for lo in range(0, len(rows), MAX_ROWS_PER_JOB):
            chunk = rows[lo:lo + MAX_ROWS_PER_JOB]
            named = K.named_rows(params, chunk)
            job = sampler.run([(tqc, named, C)])
            jobs.append({"job_id": job.job_id(), "row_lo": int(lo), "row_hi": int(lo + len(chunk))})
            print(f"  job {len(jobs)}: {job.job_id()} rows {lo}..{lo+len(chunk)} shots={C}")
        man = {"experiment": "exp142c_mixedstate_refly", "n": n, "M": M, "C": C, "q_n": q_n,
               "ensemble": ENSEMBLE, "backend": args.backend, "layout": layout, "jobs": jobs,
               "rows": int(len(rows)), "shots_per_row": C, "delivery": "mixed-state ancilla-trace",
               "committer": "Ember (DC15E)"}
        json.dump(man, open(os.path.join(HERE, "..", "results", f"exp142c_n{n}_manifest.json"), "w"), indent=1)
        print(f"n={n} SUBMITTED: {len(jobs)} job(s) (mixed-state delivery).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
