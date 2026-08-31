#!/usr/bin/env python3
"""P1 n=8 C1 covering decode — Elder C6575. The capstone C1 arm on the ALT single-epoch flight.

EXTENDS the n6-gated flown driver (exp142_p1_c1_flown_gate_elder_c6568.py) across the TWO seams the
n8 ALT manifest introduces. The frozen c5003 decoder is IMPORTED UNCHANGED — only the fetch/index
layer differs, because that is the only thing that differs on n8.

  SEAM 1 — BASIS-OF-ROW IS A GENERATOR, NOT VERBATIM.
    n6 manifest carries c1_basis_of_row verbatim (46656 entries). The n8 ALT manifest slims it to
    "full_weight_bases(8) x C_PER_BASIS, Elder order" (Whisper #1489 contract). We regenerate
    basis-major: for A in full_weight_bases(n): [A]*c_per_basis  (equivalently fwb[r//c_per_basis]).
    *** The regeneration is ASSERTED EQUAL to the verbatim list whenever one is present (n6). That
    turns the n6 known-answer gate into a test of the GENERATOR branch too, on the rung where a
    ground truth exists — otherwise the n8-only code path would fly completely untested. ***

  SEAM 2 — MULTIPLE CHUNKS PER JOB.
    n6 = 6 jobs x 1 pub. n8 ALT = 13 jobs x 4 pubs (BATCH_CHUNKS=4). The c6568 driver read pub 0 only
    (`fetch_pub_bits(job, 0)`), which on n8 would have silently fetched 13 of 52 chunks and decoded a
    75%-truncated stream. We iterate every pub, in submit order (batch asc, pub idx asc), which is the
    order build_flight emitted them (tc1[b*4:(b+1)*4]) and therefore the GLOBAL row order.

Bit convention `[::-1]` unchanged from the scaffold / Q arm / c6568 driver (Whisper interface-verify
#1489, all four seams). Identification is q-robust; the METER is not, so --q-sweep reports both.

USE:
  # 1. re-gate on n6 THROUGH THIS DRIVER (modified code => the old PASS does not carry over)
  python3 exp142_p1_c1_n8_decode_elder_c6575.py --manifest ../results/exp142_p1_n6_manifest.json \
      --n 6 --expect IYXZXY --q 0.055
  # 2. blind n8
  python3 exp142_p1_c1_n8_decode_elder_c6575.py \
      --manifest ../results/exp142_p1_n8_c1_refly_manifest_ALT.json --n 8
"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp142_p1_c1_decoder_elder_c5003 import (      # FROZEN — imported, never reimplemented
    covering_decode, full_weight_bases, determinism_redteam)
from run_exp66_qpu_partb import _get_ibm_service


def basis_of_row(man, n):
    """Regenerate the basis-major row->basis map, and VALIDATE it against the verbatim list if the
    manifest carries one (n6). Returns (list, source_str)."""
    c = int(man["c_per_basis"])
    fwb = full_weight_bases(n)
    gen = [A for A in fwb for _ in range(c)]
    verbatim = man.get("c1_basis_of_row")
    if verbatim:
        if list(verbatim) != gen:
            raise SystemExit(f"*** GENERATOR MISMATCH vs verbatim c1_basis_of_row (n={n}): "
                             f"len {len(verbatim)} vs {len(gen)} — n8 regeneration contract is BROKEN, "
                             f"do NOT trust any n8 C1 number ***")
        return list(verbatim), f"verbatim (generator ASSERTED IDENTICAL, {len(gen)} rows)"
    exp = int(man.get("emission_bases", len(fwb)))
    if exp != len(fwb):
        raise SystemExit(f"emission_bases {exp} != 3^{n}={len(fwb)}")
    return gen, f"regenerated full_weight_bases({n}) x {c} = {len(gen)} rows"


def fetch_all_c1_rows(man, svc, verbose=True):
    """Every C1 covering chunk, ALL pubs per job, in submit order. Returns list of bit-arrays."""
    jobs = [j for j in man["jobs"] if j["kind"] == "c1_covering"]
    jobs.sort(key=lambda j: j.get("batch", 0))
    rows = []
    for k, j in enumerate(jobs):
        t0 = time.time()
        job = svc.job(j["job_id"])
        st = str(job.status())
        if "DONE" not in st.upper() and "COMPLETED" not in st.upper():
            raise SystemExit(f"job {j['job_id']} status={st} — not Completed, refusing to decode partial")
        res = job.result()
        npubs = len(res)
        expect = int(j.get("chunks", 1))
        if npubs != expect:
            raise SystemExit(f"job {j['job_id']}: {npubs} pubs but manifest says chunks={expect}")
        got = 0
        for pi in range(npubs):
            r = res[pi]
            reg = list(r.data.keys())[0] if hasattr(r.data, "keys") else "c"
            for s in getattr(r.data, reg).get_bitstrings():
                rows.append([int(x) for x in s.replace(" ", "")[::-1]])   # SAME convention as scaffold/Q/c6568
                got += 1
        if verbose:
            print(f"  batch {j.get('batch')}: {j['job_id']} {npubs} pubs, {got} rows "
                  f"({time.time()-t0:.1f}s, total {len(rows)})", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--q", type=float, default=None, help="scalar single-copy readout flip; default = mean of manifest per-qubit q")
    ap.add_argument("--expect", default=None, help="revealed P for the known-answer gate (n6)")
    ap.add_argument("--q-sweep", default="", help="comma list of q values for the robustness sweep")
    ap.add_argument("--redteam", action="store_true", help="run the flown determinism red-team too")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    man = json.load(open(args.manifest)); assert man["n"] == args.n
    bor, src = basis_of_row(man, args.n)
    print(f"basis_of_row: {src}", flush=True)

    qper = man.get("q_backend_props_per_qubit") or {}
    q = args.q if args.q is not None else (
        sum(v["q"] for v in qper.values()) / len(qper) if qper else 0.055)
    print(f"q (scalar for frozen p0_of) = {q:.6f}"
          f"{' [mean of manifest per-qubit]' if args.q is None and qper else ''}", flush=True)

    svc = _get_ibm_service()
    print(f"fetching C1 covering chunks (n={args.n}, {man['emission_bases']} bases x {man['c_per_basis']})...",
          flush=True)
    rows = fetch_all_c1_rows(man, svc)
    if len(rows) != len(bor):
        raise SystemExit(f"*** ROW-COUNT MISMATCH: fetched {len(rows)} vs expected {len(bor)} — "
                         f"chunk/pub enumeration is wrong, do NOT trust the decode ***")
    fw_shots = {}
    for i, b in enumerate(rows):
        fw_shots.setdefault(bor[i], []).append(b)
    print(f"  fetched {len(rows)} rows, {len(fw_shots)} distinct bases (expect {man['emission_bases']})",
          flush=True)
    if len(fw_shots) != int(man["emission_bases"]):
        raise SystemExit("basis coverage mismatch — refusing to decode")

    print(f"running FROZEN c5003 covering_decode (alpha=0.95, q={q:.6f})...", flush=True)
    t0 = time.time()
    res = covering_decode(fw_shots, args.n, 0.95, q)
    phat = res.get("P_hat")
    print(f"  P_hat_C1 = {phat}   C1_distinct_copies = {res.get('C1_distinct_copies')}   "
          f"({time.time()-t0:.1f}s)")
    print(f"  identified = {phat is not None}   candidates = {res.get('candidates_walked')}")

    gate = None
    if args.expect:
        gate = (phat == args.expect)
        print(f"  n{args.n} GATE: expect {args.expect} -> "
              f"{'PASS — flown-extraction + generator branch validated' if gate else '*** MISMATCH — seam bug ***'}")

    sweep = {}
    for qs in [x for x in args.q_sweep.split(",") if x.strip()]:
        qv = float(qs)
        r2 = covering_decode(fw_shots, args.n, 0.95, qv)
        sweep[qs] = {"P_hat": r2.get("P_hat"), "C1_distinct_copies": r2.get("C1_distinct_copies")}
        print(f"  q={qv:<8} -> P_hat={r2.get('P_hat')}  copies={r2.get('C1_distinct_copies')}"
              f"{'  [identification STABLE]' if r2.get('P_hat') == phat else '  *** P_hat MOVED ***'}")

    rt = determinism_redteam(fw_shots, args.n) if args.redteam else None
    if rt:
        print(f"  red-team: max_within_basis_modal={rt['max_within_basis_modal_freq']} "
              f"(fresh expected {rt['fresh_expected_modal']})  LEAK={rt['LEAK']}")

    out = args.out or os.path.join(HERE, "..", "results",
                                   f"exp142_p1_c1_n{args.n}_decode_elder_c6575.json")
    # PERSIST RAW BITS before the verdict is written (board#353 / grade-spec open item #1). IBM jobs
    # expire; saving only the derived verdict leaves it un-re-checkable once the job is gone. Save the
    # row-major bits + basis map so covering_decode can be re-run offline and this verdict re-derived.
    # Pure side-effect, mirrors exp142_p1_c1_parallel_baseline; does not touch rows/fw_shots/res.
    _bits_path = out.replace(".json", "_rawbits.npz")
    np.savez_compressed(_bits_path, bits=np.array(rows, dtype=np.int8),
                        basis_of_row=np.array(bor), n=args.n, q_used=q,
                        manifest_hash=str(man.get("commit_hash", "")))
    print(f"SAVED RAW BITS {_bits_path}", flush=True)
    json.dump({"n": args.n, "manifest": os.path.basename(args.manifest),
               "manifest_hash": man.get("commit_hash"), "backend": man.get("backend"),
               "basis_of_row_source": src, "q_used": q, "q_per_qubit": qper,
               "rows_fetched": len(rows), "bases": len(fw_shots),
               "P_hat_C1": phat, "result": res, "expect": args.expect, "gate_pass": gate,
               "q_sweep": sweep, "determinism_redteam": rt,
               "decoder": "FROZEN exp142_p1_c1_decoder_elder_c5003.covering_decode",
               "driver": "exp142_p1_c1_n8_decode_elder_c6575.py (Elder C6575)"},
              open(out, "w"), indent=1)
    print(f"SAVED {out}", flush=True)
    return 0 if (gate is None or gate) else 1


if __name__ == "__main__":
    sys.exit(main())
