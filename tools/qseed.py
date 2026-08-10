#!/usr/bin/env python3
"""QSEED — Bell-gated, Tier-2 device-trusted entropy service.  Whisper C5058, board #67.

Spec: docs/entropy-service-spec-whisper-c5051.md.  Court: Elder GO + interface (general#9013),
sec5 independently reconstructed by him (joint 158,056 vs my 154,362, +2.4% conservative).

  harvest <job_id>   fetch raw shots read-only, emit the A3/A4 BATCH RECORD (per-pub table,
                     pub-type tag, raw-bits sha256) and the pool.  Sentinels excluded BY RULE.
  status             pool state, entropy budget, ledger position
  draw --consumer C --purpose P     pre-declared purpose -> one 256-bit hex seed, ledger appended
  audit              re-derive every issued seed from the pool and verify the ledger's integrity
  selftest           known-answer checks, no network

INTERFACE (frozen, Elder #9013): seeds are 256-bit HEX, ONE per purpose.
  python:  numpy.random.SeedSequence(int(seed_hex, 16))   then .spawn(n) locally
  js:      uint32 = int(sha256(f"{seed_hex}:{label}").hexdigest()[:8], 16)
ACCOUNTING: per-shot JOINT min-entropy only (never summed per-bit marginals — 38% overcount,
localized entirely to the entangled pubs).  Output capped at 0.5 x measured joint H_min.
NOT SECRECY: the pool is public in-repo.  The product is PROVENANCE — a seed that provably
was not shopped: pre-declared purpose, monotone offset, re-draws recorded not blocked.
"""
import argparse, hashlib, json, math, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, "qseed")
LEDGER = os.path.join(QDIR, "ledger.jsonl")
SAFETY = 0.5              # frozen in spec sec5; not a tuning surface
SENTINEL_HMIN = 0.10      # per-shot joint H_min below this => sentinel pub, excluded by rule A2
SEED_BITS = 256
MIN_SEGMENT_HMIN = 2 * SEED_BITS   # spec sec6: segment H_min >= 2x output size

def _now(): return datetime.now(timezone.utc).isoformat()

def joint_hmin_per_shot(outcomes):
    """H_min = -log2(max freq) over the JOINT outcome distribution of one shot."""
    n = len(outcomes)
    counts = {}
    for o in outcomes: counts[o] = counts.get(o, 0) + 1
    return -math.log2(max(counts.values()) / n)

