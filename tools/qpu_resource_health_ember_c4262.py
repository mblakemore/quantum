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

# C5073 (#154 fix + Creator directive "add IBMQ_ALT5"): DISCOVER every IBMQ_* token instead of a
# hardcoded list. The old list ["IBMQ_TOKEN","IBMQ_ALT","IBMQ_ALT2","IBMQ_ALT3"] was missing ALT4
# AND ALT5 (both token-only, in DC15W/.env), so this feeder never probed them and their registry
# rows went stale/absent — exactly board #154. Regex mirrors ibm_multi_account.TOKEN_VAR_RE, so any
# future IBMQ_ALTn is picked up automatically (structural fix: discover, don't enumerate).
TOKEN_RE = re.compile(r"^(IBMQ_[A-Z0-9_]*|QISKIT_IBM_TOKEN)=(.+)$")
ENV_PATHS = ["/mnt/droid/repos/DC15E/.env", "/droid/repos/DC15W/.env"]


def tokens():
    """Collect (label, token) pairs for every IBMQ_* var. Values never printed — only fingerprints."""
    import hashlib
    found, seen = [], set()
    for path in ENV_PATHS:
        if not os.path.exists(path):
            continue
        for line in open(path):
            m = TOKEN_RE.match(line.strip())
            if not m:
                continue
            name, tok = m.group(1), m.group(2).strip().strip('"').strip("'")
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
    ap.add_argument("--need", type=float, default=181.0,
                    help="seconds the job needs; health is reported RELATIVE to this. "
                         "Default 181 = the door (b) registered flight. Health is not a "
                         "property of an account, it is a property of an account AND a job.")
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
                # The FULL CRN is the identity (lesson 2 above: NAME IS NOT AN IDENTIFIER — two accounts
                #                 both call an instance "open-instance" and only the CRN
                #                 separates them, one of which is the black hole). The tail
                #                 is for HUMAN display only; a consumer keying on it would
                #                 reintroduce exactly the ambiguity this tool exists to kill.
                #                 A CRN is an account identifier, not a credential — tokens
                #                 are still never emitted, only fingerprints.
                row = {"token": label, "fp": fp, "name": name, "crn": crn, "crn_tail": crn[-14:],
                       "consumed": u["usage_consumed_seconds"], "limit": u["usage_limit_seconds"],
                       "remaining": u["usage_remaining_seconds"],
                       "flagged": bool(u["usage_limit_reached"])}
                # C4262 (Whisper review #7533): "USABLE" as a BOOLEAN reproduced the night's
                # own near-miss — WhisperPaid read USABLE on 10 seconds. Not flagged is not the
                # same as able to carry the job. Health is relative to a REQUIREMENT or it is
                # not health; a binary flag invites exactly the read that put six jobs into an
                # account showing 738s.
                row["usable"] = (not row["flagged"]) and row["remaining"] > 0
                row["fits_need"] = row["usable"] and row["remaining"] >= a.need
                row["margin"] = (row["remaining"] / a.need) if a.need else float("inf")
                if a.backends:
                    devs = []
                    for b in svc.backends():
                        st = b.status()
                        devs.append({"name": b.name, "status": st.status_msg,
                                     "queue": st.pending_jobs})
                    row["backends"] = devs
                rows.append(row)
            except Exception as e:
                rows.append({"token": label, "fp": fp, "name": name, "crn": crn, "crn_tail": crn[-14:],
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
        if r["flagged"]:
            health = "BLACK HOLE — accepts, never runs"
        elif r["remaining"] <= 0:
            health = "EMPTY"
        elif r["fits_need"]:
            health = f"FITS  ({r['margin']:.1f}x the {a.need:.0f}s need)"
        else:
            health = f"TOO SMALL — {r['remaining']}s < {a.need:.0f}s needed"
        print(f"{r['token']:<22}{r['name']:<16}{r['crn_tail']:<16}"
              f"{str(r['consumed'])+'/'+str(r['limit']):<14}{r['remaining']:>7}s  {health}")
        for d in r.get("backends", []):
            mark = "" if d["status"] == "active" else f"  <-- {d['status'].upper()}"
            print(f"{'':<22}    {d['name']:<16} queue {d['queue']:<4} {d['status']}{mark}")

    fits = [r for r in rows if r.get("fits_need")]
    alive = [r for r in rows if r.get("usable")]
    print(f"\n  need {a.need:.0f}s: {len(fits)} account(s) FIT "
          f"({', '.join(r['name'] for r in fits) if fits else 'NONE'}).")
    print(f"  {len(alive)} unflagged, {sum(r['remaining'] for r in alive)}s total; "
          f"{sum(1 for r in rows if r.get('flagged'))} flagged.")
    if alive and not fits:
        print("  ** NO SINGLE ACCOUNT CARRIES THIS JOB. Seconds exist; capacity does not. **")
    print("  READ-ONLY: this tool cannot submit, cancel or spend.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
