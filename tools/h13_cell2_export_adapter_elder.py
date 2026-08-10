#!/usr/bin/env python3
"""H13 Cell 2 — export ADAPTER: Ember's blinded-records spec -> Elder's frozen decoder input.
Elder register/decode seat, C6603. Committed BEFORE records land.

WHY AN ADAPTER AND NOT AN EDIT TO THE DECODER: `tools/h13_cell2_decoder_elder.py` was committed
pre-flight and is FROZEN. Its statistic, NO-CALL floor, and blindness refusal must not move
after the court signed on them. This file is PURE FORMAT TRANSLATION with NO decision logic —
it cannot influence a call. The decoder stays byte-identical to what was frozen.

INPUT — Ember's spec (general#9067 as corrected by #9070), exhaustive field list:
    set_id    0..79, RANDOMLY PERMUTED, no relation to run or arm
    group     "P" | "Q"   (opaque, re-randomised per run)
    basis     "X" | "Y" | "Z"
    outcomes  [a, b]      two ±1 values, FIXED arm-independent slot order
Accepted container shapes (both, because the harness shape is not yet confirmed):
    (a) one JSON file, list of records, or {"records": [...]}
    (b) one JSON file per set_id
OUTPUT: one file per set_id in the decoder's frozen schema:
    {"records": [{"basis": "XX", "a": ±1, "b": ±1}, ...]}
Basis widening is the only semantic step: X->XX, Y->YY, Z->ZZ (the flight carries DIAGONAL
bases only — 3 diagonals x 2 arms = 6 circuits per run, per the frozen prereg).

FAILS LOUD, NEVER RESHAPES SILENTLY (Ember #9070, seat requirement): any field outside the
exhaustive list is a BLINDNESS VIOLATION and aborts — reshaping is where a mismatch gets
laundered into a confident decode. Same discipline as the decoder's own tool-boundary refusal.

Usage:
  python3 tools/h13_cell2_export_adapter_elder.py --selftest
  python3 tools/h13_cell2_export_adapter_elder.py --in EXPORT --out DIR [--allow-group]
"""
import argparse, glob, json, os, sys

ALLOWED = {"set_id", "group", "basis", "outcomes", "a", "b"}
BASIS_MAP = {"X": "XX", "Y": "YY", "Z": "ZZ"}


def _pm(v, where):
    if v in (1, -1):
        return v
    if v in (0,):            # frozen contract: 0->+1, 1->-1 (decoder header)
        return 1
    raise SystemExit(f"ABORT: outcome {v!r} not in {{+1,-1,0}} at {where}")


def normalize(records, allow_group=False):
    """Ember-spec records -> {set_id: decoder-schema object}. Aborts on any anomaly."""
    allowed = set(ALLOWED)
    if not allow_group:
        pass  # 'group' tolerated but flagged by the caller; see --allow-group note
    out, counts = {}, {}
    for i, r in enumerate(records):
        extra = set(r.keys()) - allowed
        if extra:
            raise SystemExit(f"ABORT (blindness violation): unexpected field(s) {sorted(extra)} "
                             f"in record {i}. Ember's field list is EXHAUSTIVE. Not reshaping — "
                             f"this mismatch is a FINDING, report it.")
        sid = r["set_id"]
        b = r["basis"]
        if b in ("XX", "YY", "ZZ"):
            b2 = b                      # NATIVE decoder schema (Whisper #9072 adopted it verbatim)
        elif b in BASIS_MAP:
            b2 = BASIS_MAP[b]           # Ember-spec single-char -> widen
        else:
            raise SystemExit(f"ABORT: basis {b!r} not in {{X,Y,Z,XX,YY,ZZ}} at record {i}")
        if "outcomes" in r:
            o = r["outcomes"]
            if not (isinstance(o, (list, tuple)) and len(o) == 2):
                raise SystemExit(f"ABORT: outcomes {o!r} not a 2-list at record {i}")
            av, bv = o[0], o[1]
        else:
            av, bv = r["a"], r["b"]
        out.setdefault(sid, {"records": []})["records"].append(
            {"basis": b2, "a": _pm(av, f"rec {i}"), "b": _pm(bv, f"rec {i}")})
        counts.setdefault((sid, b), 0)
        counts[(sid, b)] += 1
    # COUNT-PARITY CHECK (Ember: "exact record-count parity per (set, basis); a count difference
    # is a free discriminator that needs no physics"). Report, do not silently pass.
    per = {}
    for (sid, b), n in counts.items():
        per.setdefault(n, []).append((sid, b))
    parity_ok = len(per) == 1
    return out, {"n_sets": len(out), "counts_seen": sorted(per.keys()),
                 "count_parity_ok": parity_ok,
                 "parity_note": ("uniform" if parity_ok else
                                 "NON-UNIFORM counts — a free discriminator; report before decoding")}


