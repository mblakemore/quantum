#!/usr/bin/env python3
"""Exp144 wave-1 QUANTUM-ARM blind decode — Elder (C6522).

Own driver, own retrieval, frozen decode_meter (sha 8beae25e...). Per frozen §3:
decode -> hash-COMMIT support (this file's JSON output committed BEFORE reading
any sibling decode) -> 2-of-2 cross-check -> convey to submitter for sign wave.
Reads manifests as kinds/rows/shots + job_id ONLY. Conv arm NOT decoded here
(F-A/F-B flown-vs-frozen findings posted separately; chair rules on recovery).
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exp144_decode_meter import shots_to_labels, decode

from qiskit_ibm_runtime import QiskitRuntimeService
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'scripts'))
from ibm_multi_account import multi_account_service  # C6578: sweep ALL accounts, not the default one

OUT = os.path.join(HERE, "..", "results", "exp144_wave1_quantum_decode_elder.json")


def bitstrings_of(pub_result):
    d = pub_result.data
    reg = getattr(d, "c", None) or getattr(d, "meas", None)
    return reg.get_bitstrings()


def sentinel_fidelity(bits):
    good = sum(1 for b in bits if b in ("00", "11"))
    return good / len(bits)


def main():
    svc = multi_account_service()
    out = {"decoder": "elder", "wave": 1, "arm": "quantum", "instances": {}}
    for mf in sorted(glob.glob(os.path.join(HERE, "..", "results",
                                            "exp144_quantum_n*_w1_manifest.json"))):
        m = json.load(open(mf))
        import re
        fm = re.search(r"_n(\d+)_k(\d+)_w1", os.path.basename(mf))
        n, k = int(fm.group(1)), int(fm.group(2))   # quantum manifests lack k field
        assert n == int(m["n"])                      # (frozen-kit gap, report-only)
        job = svc.job(m["job_id"])
        res = job.result()
        s_start = sentinel_fidelity(bitstrings_of(res[0]))
        bell = bitstrings_of(res[1])
        s_end = sentinel_fidelity(bitstrings_of(res[2]))
        labels = shots_to_labels(bell, n)
        dec = decode(labels, n, len(bell))
        out["instances"][f"n{n}_k{k}"] = {
            "support": sorted(dec["support"]),
            "abs_coeffs": {lab: round(v, 4) for lab, v in dec["abs_coeffs"].items()},
            "identity_count": dec["identity_count"],
            "off_group_mass": round(dec["off_group_mass"], 5),
            "consistency_ok": all(c["ok"] for c in dec["consistency"]),
            "n_shots": dec["n_shots"],
            "sentinels": [round(s_start, 4), round(s_end, 4)],
        }
        print(f"n={n} k={k}: support {sorted(dec['support'])} "
              f"|c| {[round(dec['abs_coeffs'][l], 3) for l in sorted(dec['support'])]} "
              f"off-group {dec['off_group_mass']:.4f} sent {s_start:.3f}/{s_end:.3f}")
    with open(os.path.abspath(OUT), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("->", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
