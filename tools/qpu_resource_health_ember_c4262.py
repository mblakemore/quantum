#!/usr/bin/env python3
"""QPU RESOURCE HEALTH — every account every seat can reach, with HEALTH, in one place.

Written after hand-rolling this same query six times in one night, and after the failure it
exists to prevent: on 2026-08-08 six exp142 jobs were submitted into an `open-instance` whose
`usage_limit_reached` was TRUE — an account that ACCEPTS submissions and never runs them. They
sat QUEUED and were cancelled unrun. An earlier job had already sat there 8h45m.

THREE THINGS THIS SHOWS THAT A CREDENTIAL LIST DOES NOT:

  1. FLAGGED vs REMAINING. The black-hole account displayed 738s REMAINING while flagged. A
     view that shows seconds without the flag calls it the richest tank on the board.
  2. NAME IS NOT AN IDENTIFIER. Two different accounts both name an instance "open-instance";
     only the CRN distinguishes them, and one of them is the black hole.
  3. BACKEND STATE. A tank with seconds in it is useless if its device is in maintenance —
     which is exactly why a probe sat queued tonight while the tank read 484s.

DELIBERATELY READ-ONLY. It cannot submit, cancel, or spend. A resource dashboard that can act
is a resource dashboard that can act by mistake.
"""
import argparse, json, os, re, sys

TOKEN_NAMES = ["IBMQ_TOKEN", "IBMQ_ALT", "IBMQ_ALT2", "IBMQ_ALT3"]
ENV_PATHS = ["/mnt/droid/repos/DC15E/.env", "/droid/repos/DC15W/.env"]


def tokens():
    """Collect (label, token) pairs. Values are never printed — only fingerprints."""
    import hashlib
    found, seen = [], set()
    for path in ENV_PATHS:
        if not os.path.exists(path):
            continue
        for line in open(path):
            for name in TOKEN_NAMES:
                m = re.match(rf"^{name}=(.+)$", line.strip())
                if m:
                    tok = m.group(1).strip().strip('"').strip("'")
                    fp = hashlib.sha256(tok.encode()).hexdigest()[:12]
                    if fp in seen:
                        continue
                    seen.add(fp)
                    found.append((f"{name}@{os.path.basename(os.path.dirname(path))}", fp, tok))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--backends", action="store_true", help="also poll device status (slower)")
    a = ap.parse_args()

    from qiskit_ibm_runtime import QiskitRuntimeService

    rows = []
    for label, fp, tok in tokens():
        try:
            base = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
            instances = base.instances()
        except Exception as e:
            rows.append({"token": label, "fp": fp, "error": f"{type(e).__name__}: {str(e)[:60]}"})
            continue
        for inst in instances:
            crn = inst if isinstance(inst, str) else (inst.get("crn") or str(inst))
            name = "" if isinstance(inst, str) else (inst.get("name") or "")
            try:
                svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok, instance=crn)
                u = svc.usage()
                row = {"token": label, "fp": fp, "name": name, "crn_tail": crn[-14:],
                       "consumed": u["usage_consumed_seconds"], "limit": u["usage_limit_seconds"],
                       "remaining": u["usage_remaining_seconds"],
                       "flagged": bool(u["usage_limit_reached"])}
                row["usable"] = (not row["flagged"]) and row["remaining"] > 0
                if a.backends:
                    devs = []
                    for b in svc.backends():
                        st = b.status()
                        devs.append({"name": b.name, "status": st.status_msg,
                                     "queue": st.pending_jobs})
                    row["backends"] = devs
                rows.append(row)
            except Exception as e:
                rows.append({"token": label, "fp": fp, "name": name, "crn_tail": crn[-14:],
                             "error": f"{type(e).__name__}"})

    if a.json:
        print(json.dumps(rows, indent=2))
        return 0

    print(f"{'token':<22}{'instance':<16}{'crn tail':<16}{'used/limit':<14}{'remain':>8}  health")
    print("-" * 90)
    for r in rows:
        if "error" in r:
            print(f"{r['token']:<22}{r.get('name',''):<16}{r.get('crn_tail',''):<16}"
                  f"{'':<14}{'':>8}  ERROR {r['error']}")
            continue
        health = "USABLE" if r["usable"] else ("BLACK HOLE — accepts, never runs" if r["flagged"]
                                              else "EMPTY")
        print(f"{r['token']:<22}{r['name']:<16}{r['crn_tail']:<16}"
              f"{str(r['consumed'])+'/'+str(r['limit']):<14}{r['remaining']:>7}s  {health}")
        for d in r.get("backends", []):
            mark = "" if d["status"] == "active" else f"  <-- {d['status'].upper()}"
            print(f"{'':<22}    {d['name']:<16} queue {d['queue']:<4} {d['status']}{mark}")

    usable = [r for r in rows if r.get("usable")]
    print(f"\n  {len(usable)} usable account(s), "
          f"{sum(r['remaining'] for r in usable)}s total; "
          f"{sum(1 for r in rows if r.get('flagged'))} flagged.")
    print("  READ-ONLY: this tool cannot submit, cancel or spend.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