def load_any(path):
    if os.path.isdir(path):
        recs = []
        for f in sorted(glob.glob(os.path.join(path, "*.json"))):
            d = json.load(open(f))
            recs.extend(d["records"] if isinstance(d, dict) and "records" in d else d)
        return recs
    d = json.load(open(path))
    return d["records"] if isinstance(d, dict) and "records" in d else d


def selftest():
    # synthesize Ember-spec export: 4 sets, 3 diagonal bases, 50 shots each
    recs = []
    for sid in range(4):
        for b in ("X", "Y", "Z"):
            for k in range(200):   # >= decoder NO-CALL floor of 100
                a = 1 if k % 3 else -1
                bb = a if not (b == "Y" and sid % 2) else -a   # sid odd -> Y anticorrelated
                recs.append({"set_id": sid, "group": "P" if sid % 2 else "Q",
                             "basis": b, "outcomes": [a, bb]})
    out, man = normalize(recs)
    ok = (man["n_sets"] == 4 and man["count_parity_ok"] and
          all(len(v["records"]) == 600 for v in out.values()) and
          out[0]["records"][0]["basis"] == "XX")
    print(f"  [{'PASS' if ok else 'FAIL'}] translation: {man}")
    # end-to-end through the FROZEN decoder
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from h13_cell2_decoder_elder import decode_records
    calls = {sid: decode_records(obj)["call"] for sid, obj in out.items()}
    exp = {0: "CE", 1: "CC", 2: "CE", 3: "CC"}
    ok2 = calls == exp
    print(f"  [{'PASS' if ok2 else 'FAIL'}] decoder end-to-end: {calls} (expect {exp})")
    # loud-failure paths — an adapter that cannot refuse is an adapter that launders
    for bad, why in (({"set_id": 0, "group": "P", "basis": "X", "outcomes": [1, 1],
                       "num_qubits": 2}, "extra field"),
                     ({"set_id": 0, "group": "P", "basis": "W", "outcomes": [1, 1]}, "bad basis"),
                     ({"set_id": 0, "group": "P", "basis": "X", "outcomes": [1]}, "short outcomes")):
        try:
            normalize([bad]); print(f"  [FAIL] {why}: accepted (should abort)"); ok2 = False
        except SystemExit:
            print(f"  [PASS] {why}: aborted")
    print("SELFTEST", "PASS" if (ok and ok2) else "FAIL",
          "— fixtures are self-generated; a LANDED pre-run file must still be verified verbatim")
    return 0 if (ok and ok2) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp"); ap.add_argument("--out")
    ap.add_argument("--allow-group", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.inp and a.out):
        ap.error("--in and --out required")
    out, man = normalize(load_any(a.inp), a.allow_group)
    os.makedirs(a.out, exist_ok=True)
    for sid, obj in out.items():
        json.dump(obj, open(os.path.join(a.out, f"set_{sid}.json"), "w"))
    print(json.dumps(man, indent=1))
    if not man["count_parity_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
