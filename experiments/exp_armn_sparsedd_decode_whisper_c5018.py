#!/usr/bin/env python3
"""SPARSE-DD decode — READS ONLY ITS OWN FLIGHT'S ARTIFACT (Elder #5068).

The pair that closes the class from both ends:
  * builder: EMIT what you computed (the plan goes into pubs_meta)
  * decoder: REFUSE when a needed field is absent — never substitute from a sibling file.
Emit-what-you-computed makes the artifact complete; read-only-your-own-artifact makes
incompleteness LOUD instead of quietly borrowed. The first sparse decode borrowed plans from
a different build; they happened to match, so the numbers were fine and the PROVENANCE was
not — which is exactly the failure that stays invisible until it does not.

Also runs the PRE-REGISTERED REPRODUCTION CHECK before any density conclusion.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))


def main(jid):
    from ibm_multi_account import service_for_job
    man = json.load(open(os.path.join(RES, f"armn_sparsedd_manifest_{jid}.json")))
    # --- REFUSAL GATE: every field the decode needs must be in THIS artifact -------------
    missing = [m["block"] for m in man["pubs_meta"] if "n" in m and "plan" not in m]
    if missing:
        sys.exit(f"REFUSED: {len(missing)} pubs carry no `plan` in this flight's manifest. "
                 f"A decode may not substitute partner qubits from a sibling artifact "
                 f"(Elder #5068). Fix the builder and re-fly; do not decode.")
    print(f"[refusal gate] all {sum(1 for m in man['pubs_meta'] if 'n' in m)} pubs carry their "
          f"own plan — decode may proceed on this artifact alone")
    svc, _ = service_for_job(jid); res = svc.job(jid).result()
    ci = {m["block"]: i for i, m in enumerate(man["pubs_meta"]) if m["block"].startswith("cal")}

    def marg(i, q):
        c = res[i].data.meas.get_counts(); t = sum(c.values())
        return sum(n for bs, n in c.items() if bs.replace(" ", "")[::-1][q] == "1") / t

    def Ainv(q):
        e0 = marg(ci["cal0"], q); e1 = 1 - marg(ci["cal1"], q)
        return np.linalg.inv(np.array([[1 - e0, e1], [e0, 1 - e1]]))

    def purity(i, q, pl):
        qs = [pl["anc1"], pl["anc2"], pl["s1"], q]
        c = res[i].data.meas.get_counts(); tot = sum(c.values()); d = np.zeros(16)
        for bs, n in c.items():
            s = bs.replace(" ", "")[::-1]
            d[sum(int(s[x]) << (3 - j) for j, x in enumerate(qs))] += n
        d /= tot
        M = Ainv(qs[0])
        for x in qs[1:]:
            M = np.kron(M, Ainv(x))
        dc = np.clip(M @ d, 0, None); dc /= dc.sum()
        px = sum(dc[k] for k in range(16)
                 if ((((k >> 3) & 1) & ((k >> 2) & 1)) + (((k >> 1) & 1) & (k & 1))) % 2)
        return 1 - 2 * px

    rows = {}
    for i, m in enumerate(man["pubs_meta"]):
        if "n" not in m:
            continue
        rows.setdefault(m["n"], []).append(purity(i, m["q"], m["plan"]))

    # --- PRE-REGISTERED REPRODUCTION CHECK, before any density conclusion ---------------
    base = float(np.mean(rows[0]))
    prior = man["prior_none_u"]; drift = man["cross_job_drift"]
    ok = abs(base - prior) <= drift
    print(f"[reproduction] n=0 gives u={base:.4f}; DD sweep's `none` gave {prior}; "
          f"|diff| {abs(base-prior):.4f} vs cross-job drift {drift} -> "
          f"{'REPRODUCES' if ok else 'DOES NOT REPRODUCE'}")
    if not ok:
        print("REFUSED: reproduction check FAILED — the density curve is NOT reported "
              "(pre-registered). Something other than density differs between these flights.")
        json.dump({"reproduction": "FAILED", "n0_u": round(base, 4), "prior": prior},
                  open(os.path.join(RES, f"armn_sparsedd_decode_{jid}.json"), "w"), indent=1)
        return

    mde = man["power"]["mde_pooled"]
    print(f"\nSPARSE-DD DENSITY CURVE (pooled over {len(rows[0])}; MDE {mde}; gate 0.700)")
    print(f"{'n/idle':>7} {'pooled u':>9} {'sd':>7} {'vs bare':>9}  verdict")
    for n in man["densities"]:
        v = rows[n]; m = float(np.mean(v)); adv = m - base
        ver = "baseline" if n == 0 else ("WINS" if adv > mde else
                                         ("no (within MDE)" if abs(adv) <= mde else "WORSE"))
        print(f"{n:>7} {m:>9.4f} {np.std(v):>7.4f} {adv:>+9.4f}  {ver}")
    best = max(man["densities"], key=lambda n: np.mean(rows[n]))
    bm = float(np.mean(rows[best]))
    print(f"\nBEST: n={best} at u={bm:.4f} | margin over gate {bm-0.700:+.4f} "
          f"(bare margin {base-0.700:+.4f})")
    json.dump({"reproduction": "PASSED", "pooled": {str(n): round(float(np.mean(rows[n])), 4)
                                                    for n in rows},
               "mde_pooled": mde, "best_n": best, "gate": 0.700},
              open(os.path.join(RES, f"armn_sparsedd_decode_{jid}.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
