#!/usr/bin/env python3
"""Exp142b build_job_v2 + blind submit (Ember C4215) — the F119 remedy re-fly to hardware.

Integrates the conv-v2 emission (exp142b_conv_emission: blind uniform-C shots=1, C=p99 from
MEASURED q_n) with the frozen kit's quantum arm + cals + sentinels into Ember-submitted jobs.
Grid = fixed-ALPHA: n=4/6 M=20, n=8 M=5. One sealed P/rung (fullweight_eps1_v2, off-git secret).

  --dry-run           : build all pubs, report PUB/shot counts, verify integrity, NO submit, NO QPU
  --submit --n N      : EMBER-ONLY. build+transpile+submit one rung's job(s), save manifest+job_id
  --backend NAME      : default ibm_fez (short queue; avoids kingston cross-block collision)

Blind protocol: state prep depends on the secret P, so EMBER runs this. Siblings get outcome
bitstrings + the P-INDEPENDENT manifest only. q_n (readout) measured from backend calibration on
the conv layout -> re-sizes C per rung. PUB-limit safe: submit per-rung (n=8 may split per-rep).
"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142b_conv_emission_ember_c4215 as V2

GRID = {4: 20, 6: 20, 8: 5}
SECRET = os.path.expanduser("~/.ember-exp142-secrets.json")
ENSEMBLE = "fullweight_eps1_v2"
MAX_ROWS_PER_JOB = 100000       # catch #9: split by TOTAL param-ROWS/job (control-hw OOM, err 6073).
                                # calibrated: n6b DONE @17.4k rows, failed @494.5k -> 100k safe (Whisper
                                # ~10-20 n=8 jobs). No single PUB exceeds 8192 rows so grouping always fits.


def measured_q_n(backend, conv_layout):
    """Mean per-qubit readout error over the conv layout = q_n for C re-sizing."""
    tgt = backend.target
    errs = []
    for q in conv_layout:
        try:
            errs.append(tgt["measure"][(q,)].error or 0.0)
        except Exception:
            pass
    return float(np.mean(errs)) if errs else 0.02


def build_rung(n, P, C, M, rng):
    """All pubs for one rung: M disjoint decode blocks (conv-v2 shots=1 + quantum shots=1) +
    cals + sentinels. Returns (pubs, manifest_pubs). Manifest is P-INDEPENDENT."""
    pubs, man = [], []
    # sentinel start
    pubs.append((K.sentinel_circuit(), None, K.SENT_SHOTS)); man.append({"kind": "sentinel_start", "shots": K.SENT_SHOTS})
    # calibration block (known random Paulis, basis-matched) — P-independent
    qc_c, cparams = K.conv_template(n)
    cal_paulis = ["".join(rng.choice(list(K.PAULIS), size=n)) for _ in range(K.CAL_PAULIS)]
    for cp in cal_paulis:
        r, bs = K.conv_param_rows(cp, [cp], rng)
        pubs.append((qc_c, K.named_rows(cparams, r), K.CAL_SHOTS))
        man.append({"kind": "cal", "pauli": cp, "b": bs[0], "shots": K.CAL_SHOTS})
    # M disjoint decode blocks
    qqc, qparams = K.quantum_template(n)
    for m in range(M):
        # conv-v2 (blind uniform-C shots=1)
        cpubs, cman, order, _ = V2.build_conv_rep(n, P, C, rng)
        for (qc, rows, shots), mm in zip(cpubs, cman):
            pubs.append((qc, rows, shots)); mm2 = dict(mm); mm2["rep"] = m; man.append(mm2)
        # quantum arm (transversal Bell sampling, shots=1)
        qrows, qb = K.quantum_param_rows(P, K.BQ[n], rng)
        pubs.append((qqc, K.named_rows(qparams, qrows), 1))
        man.append({"kind": "quantum", "rep": m, "rows": K.BQ[n], "shots": 1})
    # sentinel end
    pubs.append((K.sentinel_circuit(), None, K.SENT_SHOTS)); man.append({"kind": "sentinel_end", "shots": K.SENT_SHOTS})
    return pubs, man


def integrity_check(man, n):
    """Verify the manifest is P-INDEPENDENT and shots discipline holds (no leak, delivery fix)."""
    s = json.dumps(man)
    import re
    assert not re.search(r"theta|phi|angle|prep|\bP\b|param_rows", s), "manifest leaks angles/P!"
    conv = [m for m in man if m["kind"] == "conv_v2"]
    assert all(m["shots"] == 1 for m in conv), "conv shots != 1"
    quantum = [m for m in man if m["kind"] == "quantum"]
    assert all(m["shots"] == 1 for m in quantum), "quantum shots != 1"
    return len(conv), len(quantum)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--n", type=int)
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--q_n", type=float, default=0.02, help="dry-run readout (submit uses measured)")
    args = ap.parse_args()

    if args.dry_run:
        print(f"DRY-RUN (design q_n={args.q_n}; submit re-sizes from measured calibration):")
        grand_pubs = grand_shots = 0
        for n, M in GRID.items():
            C = V2.confirm_C(n, args.q_n)
            rng = np.random.default_rng(4215 + n)   # seed placeholder; submit uses OS entropy + secret
            # build with a DUMMY P (dry-run only; real P from secret at submit)
            Pdummy = "".join(rng.choice(list("XYZ"), size=n))
            pubs, man = build_rung(n, Pdummy, C, M, rng)
            nconv, nq = integrity_check(man, n)
            shots = sum(p[2] * (1 if p[1] is None else len(p[1])) for p in pubs)
            njobs = -(-len(pubs) // MAX_PUBS_PER_JOB)
            grand_pubs += len(pubs); grand_shots += shots
            print(f"  n={n} M={M} C={C}: {len(pubs)} PUBs ({nconv} conv + {nq} quantum + cals/sent), "
                  f"{shots:,} shots -> {njobs} job(s) @ <={MAX_PUBS_PER_JOB} PUBs")
        print(f"  TOTAL ~{grand_pubs} PUBs, ~{grand_shots:,} shots. integrity PASS (no P/angle leak, "
              f"conv+quantum shots==1). NO QPU spent by dry-run.")
        return 0

    if args.submit:
        if args.n is None:
            print("--submit requires --n"); return 2
        n, M = args.n, GRID[args.n]
        with open(SECRET) as f:
            P = json.load(f)[f"{ENSEMBLE}:{n}"]["P"]
        from run_exp66_qpu_partb import _get_ibm_service
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2
        svc = _get_ibm_service(); backend = svc.backend(args.backend)
        st = backend.status(); print(f"{backend.name}: op={st.operational} pending={st.pending_jobs}")
        q_layout, conv_layout, bell_pairs = K.pick_layouts(backend, n)
        q_n = measured_q_n(backend, conv_layout)
        C = V2.confirm_C(n, q_n)
        print(f"measured q_n={q_n:.4f} -> C=p99={C}  (conv_layout={conv_layout})")
        rng = np.random.default_rng()   # OS entropy for flight
        pubs, man = build_rung(n, P, C, M, rng)
        integrity_check(man, n)
        real_shots = sum(p[2] * (1 if p[1] is None else len(list(p[1].values())[0])) for p in pubs)
        print(f"n={n} M={M} C={C}: {len(pubs)} PUBs, ~{real_shots:,} shots (integrity PASS, blind)")
        # transpile each pub on its arm's layout
        tpubs = []
        for (qc, rows, shots), meta in zip(pubs, man):
            k = meta["kind"]
            il = q_layout if k == "quantum" else (list(bell_pairs[0]) if k.startswith("sentinel")
                                                  else conv_layout)
            tqc = transpile(qc, backend, initial_layout=il, optimization_level=1, seed_transpiler=142)
            tpubs.append(((tqc, rows, shots) if rows is not None else (tqc, None, shots), meta))
        # split into jobs capped by TOTAL ROWS/JOB (catch #9), submit each
        def prows(meta):
            return meta.get("rows", 1)   # conv/quantum carry 'rows'; cal/sentinel ~1
        sampler = SamplerV2(mode=backend)
        jobs = []; grp = []; grp_rows = 0; grp_lo = 0
        def flush(hi):
            nonlocal grp, grp_rows
            if not grp:
                return
            job = sampler.run([p for p in grp])
            jid = job.job_id()
            jobs.append({"job_id": jid, "pub_lo": grp_lo, "pub_hi": hi, "rows": grp_rows})
            print(f"  job {len(jobs)}: {jid}  (PUBs {grp_lo}..{hi}, {grp_rows:,} rows)")
            grp = []; grp_rows = 0
        for i, (p, meta) in enumerate(tpubs):
            r = prows(meta)
            if grp and grp_rows + r > MAX_ROWS_PER_JOB:
                flush(i); grp_lo = i
            grp.append(p); grp_rows += r
        flush(len(tpubs))
        manifest = {"experiment": "exp142b_f119_remedy_refly", "n": n, "M": M, "C": C, "q_n": q_n,
                    "ensemble": ENSEMBLE, "backend": args.backend, "bell_pairs": bell_pairs,
                    "conv_layout": conv_layout, "q_layout": q_layout, "jobs": jobs,
                    "shots_est": real_shots, "pubs": man, "committer": "Ember (DC15E)"}
        outp = os.path.join(HERE, "..", "results", f"exp142b_n{n}_manifest.json")
        json.dump(manifest, open(outp, "w"), indent=1)
        print(f"n={n} SUBMITTED: {len(jobs)} job(s). Manifest -> {outp}")
        return 0

    print("use --dry-run or --submit --n N")
    return 0


if __name__ == "__main__":
    sys.exit(main())
