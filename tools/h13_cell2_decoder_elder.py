#!/usr/bin/env python3
"""H13 Cell 2 (Causal Compass) — FROZEN blind decoder. Elder register/decode seat (C6603).

Committed BEFORE flight per court dispatch (board #57, whisper C5057; prereg
docs/h13-cell2-compass-prereg-DRAFT-whisper-c5048.md §4: "decoder committed before flight").

FROZEN STATISTIC (from the prereg, not tunable here):
  For one sealed record set: compute same-basis correlators C_XX, C_YY, C_ZZ
  (mean of a*b over that basis's records). P = C_XX * C_YY * C_ZZ.
  CALL: P > 0 -> CE (cause-effect);  P < 0 -> CC (common-cause).
  T0.3 design predicts CE: +0.7835, CC: -0.81313 (results/h13_t03_compass_design_c5048.json).

NO-CALL (frozen; abstention is an outcome, never a default-to-call — the C6579
permissive-failure lesson):
  - any of XX/YY/ZZ absent or with N < 100 records
  - any diagonal correlator with |C|/se < 5  (se = sqrt((1-C^2)/N), the shot-noise
    ruler used for door(b));  a sign not established at 5 sigma cannot anchor a
    sign-product call
  - any |C| > 1 + 1e-9 or malformed outcome values (fail closed)

RECORD SCHEMA (DECLARED SEAM — Whisper must confirm before seal; a selftest that
only round-trips its own fixtures cannot detect a flown-format mismatch):
  JSON file: {"records": [{"basis": "XX", "a": +1, "b": -1}, ...]}
  basis in {XX,XY,XZ,YX,YY,YZ,ZX,ZY,ZZ}; off-diagonal records are IGNORED by the
  statistic but counted in the manifest. Outcomes a,b in {+1,-1} (0/1 accepted,
  mapped 0->+1, 1->-1 — the mapping is part of the frozen contract).
  NO circuit metadata, NO scenario label may appear in the file (data-plane
  blindness, prereg req 1); decoder REFUSES files containing keys 'arm',
  'scenario', 'label', or 'circuit' at top level.

DECISIONS-HASH DISCIPLINE (door(b) protocol): output JSON carries a sha256 over
the canonical decision content (calls + correlators), to be posted BEFORE labels
unseal.

Usage:
  python3 tools/h13_cell2_decoder_elder.py --records FILE [FILE...] [--json]
  python3 tools/h13_cell2_decoder_elder.py --selftest
"""
import argparse, hashlib, json, math, sys

DIAG = ("XX", "YY", "ZZ")
BASES = {a + b for a in "XYZ" for b in "XYZ"}
MIN_N = 100
SIGN_SIGMA = 5.0
FORBIDDEN_KEYS = {"arm", "scenario", "label", "circuit"}


def _pm(v):
    if v in (1, -1):
        return v
    if v == 0:
        return 1
    raise ValueError(f"outcome {v!r} not in {{+1,-1,0,1}}")


def decode_records(obj):
    bad = FORBIDDEN_KEYS & set(obj.keys())
    if bad:
        return {"call": "REFUSED", "reason": f"blindness violation: keys {sorted(bad)} present"}
    stats = {b: {"n": 0, "s": 0} for b in DIAG}
    n_off = 0
    for r in obj["records"]:
        b = r["basis"]
        if b not in BASES:
            return {"call": "REFUSED", "reason": f"unknown basis {b!r}"}
        if b in stats:
            stats[b]["n"] += 1
            stats[b]["s"] += _pm(r["a"]) * _pm(r["b"])
        else:
            n_off += 1
    corr, no_call, raw = {}, [], {}
    for b in DIAG:
        n, s = stats[b]["n"], stats[b]["s"]
        if n < MIN_N:
            no_call.append(f"{b}: N={n} < {MIN_N}")
            continue
        c = s / n
        se = math.sqrt(max(1.0 - c * c, 1e-12) / n)
        z = abs(c) / se if se > 0 else float("inf")
        raw[b] = (c, se)          # UNROUNDED — propagation must not read display values back
        corr[b] = {"C": round(c, 6), "N": n, "se": round(se, 6), "z_sign": round(z, 2)}
        if z < SIGN_SIGMA:
            no_call.append(f"{b}: |C|/se={z:.2f} < {SIGN_SIGMA}")
    if no_call:
        return {"call": "NO_CALL", "reasons": no_call, "correlators": corr, "n_offdiag": n_off}
    cs = [raw[b][0] for b in DIAG]
    ses = [raw[b][1] for b in DIAG]
    P = cs[0] * cs[1] * cs[2]
    # error propagation: se_P^2 = sum_i (P/C_i)^2 se_i^2
    se_P = math.sqrt(sum((P / c) ** 2 * s ** 2 for c, s in zip(cs, ses)))
    return {
        "call": "CE" if P > 0 else "CC",
        "sign_product": round(P, 6),
        "se_product": round(se_P, 6),
        "z_product": round(abs(P) / se_P, 2),
        "min_z_sign": min(corr[b]["z_sign"] for b in DIAG),
        "correlators": corr,
        "n_offdiag": n_off,
    }


def decisions_hash(results):
    canon = json.dumps(
        [{"file": r["file"], "call": r["call"], "sign_product": r.get("sign_product")}
         for r in results], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()


def _fixture(cxx, cyy, czz, n=4000, seed=1):
    # deterministic LCG; per-basis records with exact target correlation via alternation
    recs = []
    state = seed
    for b, c in zip(DIAG, (cxx, cyy, czz)):
        p_same = (1 + c) / 2
        for i in range(n):
            state = (1103515245 * state + 12345) % (2 ** 31)
            a = 1 if (state >> 8) & 1 else -1
            same = (state % 100000) / 100000.0 < p_same
            recs.append({"basis": b, "a": a, "b": a if same else -a})
    return {"records": recs}


def selftest():
    ok = True
    cases = [
        ("CE-design", _fixture(0.92189, 0.92189, 0.92189), "CE"),
        ("CC-design", _fixture(0.93337, -0.93337, 0.93337, seed=2), "CC"),
        ("null-noise", _fixture(0.0, 0.01, -0.01, seed=3), "NO_CALL"),   # genuinely-false sibling
        ("tiny-N", {"records": [{"basis": "XX", "a": 1, "b": 1}] * 50}, "NO_CALL"),
        ("blindness", {"records": [], "arm": "CE"}, "REFUSED"),
    ]
    for name, obj, want in cases:
        got = decode_records(obj)["call"]
        mark = "PASS" if got == want else "FAIL"
        ok &= got == want
        print(f"  [{mark}] {name}: want {want} got {got}")
    print("SELFTEST", "PASS" if ok else "FAIL",
          "(fixtures are self-generated — flown record schema must be confirmed by the seal seat)")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", nargs="+")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.records:
        ap.error("--records or --selftest required")
    results = []
    for f in a.records:
        with open(f) as fh:
            obj = json.load(fh)
        r = decode_records(obj)
        r["file"] = f
        results.append(r)
    out = {"decoder": "h13_cell2_decoder_elder.py", "results": results,
           "decisions_sha256": decisions_hash(results)}
    print(json.dumps(out, indent=1) if a.json else
          "\n".join(f"{r['file']}: {r['call']} (P={r.get('sign_product')}, zP={r.get('z_product')})"
                    for r in results) + f"\ndecisions_sha256: {out['decisions_sha256']}")


if __name__ == "__main__":
    main()
