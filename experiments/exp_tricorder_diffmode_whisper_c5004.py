#!/usr/bin/env python3
"""THE TRICORDER — Diff-Mode ($0 build+run, Whisper C5004, Creator directive: "run H9B item 1").

H9 B-side invention #1/#8: a quantum-memory scanner that reads a process's per-site fingerprint and,
in DIFF-MODE, the DIFFERENCE between a device and a reference (or one device across an event) — flagging
drift/tamper by differential fingerprint (Elder #1400: "the nearest real customer"), and overlaying the
COHERENCE CHARACTER of each drifted site (P2 difference-witness / revival test).

HONEST SCOPE (the B-side label, enforced in the output):
  • [GROUNDED] the INSTRUMENT — the differential-fingerprint + coherence-verdict logic — is real and
    demonstrated here on FLOWN cross-block drift data (the census that found drifters {73,26,53,23}).
  • [SEPARATION-OWED] the two-copy quantum-memory SAMPLE-ADVANTAGE for the *difference* is NOT claimed
    here: this demo runs on single-copy depth-sweep data (|<Z>| marginal bias), not the F119 two-copy
    Bell channel. That the DIFF inherits F119's sample-saving is its own argument (Elder no-free-ride).
  So this is the scanner working as an instrument — NOT a quantum-advantage claim for diff-mode.

$0: reads existing decoded results, spends no QPU (the n=8 capstone queue is untouched).
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
DRIFTALIVE = os.path.join(QROOT, "results", "exp_crossblock_driftalive_decoded.json")
WIDESWEEP = os.path.join(QROOT, "results", "exp_crossblock_widesweep_decoded.json")
FLAG_SIGMA = 3.0        # differential-fingerprint drift threshold (|sigma| >= this = flagged site)


def diff_scan(device_sites, ref_baseline, ref_sigma, coherence_map, epoch_dev=None, epoch_coh=None):
    """DIFF-MODE core: given per-site device signal vs a reference baseline+robust-sigma, return the
    differential fingerprint (per-site drift in sigma) + coherence overlay + a scan verdict.
    device_sites: {site: signed_excess_over_ref}  (already ref-subtracted, in raw units)
    ref_baseline/ref_sigma: the reference population's median + robust sigma (the 'stable' reference)
    coherence_map: {site: {'mechanism':..., 'revival_amplitude':...}} from the revival test."""
    report = {"instrument": "Tricorder Diff-Mode", "by": "whisper c5004",
              "mode": "DIFFERENCE (device vs reference population)",
              "grounded": "instrument demonstrated on flown drift data",
              "separation_owed": "two-copy sample-advantage for the DIFF not claimed (single-copy depth-sweep data)",
              "reference": {"baseline_decay": ref_baseline, "robust_sigma": ref_sigma},
              "epochs": {"device_fingerprint": epoch_dev, "coherence_overlay": epoch_coh,
                         "note": ("cross-epoch overlay ~3h apart (Elder #1423): the drifter SET is consistent "
                                  "across the arc, BUT the per-site coherent/decoherent MECHANISM label assumes it "
                                  "did NOT flip in the gap — and calibration-epoch volatility (mechanism shifts "
                                  "across recals; kingston ~3hr recal cadence) makes that a real threat, not just a "
                                  "set-membership question. Museum-demo: instrument works [GROUNDED]. Actionable "
                                  "correctable/retire verdict: needs a SAME-EPOCH drift+revival pass to pin the "
                                  "mechanism to the fingerprint it labels."),
                         "actionable_fix": "same-epoch drift+revival pass (pins mechanism to the fingerprint)"},
              "flag_threshold_sigma": FLAG_SIGMA, "sites": {}}
    flagged, stable, anomalous = [], [], []
    for site, excess in device_sites.items():
        nsig = excess / ref_sigma if ref_sigma else 0.0
        coh = coherence_map.get(site, {})
        mech = coh.get("mechanism", "uncharacterized")
        entry = {"drift_sigma": round(nsig, 2), "excess_raw": round(excess, 4),
                 "coherence": mech, "revival_amplitude": coh.get("revival_amplitude")}
        # classify
        if nsig <= -FLAG_SIGMA:
            entry["verdict"] = "ANOMALOUS (signal GREW vs reference — inverted drift)"
            anomalous.append(site)
        elif nsig >= FLAG_SIGMA:
            entry["verdict"] = "DRIFTED (flagged)"
            flagged.append(site)
        elif abs(nsig) >= 1.0:
            entry["verdict"] = "MARGINAL (sub-threshold drift)"
        else:
            entry["verdict"] = "STABLE"
            stable.append(site)
        # actionable recommendation from the coherence character
        if entry["verdict"].startswith(("DRIFTED", "ANOMALOUS")):
            xep = " [mechanism is CROSS-EPOCH — pin with a same-epoch pass before acting]"
            if "COHERENT" in mech:
                entry["action"] = "coherent drift = UNITARY = in-principle correctable (recalibrate phase / track)" + xep
            elif "no revival" in mech or "decoher" in mech.lower():
                entry["action"] = "decoherent = information loss = NOT correctable by phase (recalibrate/retire site)" + xep
            else:
                entry["action"] = "characterize coherence before deciding (run revival test)"
        report["sites"][f"phys{site}"] = entry
    report["summary"] = {
        "flagged_drifted": [f"phys{s}" for s in flagged],
        "anomalous": [f"phys{s}" for s in anomalous],
        "stable": [f"phys{s}" for s in stable],
        "scan_verdict": (f"DRIFT DETECTED at {len(flagged)+len(anomalous)} site(s) "
                         f"({len(flagged)} drifted, {len(anomalous)} anomalous); "
                         f"differential fingerprint distinguishes them from the stable reference"),
    }
    return report


def demo():
    da = json.load(open(DRIFTALIVE)); ws = json.load(open(WIDESWEEP))
    ref_baseline = da["nonfdrifter_median_decay"]; ref_sigma = da["robust_sigma"]
    # DEVICE fingerprint = the drifters' excess-over-population (the differential signal, ref-subtracted)
    device_sites = {int(q): v["excess_over_pop"] for q, v in da["drifters"].items()
                    if v.get("excess_over_pop") is not None}
    # COHERENCE overlay from the revival (wide-depth) test
    coherence_map = {int(q): {"mechanism": v.get("mechanism"), "revival_amplitude": v.get("revival_amplitude")}
                     for q, v in ws.get("drifters", {}).items()}
    rep = diff_scan(device_sites, ref_baseline, ref_sigma, coherence_map,
                    epoch_dev=da.get("cal_epoch"), epoch_coh=ws.get("cal_epoch"))
    out = os.path.join(QROOT, "results", "tricorder_diffmode_scan_whisper_c5004.json")
    json.dump(rep, open(out, "w"), indent=1)
    # pretty print the scan
    print("=" * 78)
    print("  THE TRICORDER — DIFF-MODE SCAN  (device vs stable reference population)")
    print("=" * 78)
    print(f"  reference: stable-population decay {ref_baseline:.3f} +/- {ref_sigma:.3f} (robust)")
    print(f"  epochs: fingerprint {rep['epochs']['device_fingerprint']} | coherence {rep['epochs']['coherence_overlay']}")
    print(f"  flag threshold: |{FLAG_SIGMA}sigma|\n")
    print(f"  {'SITE':8s} {'DRIFT(sigma)':>12s}  {'VERDICT':<38s} COHERENCE")
    print("  " + "-" * 74)
    for site, e in sorted(rep["sites"].items(), key=lambda kv: -abs(kv[1]["drift_sigma"])):
        coh = (e["coherence"] or "")[:26]
        print(f"  {site:8s} {e['drift_sigma']:>12.2f}  {e['verdict']:<38s} {coh}")
        if "action" in e:
            print(f"  {'':8s} {'':>12s}  -> {e['action']}")
    print("\n  SCAN VERDICT:", rep["summary"]["scan_verdict"])
    print(f"  flagged drifted: {rep['summary']['flagged_drifted']}  anomalous: {rep['summary']['anomalous']}"
          f"  stable: {rep['summary']['stable']}")
    print("\n  [GROUNDED] instrument works: the differential fingerprint separates drifted sites from the")
    print("             stable reference AND characterizes each drift as coherent(correctable)/decoherent.")
    print("  [SEPARATION-OWED] two-copy sample-advantage for the DIFF not claimed (single-copy depth-sweep data).")
    print(f"\n  scan -> {out}")
    return rep


if __name__ == "__main__":
    demo()
