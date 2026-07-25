#!/usr/bin/env python3
"""P1 C1 FLOWN covering-extraction gate — Elder C6568.

The MISSING flown driver (Q arm had decode_meter; C1 had none): fetch flown C1 covering chunks →
build fw_shots (basis → [shot bit-arrays]) via the manifest's c1_basis_of_row → run the FROZEN
c5003 covering_decode. Reuses the emission author's own helpers (covers/full_weight_bases/
candidates + c1_basis_of_row verbatim from the manifest) so the extraction matches emission BY
CONSTRUCTION — the emission↔extraction seam Whisper (emission author) offered to interface-verify.

USE: n6 KNOWN-ANSWER GATE first (revealed P=IYXZXY) — validates the flown-extraction convention
end-to-end BEFORE the blind n8 decode, the same n6-gate that caught the Q-arm decode_meter trap.
  python3 exp142_p1_c1_flown_gate_elder_c6568.py --manifest ../results/exp142_p1_n6_manifest.json \
      --n 6 --expect IYXZXY --q 0.055
Blind n8 (no --expect) reuses the identical pipeline once the fez C1 chunks clear.
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_decode_meter as M                          # fetch_pub_bits only
from exp142_p1_c1_decoder_elder_c5003 import covering_decode, full_weight_bases, covers, candidates
from run_exp66_qpu_partb import _get_ibm_service


def fetch_c1_fw_shots(manifest, svc):
    """Fetch every C1 covering chunk, concatenate rows in GLOBAL order, group by basis via the
    manifest's c1_basis_of_row (verbatim). Returns fw_shots {basisStr: [ [int per qubit], ... ]}."""
    basis_of_row = manifest["c1_basis_of_row"]           # verbatim list, one basis per global row
    c1jobs = [j["job_id"] for j in manifest["jobs"] if j["kind"] == "c1_covering"]
    fw_shots, grow = {}, 0
    for jid in c1jobs:
        bits = list(M.fetch_pub_bits(svc.job(jid), 0))   # row-major bitstrings for this chunk
        for s in bits:
            b = [int(x) for x in s.replace(" ", "")[::-1]]   # SAME convention as the scaffold/Q arm
            A = basis_of_row[grow]
            fw_shots.setdefault(A, []).append(b)
            grow += 1
    if grow != len(basis_of_row):
        raise SystemExit(f"row-count mismatch: fetched {grow} vs manifest {len(basis_of_row)}")
    return fw_shots, grow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--q", type=float, default=0.055, help="single-copy readout flip proxy (id is q-robust)")
    ap.add_argument("--expect", default=None, help="revealed P for the known-answer gate (n6)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    man = json.load(open(args.manifest))
    assert man["n"] == args.n
    svc = _get_ibm_service()
    print(f"fetching C1 covering chunks (n={args.n}, {man['emission_bases']} bases x {man['c_per_basis']})...",
          flush=True)
    fw_shots, nrows = fetch_c1_fw_shots(man, svc)
    print(f"  fetched {nrows} rows, {len(fw_shots)} distinct bases (expect {man['emission_bases']})", flush=True)
    print(f"running FROZEN c5003 covering_decode (alpha=0.95, q={args.q})...", flush=True)
    res = covering_decode(fw_shots, args.n, 0.95, args.q)
    phat = res.get("P_hat")
    print(f"  P_hat_C1 = {phat}  C1_distinct_copies (copies-to-identify) = {res.get('C1_distinct_copies')}")
    print(f"  identified = {phat is not None}  candidates_walked = {res.get('candidates_walked')}")
    if args.expect:
        ok = phat == args.expect
        print(f"  n6 GATE: expect {args.expect} -> {'PASS — flown-extraction convention validated' if ok else '*** MISMATCH — seam bug, do NOT trust n8 C1 ***'}")
    out = args.out or os.path.join(HERE, "..", "results",
                                   f"exp142_p1_c1_gate_n{args.n}_elder_c6568.json")
    json.dump({"n": args.n, "manifest_hash": man.get("commit_hash"), "q_used": args.q,
               "P_hat_C1": phat, "result": res, "expect": args.expect}, open(out, "w"), indent=1)
    print(f"SAVED {out}", flush=True)


if __name__ == "__main__":
    main()
