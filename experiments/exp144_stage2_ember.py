#!/usr/bin/env python3
"""Exp144 conv STAGE-2 (Ember, sole-submitter) — chair C4808 ruling A5.

A5 TERMS, implemented literally:
  1. Override pub shots to S2_SHOTS (=500) for stage-2 waves w=1..12, DISCLOSED per
     manifest ("shots_overridden_from": CONV_WAVE_SHOTS, "per": "A5/frozen §5").
  2. Kit UNTOUCHED, hash unchanged — re-verified pre-flight against the freeze record.
  3. Meter accounts FLOWN shots only. Actuals, never the plan.

WHY AN OVERRIDE IS LEGITIMATE HERE AND WAS NOT AT C4747: the kit's
build_conv_job(wave=w, alive=survivors) emits the CORRECT CIRCUITS — probe rotation per
wave is the frozen conv_probe semantics. Only the pub-shots CONSTANT is wrong for stage-2
(it is stage-1's 60). Overriding a config constant on a returned pub is config-level, not
code-level: the Exp142 A2 class. C4747 was a CODE-path defect (positional pub binding);
this is a number the frozen prose already fixed at 500 and the builder simply does not
know about. The distinction is the whole reason A5 is disclosure-and-hash rather than a
full P1 re-verify.

SELFTEST BUG FOOTNOTE (found by reading, recorded in A5, NOT patched — the frozen file
stays frozen): kit lines 481-488 run the sim at 400 shots while metering S2_SHOTS=500.
Harmless in sim; it is why the stage-2 shot count had to be adjudicated rather than
inherited.

  python3 exp144_stage2_ember.py --dry-run --n 4
  python3 exp144_stage2_ember.py --fly --n 4
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")
KIT_FROZEN_SHA = "8944fc34"          # A2-rev1, declared by Elder, chair-verified


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KIT = _load("kit", "exp144_flight_kit.py")
SEALER = _load("sealer", "exp144_seal_reveal_ember.py")


def verify_kit_hash():
    h = hashlib.sha256(open(os.path.join(HERE, "exp144_flight_kit.py"), "rb").read()).hexdigest()
    ok = h.startswith(KIT_FROZEN_SHA)
    print(f"kit hash {h[:8]} vs frozen {KIT_FROZEN_SHA}: {'MATCH ✓' if ok else 'MISMATCH ✗'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--survivors", required=True,
                    help="2-of-2 CLOSED stage-1 verdicts file (no default — a hardcoded "
                         "path goes stale silently; mine did, at wave 3)")
    ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if not (a.dry_run or a.fly):
        ap.print_help(); return 0

    try:
        from run_exp66_qpu_partb import _get_ibm_service
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2
        print("submit imports: resolved ✓")
    except Exception as e:
        print(f"REFUSING: submit deps do not import ({type(e).__name__}: {e})")
        return 2

    # A5(2): kit untouched, hash re-verified BEFORE the flight.
    if not verify_kit_hash():
        print("REFUSING: kit hash moved — A5 permits a config override on a FROZEN kit, "
              "not on a changed one.")
        return 3

    with open(SEALER.SECRETS_PATH) as f:
        sec = json.load(f)
    with open(a.survivors) as f:
        vraw = json.load(f)
    verd = vraw.get("instances", vraw)
    print(f"survivors: {os.path.basename(a.survivors)}")

    seed = sec["convseeds"][str(a.n)]["seed"]
    order = KIT.conv_candidates(a.n, seed)

    all_pubs, index, total_shots = [], [], 0
    print(f"\nA5 override: pub shots {KIT.CONV_WAVE_SHOTS} -> S2_SHOTS={KIT.S2_SHOTS} "
          f"| probe family w=1..{KIT.S2_FAMILY}")
    for k in KIT.KS:
        key = f"n{a.n}_k{k}"
        if key not in verd:
            continue
        v = verd[key]
        rows = v.get("conserved_rows", v.get("conserved", []))
        alive = v.get("alive_rows", v.get("alive", []))
        if alive:
            print(f"  REFUSING {key}: {len(alive)} rows still ALIVE — stage-1 is not "
                  f"closed for this instance; stage-2 must not run on an open rung.")
            return 3
        if not rows:
            print(f"  {key}: no survivors — skipping"); continue
        if max(rows) >= len(order):
            print(f"  REFUSING {key}: row {max(rows)} exceeds sweep order {len(order)}")
            return 3
        survivors = [order[i] for i in rows]
        e = sec["instances"][str(a.n)][str(k)]
        for w in range(1, KIT.S2_FAMILY + 1):
            pubs, man, meta = KIT.build_conv_job(a.n, k, e["terms"], e["coeffs"],
                                                 wave=w, alive=survivors, seed=seed)
            # pubs[0]=sentinel_start, pubs[1]=conv chunk, pubs[2]=sentinel_end.
            # Take the CONV pub and override ONLY its shots (A5(1)). Circuits untouched.
            qc, rowsd, _shots = pubs[1]
            all_pubs.append((qc, rowsd, KIT.S2_SHOTS))
            total_shots += len(survivors) * KIT.S2_SHOTS
            # blindness: manifests reach the decoders
            if any(t in str(man) for t in e["terms"]):
                raise AssertionError(f"BLINDNESS BREACH: manifest leaks a planted term")
        index.append({"k": k, "survivor_rows": rows, "n_survivors": len(rows),
                      "waves": KIT.S2_FAMILY})
        print(f"  {key}: {len(rows)} survivors x {KIT.S2_FAMILY} probes x "
              f"{KIT.S2_SHOTS} = {len(rows)*KIT.S2_FAMILY*KIT.S2_SHOTS:,} shots")

    print(f"\n  n={a.n} STAGE-2: {sum(i['n_survivors'] for i in index)} survivors, "
          f"{len(all_pubs)} pubs, {total_shots:,} shots (FLOWN, = metered per A5(3))")
    print(f"  (no QPU figure — measured on landing, C4796 rule)")

    if a.dry_run:
        print("\nDRY-RUN: nothing submitted.")
        return 0

    svc = _get_ibm_service()
    backend = svc.backend(a.backend)
    print(f"\n{backend.name}: operational={backend.status().operational} "
          f"pending={backend.status().pending_jobs}")
    tp = [(transpile(qc, backend, optimization_level=1, seed_transpiler=144), r, s)
          for qc, r, s in all_pubs]
    outp = os.path.join(RESULTS, f"exp144_conv_n{a.n}_stage2_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists — would overwrite a record.")
        return 3
    job = SamplerV2(mode=backend).run(tp)
    out = {"exp": "144-conv-stage2", "n": a.n, "cobatched": True,
           "job_id": job.job_id(), "backend": a.backend,
           "s2_family": KIT.S2_FAMILY, "s2_shots": KIT.S2_SHOTS,
           "shots_overridden_from": KIT.CONV_WAVE_SHOTS, "per": "A5/frozen §5",
           "shots_flown_total": total_shots, "total_pubs": len(all_pubs),
           "instances": index, "kit_sha_prefix": KIT_FROZEN_SHA,
           "survivors_source": os.path.basename(a.survivors),
           "_note": "A5 (chair C4808): pub shots overridden 60 -> 500 for stage-2. Kit "
                    "UNTOUCHED and hash re-verified pre-flight; circuits are the kit's own "
                    "(probe rotation per wave = frozen conv_probe semantics), only the "
                    "shots constant is stage-1's. Meter accounts FLOWN shots (A5(3))."}
    with open(outp, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\n  SUBMITTED STAGE-2: job {job.job_id()} -> {os.path.basename(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