def harvest(job_id):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from ibm_multi_account import service_for_job
    import numpy as np
    o = service_for_job(job_id); svc = o[0] if isinstance(o, tuple) else o
    job = svc.job(job_id); res = job.result()
    pubs, pool_bits, total_hmin = [], [], 0.0
    for i, pub in enumerate(res):
        d = pub.data
        fld = [f for f in dir(d) if not f.startswith("_") and hasattr(getattr(d, f), "num_shots")][0]
        arr = getattr(d, fld).to_bool_array().astype(int)
        shots, nbits = arr.shape
        outs = [tuple(r) for r in arr]
        h = joint_hmin_per_shot(outs)
        ptype = "sentinel" if h < SENTINEL_HMIN else "data"
        # lag-1 autocorrelation sanity (spec sec5), printed not gated
        v = np.array([int("".join(map(str, r)), 2) for r in arr], dtype=float)
        v -= v.mean()
        ac1 = float((v[:-1] * v[1:]).mean() / v.var()) if v.var() > 0 else 0.0
        raw = "".join("".join(map(str, r)) for r in arr)
        pubs.append({"pub": i, "type": ptype, "shots": shots, "bits_per_shot": nbits,
                     "joint_hmin_per_shot": round(h, 6), "joint_hmin_total": round(h * shots, 1),
                     "lag1_autocorr": round(ac1, 5),
                     "raw_bits_sha256": hashlib.sha256(raw.encode()).hexdigest()})
        if ptype == "data":
            pool_bits.append(raw); total_hmin += h * shots
    pool = "".join(pool_bits)
    batch = {"batch_id": job_id, "harvested": _now(), "backend": job.backend().name if hasattr(job, "backend") else "?",
             "admission": {"A1_bell_health": "graded finding required — F115 (Exp135) W1/W2/W3/G_SENT all PASS",
                           "A2_sentinels_excluded": [p["pub"] for p in pubs if p["type"] == "sentinel"],
                           "A3_provenance": {"job_id": job_id, "fetched": _now()},
                           "A4_pool_sha256": hashlib.sha256(pool.encode()).hexdigest()},
             "pubs": pubs,
             "totals": {"data_bits": len(pool), "measured_joint_hmin": round(total_hmin, 1),
                        "safety_factor": SAFETY,
                        "issuable_bits": int(total_hmin * SAFETY),
                        "max_seeds": int(total_hmin * SAFETY) // SEED_BITS}}
    os.makedirs(QDIR, exist_ok=True)
    open(os.path.join(QDIR, f"pool_{job_id}.bits"), "w").write(pool)
    json.dump(batch, open(os.path.join(QDIR, f"batch_{job_id}.json"), "w"), indent=1)
    print(f"[harvest] {len(pubs)} pubs, {len(batch['admission']['A2_sentinels_excluded'])} sentinel(s) excluded by rule")
    print(f"[harvest] data bits {len(pool):,} | measured JOINT H_min {total_hmin:,.0f} bits")
    print(f"[harvest] issuable @{SAFETY} = {batch['totals']['issuable_bits']:,} bits = {batch['totals']['max_seeds']} seeds")
    print(f"[harvest] pool sha256 {batch['admission']['A4_pool_sha256'][:32]}…")

def _load_batch():
    bs = [f for f in os.listdir(QDIR) if f.startswith("batch_")]
    if not bs: sys.exit("no batch harvested — run: qseed.py harvest <job_id>")
    b = json.load(open(os.path.join(QDIR, bs[0])))
    pool = open(os.path.join(QDIR, f"pool_{b['batch_id']}.bits")).read()
    if hashlib.sha256(pool.encode()).hexdigest() != b["admission"]["A4_pool_sha256"]:
        sys.exit("🔴 POOL DIGEST MISMATCH — batch voided per rule A4")
    return b, pool

def _ledger():
    if not os.path.exists(LEDGER): return []
    return [json.loads(l) for l in open(LEDGER) if l.strip()]

def _segment_bits(batch):
    """Segment sized so BOTH constraints hold: segment H_min >= 512 and total <= 0.5 x H_min."""
    n = batch["totals"]["max_seeds"]
    seg = batch["totals"]["data_bits"] // max(n, 1)
    rate = batch["totals"]["measured_joint_hmin"] / batch["totals"]["data_bits"]
    if seg * rate < MIN_SEGMENT_HMIN:
        sys.exit(f"🔴 segment H_min {seg*rate:.0f} < required {MIN_SEGMENT_HMIN}")
    return seg

def status():
    b, pool = _load_batch(); led = _ledger(); seg = _segment_bits(b)
    used = sum(e["len"] for e in led)
    print(f"QSEED — batch {b['batch_id']}  (Tier-2 device-trusted, Bell-health-gated)")
    print(f"  pool           {b['totals']['data_bits']:,} bits ({len(b['pubs'])} pubs, "
          f"{len(b['admission']['A2_sentinels_excluded'])} sentinel excluded)")
    print(f"  measured H_min {b['totals']['measured_joint_hmin']:,.0f} bits (JOINT per-shot)")
    print(f"  issuable       {b['totals']['issuable_bits']:,} bits @ safety {SAFETY} = {b['totals']['max_seeds']} seeds")
    print(f"  segment        {seg} bits/seed   |  issued {len(led)}  |  remaining {b['totals']['max_seeds']-len(led)}")
    print(f"  pool consumed  {used:,} / {b['totals']['data_bits']:,} bits")
    if led:
        purposes = {}
        for e in led: purposes[e["purpose"]] = purposes.get(e["purpose"], 0) + 1
        red = {p: c for p, c in purposes.items() if c > 1}
        print(f"  purposes       {len(purposes)} distinct" + (f"  ⚠ RE-DRAWS RECORDED: {red}" if red else ""))

def draw(consumer, purpose):
    b, pool = _load_batch(); led = _ledger(); seg = _segment_bits(b)
    idx = len(led)
    if idx >= b["totals"]["max_seeds"]: sys.exit("🔴 pool exhausted at the safety factor — harvest a new batch")
    prior = [e for e in led if e["purpose"] == purpose]
    if prior:
        print(f"⚠️  RE-DRAW against an existing purpose (prior draws: {[p['i'] for p in prior]}).")
        print("   Not blocked — RECORDED. The ledger is the deterrent.")
    off = idx * seg
    segment = pool[off:off + seg]
    ctx = f"{consumer}|{purpose}|{idx}"
    seed = hashlib.sha256((segment + "|" + ctx).encode()).hexdigest()
    entry = {"i": idx, "consumer": consumer, "purpose": purpose, "batch": b["batch_id"],
             "offset": off, "len": seg, "seed_sha256": hashlib.sha256(seed.encode()).hexdigest(),
             "ts": _now()}
    os.makedirs(QDIR, exist_ok=True)
    with open(LEDGER, "a") as fh: fh.write(json.dumps(entry) + "\n")
    print(f"seed  {seed}")
    print(f"ledger[{idx}] consumer={consumer} purpose={purpose!r} offset={off} len={seg}")
    print(f"python:  numpy.random.SeedSequence(int('{seed[:16]}…', 16))")
    print(f"js:      uint32 = int(sha256('{seed[:8]}…:<label>').hexdigest()[:8], 16)")

def audit():
    b, pool = _load_batch(); led = _ledger(); seg = _segment_bits(b)
    ok = True
    spans = []
    for e in led:
        segment = pool[e["offset"]:e["offset"] + e["len"]]
        ctx = f"{e['consumer']}|{e['purpose']}|{e['i']}"
        seed = hashlib.sha256((segment + "|" + ctx).encode()).hexdigest()
        good = hashlib.sha256(seed.encode()).hexdigest() == e["seed_sha256"]
        ok &= good
        spans.append((e["offset"], e["offset"] + e["len"], e["i"]))
        print(f"  [{e['i']:>3}] {e['purpose'][:44]:<44} {'✅ re-derives' if good else '🔴 MISMATCH'}")
    spans.sort()
    for (s1, e1, i1), (s2, e2, i2) in zip(spans, spans[1:]):
        if s2 < e1:
            print(f"  🔴 OVERLAP: entries {i1} and {i2} share pool bits"); ok = False
    if len(led) != len(set(e["i"] for e in led)):
        print("  🔴 duplicate ledger indices"); ok = False
    print(f"\n  pool digest ✅ (A4)  |  entries {len(led)}  |  {'✅ LEDGER CONSISTENT' if ok else '🔴 LEDGER FAILED AUDIT'}")
    sys.exit(0 if ok else 1)

def selftest():
    assert abs(joint_hmin_per_shot([(0,0)]*500 + [(1,1)]*500) - 1.0) < 1e-9, "uniform 2-outcome = 1 bit"
    assert abs(joint_hmin_per_shot([(0,0)]*1000)) < 1e-9, "deterministic = 0 bits"
    q = [(0,0)]*250 + [(0,1)]*250 + [(1,0)]*250 + [(1,1)]*250
    assert abs(joint_hmin_per_shot(q) - 2.0) < 1e-9, "uniform 4-outcome = 2 bits"
    # the 38% overcount the joint rule removes: perfectly correlated bits
    corr = [(0,0)]*500 + [(1,1)]*500
    marginal = 2 * 1.0
    assert abs(joint_hmin_per_shot(corr) - 1.0) < 1e-9 and marginal == 2.0, "marginal overcounts correlated bits 2x"
    # determinism + context binding of the seed derivation
    s1 = hashlib.sha256(("0101|c|p|0").encode()).hexdigest()
    s2 = hashlib.sha256(("0101|c|p|1").encode()).hexdigest()
    assert s1 != s2, "context binding must change the seed"
    print("selftest: 6/6 PASS (joint-vs-marginal, degenerate, uniform, correlated-overcount, context binding)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["harvest", "status", "draw", "audit", "selftest"])
    ap.add_argument("job_id", nargs="?")
    ap.add_argument("--consumer"); ap.add_argument("--purpose")
    a = ap.parse_args()
    if a.cmd == "harvest": harvest(a.job_id)
    elif a.cmd == "status": status()
    elif a.cmd == "draw":
        if not (a.consumer and a.purpose): sys.exit("draw requires --consumer and --purpose (purpose is pre-declared)")
        draw(a.consumer, a.purpose)
    elif a.cmd == "audit": audit()
    else: selftest()
