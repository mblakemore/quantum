#!/usr/bin/env python3
"""
h14_a1_census_sweep.py — the constants-vs-weather census sweep (H14 cell A1, Whisper C5066).

Protocol (FROZEN before this ran): docs/h14-a1-constants-weather-census-protocol-FROZEN-whisper-c5066.md
Statistic: pairwise between-epoch z = |x_i - x_j| / sqrt(se_i^2 + se_j^2) within stratum; row verdict
from z_max at the frozen thresholds. Verdicts: CONSTANT (<3) / CLOCK (>=5 + pre-named structure fit
>=80%) / WEATHER (>=5, no structure) / INDETERMINATE (3-5) / UNDERPOWERED (<2 comparable epochs or
3sigma-detectable change > 50% of magnitude) / NOT-A-DIAL (analytic). Exclusion flags in source
artifacts are honored and printed. A row whose extraction fails is printed EXTRACTION-BLOCKED with
the reason — never silently skipped (no silent caps).

    python3 tools/h14_a1_census_sweep.py --selftest
    python3 tools/h14_a1_census_sweep.py            # the sweep; writes results/h14_a1_census_c5066.json
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "results")
E = os.path.join(HERE, "..", "experiments")


def jload(path):
    return json.load(open(path))


def zmax(epochs):
    """epochs: list of (label, value, se). Returns (z_max, pair)."""
    best, pair = 0.0, None
    for i in range(len(epochs)):
        for j in range(i + 1, len(epochs)):
            li, xi, si = epochs[i]
            lj, xj, sj = epochs[j]
            z = abs(xi - xj) / math.sqrt(si * si + sj * sj)
            if z > best:
                best, pair = z, (li, lj)
    return best, pair


def verdict_from(epochs, structure_fit=None, mag=None):
    """The frozen rules, one code path."""
    if len(epochs) < 2:
        return "UNDERPOWERED", {"reason": f"{len(epochs)} comparable epoch(s) in stratum"}
    if mag is not None:
        det = 3.0 * math.sqrt(sum(se * se for _, _, se in epochs) / len(epochs)) * math.sqrt(2)
        if abs(mag) > 0 and det > 0.5 * abs(mag):
            return "UNDERPOWERED", {"reason": f"3sigma-detectable change {det:.4f} > 50% of magnitude {mag:.4f}"}
    z, pair = zmax(epochs)
    info = {"z_max": round(z, 3), "worst_pair": pair, "n_epochs": len(epochs)}
    if z < 3:
        v = "CONSTANT" if len(epochs) > 2 else "CONSTANT(n=1 pair)" if len(epochs) == 2 else "CONSTANT"
        return v, info
    if z < 5:
        return "INDETERMINATE", info
    if structure_fit is not None and structure_fit >= 0.80:
        info["structure_fit"] = round(structure_fit, 3)
        return "CLOCK", info
    return "WEATHER", info


def dial_pair(d):
    """A dial dict of two floats -> (value, se): the key containing 'se' is the SE."""
    ks = list(d.keys())
    se_k = next((k for k in ks if "se" in k.lower()), ks[-1])
    v_k = next(k for k in ks if k != se_k)
    return float(d[v_k]), float(d[se_k])


def rows():
    out = []

    def row(n, name, fn):
        try:
            v, info = fn()
        except Exception as ex:
            v, info = "EXTRACTION-BLOCKED", {"reason": f"{type(ex).__name__}: {ex}"}
        out.append({"row": n, "quantity": name, "verdict": v, **info})

    # 1 — live-vs-published T1 bias
    def r1():
        for f in ("exp108b_grade.json", "exp108c_grade.json"):
            jload(os.path.join(R, f))  # measured side exists but banks no live-T1 +/- SE
        return "UNDERPOWERED", {"reason": "published side PROSE-ONLY (friction report); measured side banks "
                                          "no live-T1 value-with-SE — no mechanically comparable epochs"}
    row(1, "live-vs-published T1 bias", r1)

    # 2 — readout 0/1 asymmetry, fez pair-dial stratum (a1b, a1c)
    def r2():
        eps = []
        for lab, f in (("a1b", "h10_a1b_decode_d9nsjacsfqic73ards10.json"),
                       ("a1c", "h10_a1c_decode_d9ntia460llc73cagnfg.json")):
            d = jload(os.path.join(R, f))["dials"]
            # Booked convention recovered against the C5018 numbers (+0.036/+0.031 reproduced exactly):
            # mean over the THREE PAIR dials (s1s2, s1s3, s2s3) of |C0| - |C1|; dial SEs as magnitude-SE proxy.
            diffs, var = [], 0.0
            for k in ("s1s2", "s1s3", "s2s3"):
                v0, s0 = dial_pair(d["C0_" + k]); v1, s1 = dial_pair(d["C1_" + k])
                diffs.append(abs(v0) - abs(v1)); var += s0 * s0 + s1 * s1
            mean = sum(diffs) / len(diffs)
            se = math.sqrt(var) / len(diffs)
            eps.append((lab, mean, se))
        v, info = verdict_from(eps, mag=sum(x for _, x, _ in eps) / len(eps))
        info["epochs"] = [(l, round(x, 4), round(s, 4)) for l, x, s in eps]
        info["note"] = "pair-dial instrument stratum; armn e0/e1 census is a 2nd instrument at n=1 epoch (UNDERPOWERED separately)"
        return v, info
    row(2, "readout 0/1 asymmetry (fez, pair-dial C0-C1)", r2)

    # 3 — drift rate (kingston 2-epoch census; CLOCK structure pre-named: linear per-layer accumulation)
    def r3():
        d = jload(os.path.join(R, "exp_drift_purity_probe_census_d9kq85jhdfks73ck12gg_d9l4ncrjf64c739j1q8g.json"))
        ce = d["cross_epoch"]
        # walk each drifter for (depth -> dtheta_deg, sigma_theta)
        per_drifter = {}
        for q, sub in ce.items():
            pts = []
            def walk(node):
                if isinstance(node, dict):
                    if "dtheta_deg" in node and ("sigma_theta" in node or "sigma_dtheta" in node):
                        sk = "sigma_theta" if "sigma_theta" in node else "sigma_dtheta"
                        pts.append((node.get("depth"), float(node["dtheta_deg"]), float(node[sk])))
                    else:
                        for v in node.values():
                            walk(v)
                elif isinstance(node, list):
                    for v in node:
                        walk(v)
            walk(sub)
            if pts:
                per_drifter[q] = pts
        if not per_drifter:
            raise ValueError(f"no dtheta_deg rows found; cross_epoch keys {list(ce.keys())}, "
                             f"sample {json.dumps(list(ce.values())[0])[:200]}")
        # z = dtheta/sigma_theta per row (between-epoch tension). Structure test per the frozen text's
        # LITERAL reading: fraction of the pooled between-epoch variance explained by the pre-named model
        # (linear per-layer accumulation, per-drifter slope k_q: dtheta = k_q * depth). Per-drifter R^2s
        # also reported; the pooled number rules (it is the frozen sentence).
        zs, fits, rates = [], [], []
        ss_res_pool, allth = 0.0, []
        for q, pts in per_drifter.items():
            pts = [(dep, th, sg) for dep, th, sg in pts if dep is not None and sg > 0]
            if not pts:
                continue
            zs.append(max(abs(th) / sg for _, th, sg in pts))
            allth += [th for _, th, _ in pts]
            if len(pts) >= 3:
                num = sum(dep * th for dep, th, _ in pts); den = sum(dep * dep for dep, _, _ in pts)
                k = num / den
                ss_res = sum((th - k * dep) ** 2 for dep, th, _ in pts)
                ss_res_pool += ss_res
                mean_th = sum(th for _, th, _ in pts) / len(pts)
                ss_tot = sum((th - mean_th) ** 2 for _, th, _ in pts) or 1e-12
                fits.append(max(0.0, 1 - ss_res / ss_tot))
                rates.append(k)
        gmean = sum(allth) / len(allth)
        ss_tot_pool = sum((th - gmean) ** 2 for th in allth) or 1e-12
        fit = max(0.0, 1 - ss_res_pool / ss_tot_pool)
        z = max(zs)
        if z >= 5 and fit is not None and fit >= 0.80:
            v = "CLOCK(n=2 epochs)"
        elif z >= 5:
            v = "WEATHER"
        elif z >= 3:
            v = "INDETERMINATE"
        else:
            v = "CONSTANT(n=1 pair)"
        return v, {"z_max": round(z, 1), "structure_fit_pooled": round(fit, 3),
                   "structure_fit_mean_of_R2s_alt_reading": round(sum(fits) / len(fits), 3) if fits else None,
                   "per_layer_rates_deg": [round(k, 3) for k in rates],
                   "drifters": list(per_drifter.keys()),
                   "banked_tally_crosscheck": d.get("census_tally"),
                   "heterogeneity": "rates are PER-DRIFTER (three at ~0.01 deg/layer, one at 0.21) — the clock is "
                                    "not a universal rate; pooled R^2 is dominated by the strong drifter",
                   "note": "2 strictly-comparable kingston epochs; verdict labeled accordingly"}
    row(3, "drift rate (deg/layer, kingston)", r3)

    # 4 — DD harm contrast
    def r4():
        d = jload(os.path.join(R, "armn_dd_decode_d9prvvfv9q4s73bhe7bg.json"))
        c = d["pooled"]["none"] - d["pooled"]["xx"]
        return "UNDERPOWERED", {"reason": "all DD jobs within ~20 min on one backend = ONE epoch",
                                "within_job_contrast_none_minus_xx": round(c, 4),
                                "pooled_mde": d.get("pooled_mde")}
    row(4, "DD harm contrast (fez)", r4)

    # 5 — lambda_eff attenuation
    def r5():
        d = jload(os.path.join(R, "attenuation_map_v1_1.json"))
        seeds = d.get("v1_0_seed_points", {})
        return "UNDERPOWERED", {"reason": "one snapshot per device (5 devices); between-epoch variance "
                                          "undefined by construction", "devices": len(seeds)}
    row(5, "lambda_eff attenuation", r5)

    # 6 — switch-arm S.win across three backends (cross-backend spread IS the row statistic, labeled)
    def r6():
        eps = []
        for lab, f in (("marrakesh", "h10_b1_decode_d9ngftc60llc73ca2vo0.json"),
                       ("fez", "h10_b1_decode_d9nn1boqs0bc73e3kkh0.json"),
                       ("kingston", "h10_b1_decode_d9nqg4ssfqic73arbrf0.json")):
            d = jload(os.path.join(R, f))["S"]
            eps.append((lab, float(d["win"]), float(d["se"])))
        v, info = verdict_from(eps, mag=sum(x for _, x, _ in eps) / len(eps))
        info["epochs"] = [(l, round(x, 5), round(s, 5)) for l, x, s in eps]
        info["note"] = "CROSS-BACKEND row by frozen protocol (within-backend n=1 each); duplicate decode file excluded"
        return v, info
    row(6, "switch-arm S.win (3 backends)", r6)

    # 7 — ICO 0.177 floor: NOT-A-DIAL (pre-ruled in the protocol)
    row(7, "ICO cooling floor 0.177", lambda: ("NOT-A-DIAL", {"reason": "analytic cascade fixed point (c4720 doc), "
                                                                        "not a measured device quantity — pre-ruled in the frozen protocol"}))

    # 7' — measured ICO single-stage Delta (marrakesh, 3 jobs)
    def r7p():
        eps = []
        for lab, f in (("exp108", "exp108_grade.json"), ("exp108b", "exp108b_grade.json"),
                       ("exp108c", "exp108c_grade.json")):
            d = jload(os.path.join(R, f))
            eps.append((lab, float(d["switch"]["Delta"]), float(d["switch"]["Delta_se"])))
        v, info = verdict_from(eps, mag=sum(x for _, x, _ in eps) / len(eps))
        info["epochs"] = [(l, round(x, 5), round(s, 5)) for l, x, s in eps]
        info["note"] = ("exp108b's grade verdict is NO-TEST (calib gate) — that is a claim-gate ruling, not a data-exclusion "
                        "flag; verdict identical with or without it (checked)")
        v2, _ = verdict_from([e for e in eps if e[0] != "exp108b"])
        info["robustness_without_108b"] = v2
        return v, info
    row(7.5, "ICO single-stage Delta (marrakesh)", r7p)

    # 8 — placement bias of absolute nulls
    def r8():
        d = jload(os.path.join(R, "h13_cell5_placement_grade_d9trnegu5hac73agchf0.json"))
        return "UNDERPOWERED", {"reason": "between-epoch same-stratum comparable epochs < 2 (the cross-job sign-flip "
                                          "evidence is fez-vs-marrakesh = cross-stratum, blocked by the frozen "
                                          "no-cross-stratum-pooling rule)",
                                "within_job_placement_spread": round(float(d["G3_sum"]), 4),
                                "within_job_sigma": round(float(d["G3_sigma"]), 2),
                                "census_finding": "the 'placement is weather' claim currently rests on CROSS-stratum "
                                                  "evidence only — a same-backend two-epoch replication is the missing datapoint"}
    row(8, "placement bias of absolute nulls", r8)

    # 9 — window retention R (marrakesh; exp101 decomposition of exp95 BAD vs exp98 GOOD)
    def r9():
        d = jload(os.path.join(R, "exp101_window_retention_decomposition_c4099.json"))
        eps = []
        for lab in ("bad", "good"):
            ret = [float(x) for x in d[lab]["retention"]]
            m = sum(ret) / len(ret)
            se = (sum((x - m) ** 2 for x in ret) / (len(ret) - 1)) ** 0.5 / math.sqrt(len(ret))
            eps.append((lab, m, se))
        v, info = verdict_from(eps, mag=sum(x for _, x, _ in eps) / len(eps))
        info["epochs"] = [(l, round(x, 4), round(s, 4)) for l, x, s in eps]
        info["se_convention"] = "sd/sqrt(k) over the 6 per-k retention points (declared in results doc)"
        info["note"] = "same circuits, same qubits, 11.2 h apart; no pre-named coherent structure"
        return v, info
    row(9, "window retention R (marrakesh, 11h pair)", r9)

    # 10 — magic tax rho_stochastic (marrakesh stratum: organic 3-depth epoch + reconciliation flag_excluded)
    def r10():
        d = jload(os.path.join(R, "exp_organic_rhot_pathA.json"))
        eps = []
        for p in d["points"]:
            lo, hi = p["ci95"]
            eps.append((f"organic_{p['tag']}", float(p["rho_unsigned"]), (hi - lo) / (2 * 1.96)))
        rec = jload(os.path.join(R, "rho_t_reconciliation_c4982.json"))["marrakesh_217"]["flag_excluded"]
        val, ci = rec.get("unsigned_rho"), rec.get("ci")
        if val is not None and ci:
            eps.append(("reconc_m217", float(val), (ci[1] - ci[0]) / (2 * 1.96)))
        note = ("organic 3 depth points are ONE flight window (depth-flatness is their own claim) — the only true "
                "between-epoch pair here is organic-vs-reconciliation; kingston is a separate stratum at n=1 (UNDERPOWERED); "
                "3 of 5 attenuation-map rho_t_rows are CONFOUNDED and stay excluded")
        organ_mean = sum(x for _, x, _ in eps[:3]) / 3
        organ_se = math.sqrt(sum(s * s for _, _, s in eps[:3])) / 3
        pair = [("organic_pooled", organ_mean, organ_se)] + eps[3:]
        v, info = verdict_from(pair, mag=organ_mean)
        info["epochs"] = [(l, round(x, 4), round(s, 4)) for l, x, s in pair]
        info["organic_points"] = [(l, round(x, 4), round(s, 4)) for l, x, s in eps[:3]]
        info["note"] = note
        return v, info
    row(10, "magic tax rho_stochastic (marrakesh)", r10)

    # 11 — X-basis anisotropy (kingston): honor exp31's CONFOUNDED verdict
    def r11():
        d31 = jload(os.path.join(E, "31-xbasis-crossbackend-results.json"))
        d34 = jload(os.path.join(E, "34-xbasis-calgated-results.json"))
        v31 = str(d31["summary"].get("verdict", ""))
        excluded = "CONFOUNDED" in v31 or "INCONCLUSIVE" in v31
        info = {"reason": "exp31 self-rules INCONCLUSIVE/CONFOUNDED (flag honored) -> 1 clean epoch (exp34)",
                "exp34_ZZ_over_XX": d34["summary"].get("ZZ_over_XX_ratio"),
                "exp31_excluded": excluded}
        return ("UNDERPOWERED" if excluded else "INDETERMINATE"), info
    row(11, "X-basis Z-bias anisotropy (kingston)", r11)

    # 12 — anchor drift: recompute the prose ratios from banked artifacts
    def r12():
        a = jload(os.path.join(R, "doora_step1_anchor_n8_whisper_c5035.json"))
        b = jload(os.path.join(R, "doora_step1_anchor_paid_n8_whisper_c5037.json"))
        s = jload(os.path.join(R, "doora_shape_discriminator_n8_whisper_c5040.json"))
        se_proxy = float(s["block_A"]["se"])  # same rows/shots structure (2000 x 1) — declared proxy
        ua, ub = float(a["u_anchor"]), float(b["u_anchor"])
        eps = [("anchor_free", ua, se_proxy), ("anchor_paid", ub, se_proxy)]
        v, info = verdict_from(eps, mag=(ua + ub) / 2)
        info["recomputed_cross_job_ratio"] = round(ub / ua, 3)
        info["same_job_ratio_banked"] = s["ratio_A_over_B"]
        info["se_convention"] = "SE proxy from the same-structure shape-discriminator block (2000x1 rows); anchors bank no SE"
        info["custody_finding"] = ("the prose 2.02x is NOT reproducible from any banked artifact (banked pair gives "
                                   f"{round(ub/ua,2)}x at z={info.get('z_max')}); the 2.02x pair's artifacts are either "
                                   "unbanked or under other names — custody bug CONFIRMED and sharpened")
        info["doorb_series"] = "5 marrakesh epochs with raw cal shots exist but bank no per-epoch aggregate; decoding them is new analysis outside this sweep's frozen scope — DEFERRED, named"
        return v, info
    row(12, "anchor drift (door-a banked pair)", r12)

    return out


def selftest():
    v, i = verdict_from([("e1", 0.5, 0.01), ("e2", 0.505, 0.01)], mag=0.5)
    assert v.startswith("CONSTANT"), (v, i)
    v, i = verdict_from([("e1", 0.5, 0.01), ("e2", 0.6, 0.01)], mag=0.55)
    assert v == "WEATHER", (v, i)
    v, i = verdict_from([("e1", 0.5, 0.01), ("e2", 0.6, 0.01)], structure_fit=0.95, mag=0.55)
    assert v == "CLOCK", (v, i)
    v, i = verdict_from([("e1", 0.5, 0.01), ("e2", 0.55, 0.01)], mag=0.52)
    assert v == "INDETERMINATE", (v, i)
    v, i = verdict_from([("only", 0.5, 0.01)])
    assert v == "UNDERPOWERED", (v, i)
    v, i = verdict_from([("e1", 0.01, 0.02), ("e2", 0.012, 0.02)], mag=0.011)
    assert v == "UNDERPOWERED" and "magnitude" in i["reason"], (v, i)
    print("SELFTEST PASS: CONSTANT / WEATHER / CLOCK / INDETERMINATE / UNDERPOWERED(n) / UNDERPOWERED(power) "
          "all rule correctly on synthesized known-answer epochs.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    table = rows()
    for r in table:
        extra = {k: v for k, v in r.items() if k not in ("row", "quantity", "verdict")}
        print(f"[{r['row']}] {r['quantity']}\n    -> {r['verdict']}  {json.dumps(extra, default=str)[:400]}")
    out = os.path.join(R, "h14_a1_census_c5066.json")
    json.dump({"card": "h14_a1_census", "cycle": "C5066", "substrate": "claude-fable-5",
               "protocol": "docs/h14-a1-constants-weather-census-protocol-FROZEN-whisper-c5066.md",
               "rows": table}, open(out, "w"), indent=1)
    print(f"-> {out}")
