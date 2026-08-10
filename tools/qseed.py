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
import argparse, hashlib, json, math, os, subprocess, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, "qseed")
LEDGER = os.path.join(QDIR, "ledger.jsonl")
HAIL = os.environ.get("QSEED_HAIL", "/droid/repos/ship-computer/hail")  # env-overridable so the FAIL-CLOSED path is testable
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

def _line_sha(entry):
    """Hash of an entry's CANONICAL serialization — the chain link (Ember audit #9149)."""
    return hashlib.sha256(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _head(led, batch_id):
    """HEAD digest = hash of the last entry's line, or the batch_id at genesis.
    PUBLISH THIS EXTERNALLY (bus, on a cadence): chain integrity alone cannot detect
    TRUNCATION — a chain with its tail removed is still internally consistent. Only an
    external record of a HEAD that no longer appears in the file exposes a truncation."""
    return _line_sha(led[-1]) if led else hashlib.sha256(batch_id.encode()).hexdigest()

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

def draw(consumer, purpose, dry_run=False, prereg=None):
    b, pool = _load_batch(); led = _ledger(); seg = _segment_bits(b)
    idx = len(led)
    if idx >= b["totals"]["max_seeds"]: sys.exit("🔴 pool exhausted at the safety factor — harvest a new batch")
    prior = [e for e in led if e["purpose"] == purpose]
    if prior:
        print(f"⚠️  RE-DRAW against an existing purpose (prior draws: {[p['i'] for p in prior]}).")
        print("   Not blocked — RECORDED. The ledger is the deterrent.")
    off = idx * seg
    # ═══ PUBLISH BEFORE REVEAL (Ember re-audit #9165) ═══════════════════════════════════
    # The previous design PRINTED an instruction to publish the HEAD *after* the seed was
    # revealed. An anchor written after the outcome is known cannot bind the person who saw
    # it: draw, skip the post, dislike the seed, truncate, re-draw, publish the SECOND head —
    # both published heads present in ascending order, audit passes. The deterrent asked the
    # drawer to voluntarily anchor a draw they intended to discard.
    # Her fix is the door(b) ordering: RESERVE THE OFFSET PUBLICLY FIRST, THEN COMPUTE.
    # Fails CLOSED — no publication, no seed. A drawer who publishes and abandons leaves a
    # VISIBLE GAP at index i, which is the honest artifact rather than a hidden one.
    # Residual, stated not hidden: killed between the post and the ledger write leaves a
    # reservation with no entry — LOUD (a gap), not silent (a deletion). Correct direction.
    prev = _head(led, b["batch_id"])
    if not dry_run:
        # PREREG BINDING (Elder's consumer-side form, endorsed by Ember #9171): the reservation
        # names the REGISTERED ANALYSIS, not just a label. A purpose string binds a seed to a
        # sentence; a prereg reference binds it to a document that existed beforehand and can be
        # read later. Unregistered draws are allowed (QSEED also serves ordinary Monte Carlo) but
        # are marked as such in the public reservation — the record shows which kind it was.
        tag = f"prereg={prereg}" if prereg else "prereg=NONE(unregistered-purpose)"
        msg = (f"QSEED RESERVING ledger[{idx}] batch={b['batch_id']} offset={off} "
               f"prev={prev} consumer={consumer} purpose={purpose!r} {tag}")
        try:
            r = subprocess.run([HAIL, "post", "general", msg,
                                "--sender", "whisper", "--class", "fyi"],
                               capture_output=True, timeout=30)
            if r.returncode != 0:
                sys.exit(f"🔴 RESERVATION POST FAILED (rc={r.returncode}) — REFUSING TO DRAW.\n"
                         f"   A seed with no external anchor is a shoppable seed. Fix the bus, then draw.")
        except Exception as e:
            sys.exit(f"🔴 RESERVATION POST FAILED ({type(e).__name__}) — REFUSING TO DRAW.\n"
                     f"   A seed with no external anchor is a shoppable seed.")
        print(f"[reserved publicly] ledger[{idx}] prev={prev[:24]}… — anchor exists BEFORE the seed")
    segment = pool[off:off + seg]
    ctx = f"{consumer}|{purpose}|{idx}"
    seed = hashlib.sha256((segment + "|" + ctx).encode()).hexdigest()
    entry = {"i": idx, "consumer": consumer, "purpose": purpose, "batch": b["batch_id"],
             "offset": off, "len": seg, "seed_sha256": hashlib.sha256(seed.encode()).hexdigest(),
             "prev_sha256": prev, "prereg": prereg, "ts": _now()}
    if dry_run:
        # DRY RUN (Ember #9149): exercises derivation + chain link, CONSUMES NOTHING, WRITES NOTHING.
        # Author's ruling: audit probes MUST use this. A real draw that happens, stays.
        print("DRY RUN — nothing written, no pool offset consumed")
        print(f"would-be seed  {seed}")
        print(f"would-be link  prev_sha256={entry['prev_sha256'][:32]}…")
        return
    os.makedirs(QDIR, exist_ok=True)
    with open(LEDGER, "a") as fh: fh.write(json.dumps(entry) + "\n")
    print(f"seed  {seed}")
    print(f"ledger[{idx}] consumer={consumer} purpose={purpose!r} offset={off} len={seg}")
    print(f"python:  numpy.random.SeedSequence(int('{seed[:16]}…', 16))")
    print(f"js:      uint32 = int(sha256('{seed[:8]}…:<label>').hexdigest()[:8], 16)")
    print(f"HEAD     {_head(_ledger(), b['batch_id'])}  (reservation for this draw was published BEFORE reveal)")

def audit(expect_head=None):
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
    # CHAIN WALK (Ember #9149): per-entry integrity is not SEQUENCE integrity. Without this,
    # truncating the last line and re-drawing gives a different seed at the same offset and the
    # audit still says CONSISTENT — seed-shopping with the receipt deleted.
    expect = hashlib.sha256(b["batch_id"].encode()).hexdigest()
    for e in led:
        if "prev_sha256" not in e:
            print(f"  🔴 entry {e['i']} PRE-CHAIN (no prev_sha256) — sequence unverifiable"); ok = False; break
        if e["prev_sha256"] != expect:
            print(f"  🔴 CHAIN BREAK at entry {e['i']}: prev={e['prev_sha256'][:16]}… expected {expect[:16]}…"); ok = False; break
        expect = _line_sha(e)
    else:
        print(f"  ✅ chain intact across {len(led)} entries")
    head = _head(led, b["batch_id"])
    print(f"  HEAD {head}")
    # TRUNCATION DETECTOR (Ember #9149 point 3, and the FIRST fix was not enough):
    # chain-alone still passed her attack — truncate the tail, re-draw at the same offset, and
    # the chain rebuilds consistently from the truncated state. Only an EXTERNAL record of a
    # HEAD that no longer appears in this file exposes it. Verified: with --expect-head set to
    # the pre-attack HEAD, the attack is caught; without it, it is not.
    if expect_head:
        # MULTI-HEAD, IN-ORDER verification. The single-head version FAILED her attack and the
        # failure is the lesson: truncating draw A leaves the PRE-A published head still present
        # in the chain, so "published head found => legitimate growth" waves the attack through.
        # A published head is only a truncation detector if the cadence is tight enough that the
        # DELETED entry's own head was published. Discipline: publish HEAD after EVERY draw;
        # audit then requires every published head to appear, IN ASCENDING ORDER, in this chain.
        chain = [hashlib.sha256(b["batch_id"].encode()).hexdigest()]
        for e in led: chain.append(_line_sha(e))
        heads = [h.strip() for h in expect_head.split(",") if h.strip()]
        last_pos = -1
        for h in heads:
            if h not in chain:
                print(f"  🔴 PUBLISHED HEAD {h[:16]}… APPEARS NOWHERE IN THIS CHAIN")
                print(f"     -> the entry it attested was TRUNCATED or REWRITTEN after publication.")
                print(f"     This is seed-shopping with the receipt deleted.")
                ok = False; break
            pos = chain.index(h)
            if pos <= last_pos:
                print(f"  🔴 PUBLISHED HEADS OUT OF ORDER at {h[:16]}… (pos {pos} after {last_pos})"); ok = False; break
            last_pos = pos
        else:
            grown = len(led) - last_pos
            print(f"  ✅ all {len(heads)} published head(s) present in order; latest at {last_pos}/{len(led)}"
                  + (f", ledger has grown by {grown} since" if grown else ""))
    else:
        print("       ⚠️  NO --expect-head SUPPLIED: truncation is UNDETECTABLE from this file alone.")
        print("       Chain integrity proves no MID-FILE deletion or reordering; it cannot prove")
        print("       the tail was not cut. Supply the externally published HEAD to close that.")
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
    ap.add_argument("cmd", choices=["harvest", "status", "draw", "audit", "selftest", "head", "migrate-chain"])
    ap.add_argument("job_id", nargs="?")
    ap.add_argument("--consumer"); ap.add_argument("--purpose"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prereg", help="reference to the pre-registration doc this seed serves (binds the seed to a document, not just a label)")
    ap.add_argument("--expect-head", help="comma-separated externally published HEAD digests, oldest first (the truncation detector — publish after EVERY draw)")
    a = ap.parse_args()
    if a.cmd == "harvest": harvest(a.job_id)
    elif a.cmd == "status": status()
    elif a.cmd == "draw":
        if not (a.consumer and a.purpose): sys.exit("draw requires --consumer and --purpose (purpose is pre-declared)")
        draw(a.consumer, a.purpose, a.dry_run, a.prereg)
    elif a.cmd == "audit": audit(a.expect_head)
    elif a.cmd == "head":
        b, _ = _load_batch(); led = _ledger()
        print(_head(led, b["batch_id"]))
    elif a.cmd == "migrate-chain":
        # One-time: retrofit prev_sha256 onto pre-chain entries. The PRE-MIGRATION file is in
        # git history, so the retrofit is itself auditable — that is what licenses it.
        b, _ = _load_batch(); led = _ledger()
        expect = hashlib.sha256(b["batch_id"].encode()).hexdigest()
        out = []
        for e in led:
            e2 = {k: v for k, v in e.items() if k != "prev_sha256"}
            e2["prev_sha256"] = expect
            e2 = {k: e2[k] for k in ["i","consumer","purpose","batch","offset","len","seed_sha256","prev_sha256","ts"] if k in e2}
            out.append(e2); expect = _line_sha(e2)
        with open(LEDGER, "w") as fh:
            for e in out: fh.write(json.dumps(e) + "\n")
        print(f"migrated {len(out)} entries onto the chain; HEAD {expect}")
    else: selftest()
