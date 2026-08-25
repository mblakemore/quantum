#!/usr/bin/env python3
"""F124 RAW-LEVEL RECOUNT (Elder C6651, court seat) — the three H10-A1 flights re-decoded from the
flown counts through each flight module's OWN build_pubs / pub_stats / grade, and diffed field by
field against the banked decode files. The C6630 exhibit reproduced the ledger figures from the
DECODE files; this closes the last gap — the decode files themselves — by fetching the job results
and re-running the frozen decode. The raw per-pub counts are BANKED beside the exhibit so no future
ratification needs a fetch (the F126 lesson: the producing artifact was missing until banked).

NEVER calls module.decode(): that function writes results/h10_a1*_decode_<job>.json — the banked
artifact under comparison. Writes only results/h10_a1*_counts_<job>_elder_c6651.json and the recount.

Usage: python3 tools/f124_raw_recount_elder_c6651.py            # all three flights
"""
import json, os, sys, importlib.util, math, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results"); sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, os.path.join(ROOT, "experiments"))
FLIGHTS = [("a1",  "h10_a1_flight_whisper_c5018",  "d9nrh1ssfqic73arcr10", "h10_a1_decode_d9nrh1ssfqic73arcr10.json"),
           ("a1b", "h10_a1b_flight_whisper_c5018", "d9nsjacsfqic73ards10", "h10_a1b_decode_d9nsjacsfqic73ards10.json"),
           ("a1c", "h10_a1c_flight_whisper_c5018", "d9ntia460llc73cagnfg", "h10_a1c_decode_d9ntia460llc73cagnfg.json")]

def load(modname):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(ROOT, "experiments", modname + ".py"))
    m = importlib.util.module_from_spec(spec); sys.modules[modname] = m; spec.loader.exec_module(m); return m

def flatten(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from flatten(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from flatten(v, f"{path}[{i}]")
    else: yield path, o

def close(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))
    return a == b

def main():
    from ibm_multi_account import service_for_job
    report = {"cycle": "C6651", "grader": "elder", "what": "F124 raw-level recount through the flight modules' frozen decode", "flights": {}}
    for tag, modname, job, decode_file in FLIGHTS:
        m = load(modname)                       # each module self-binds its `a1` (and a1c its `a1b`) by file path, exactly as its own decode() does
        pub_stats = m.pub_stats if hasattr(m, "pub_stats") else m.a1b.pub_stats   # a1c decodes through a1b.pub_stats (its decode(), line 318)
        a1mod = m.a1 if hasattr(m, "a1") else m                                    # outcome_iter_counts always comes from the A1 base module
        svc, acct = service_for_job(job)
        res = svc.job(job).result()
        pubs = m.build_pubs()
        counts_bank = []; stats = {}
        for p, r in zip(pubs, res):
            counts = r.data.c.get_counts() if hasattr(r.data, "c") else r.data.meas.get_counts()
            counts_bank.append({"name": p["name"], "kind": p.get("kind"), "counts": {str(k): int(v) for k, v in counts.items()}, "shots": int(sum(counts.values()))})
            stats[p["name"]] = pub_stats(p, a1mod.outcome_iter_counts(counts))
        json.dump({"job": job, "flight": tag, "backend": "ibm_fez", "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(), "account": acct,
                   "n_pubs": len(counts_bank), "note": "raw per-pub counts of the F124 flight, banked by Elder C6651 for the ratification — the producing artifact. Keys are the bitstrings as returned by the sampler.",
                   "pubs": counts_bank}, open(os.path.join(RES, f"h10_{tag}_counts_{job}_elder_c6651.json"), "w"), indent=1)
        out = m.grade(stats)
        banked = json.load(open(os.path.join(RES, decode_file)))
        mine = dict(flatten(out)); theirs = dict(flatten(banked))
        compared = [k for k in theirs if k in mine and not k.startswith("/job_id")]
        mism = [(k, mine[k], theirs[k]) for k in compared if not close(mine[k], theirs[k])]
        only_banked = [k for k in theirs if k not in mine and not k.startswith("/job_id")]
        report["flights"][tag] = {"job": job, "account": acct, "n_pubs": len(counts_bank), "total_shots": sum(c["shots"] for c in counts_bank),
                                  "fields_compared": len(compared), "fields_matched": len(compared) - len(mism),
                                  "mismatches": [{"field": k, "recomputed": a, "banked": b} for k, a, b in mism][:40],
                                  "banked_fields_not_recomputed": only_banked[:40],
                                  "verdict_recomputed": out.get("VERDICT_A_quorum_fact") or out.get("VERDICT"),
                                  "verdict_banked": banked.get("VERDICT_A_quorum_fact") or banked.get("VERDICT")}
        print(f"{tag}: {len(compared)-len(mism)}/{len(compared)} fields match; verdict {report['flights'][tag]['verdict_recomputed']} (banked {report['flights'][tag]['verdict_banked']}); mismatches {len(mism)}", flush=True)
    path = os.path.join(RES, "f124_raw_recount_elder_c6651.json")
    json.dump(report, open(path, "w"), indent=1, default=float); print("->", path)

if __name__ == "__main__":
    main()
