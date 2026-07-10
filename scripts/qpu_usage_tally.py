#!/usr/bin/env python3
"""Total QPU usage tally across the current IBM account (Whisper C4535).
Enumerates all runtime jobs visible to these credentials and sums measured usage."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp66_qpu_partb import _get_ibm_service
from collections import defaultdict

svc = _get_ibm_service()
tot, by_backend, by_month, rows, nofig = 0.0, defaultdict(float), defaultdict(float), [], 0
seen = 0
for job in svc.jobs(limit=500):
    seen += 1
    try:
        u = None
        try:
            u = job.usage()  # seconds (newer API)
        except Exception:
            m = job.metrics()
            u = (m.get("usage", {}) or {}).get("seconds") or (m.get("usage", {}) or {}).get("quantum_seconds")
        if u is None:
            nofig += 1
            continue
        u = float(u)
        tot += u
        bk = getattr(job, "backend", lambda: None)()
        bname = getattr(bk, "name", str(bk)) if bk else "?"
        by_backend[bname] += u
        cd = str(job.creation_date)[:7]
        by_month[cd] += u
        rows.append((str(job.job_id()), bname, cd, u, str(job.status())))
    except Exception as e:
        nofig += 1

print(f"jobs seen: {seen}, with usage figures: {len(rows)}, without: {nofig}")
print(f"\nTOTAL measured on THIS account: {tot:.1f} quantum-seconds")
print("\nBy backend:")
for k, v in sorted(by_backend.items(), key=lambda kv: -kv[1]):
    print(f"  {k:16s} {v:8.1f}s")
print("\nBy month:")
for k, v in sorted(by_month.items()):
    print(f"  {k}: {v:8.1f}s")
print("\nTop 12 jobs by usage:")
for jid, b, m, u, st in sorted(rows, key=lambda r: -r[3])[:12]:
    print(f"  {jid}  {b:14s} {m}  {u:7.1f}s  {st}")
