#!/usr/bin/env python3
"""Exp144 conv stage-1 TOP-UP wave (Ember, sole-submitter) — chair C4796: n=4 first.

TWO INTERFACE FACTS, both read from the artifacts rather than assumed (my last four
derived numbers were wrong; these are not derived):

1. The decoders hand me ROW INDICES, not candidates. They decode ORDER-BLIND — they do
   not hold the sealed sweep order, which is the entire point of the C4776 convseed: a
   decoder that cannot see candidate identities cannot fit to them. I hold the seed, so
   the row->candidate mapping is mine to do. conv_candidates(n, seed) reproduces the
   exact sealed order; alive_rows index into it.

2. The kit's `alive` param takes CANDIDATES (it feeds conv_param_row(n, cnd, wave)), and
   CONV_WAVE_SHOTS is FIXED at 60. So a top-up is an ITERATIVE 60-shot wave with SPRT
   re-evaluated between waves — NOT one 740-shot blast to the cap. I priced 740-in-one-go
   at 30 QPU-s; that was the fifth derived number I would have quoted wrong. This flies
   ONE wave and MEASURES what it cost.

  python3 exp144_topup_ember.py --dry-run --n 4
  python3 exp144_topup_ember.py --fly --n 4 --wave 2
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")
VERDICTS = os.path.join(RESULTS, "exp144_conv_s1_w1_verdicts_elder_v2.json")


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KIT = _load("kit", "exp144_flight_kit.py")
SEALER = _load("sealer", "exp144_seal_reveal_ember.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--wave", type=int, default=2)
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

    with open(SEALER.SECRETS_PATH) as f:
        sec = json.load(f)
    with open(VERDICTS) as f:
        verd = json.load(f)["instances"]

    seed = sec["convseeds"][str(a.n)]["seed"]
    order = KIT.conv_candidates(a.n, seed)      # the sealed order — mine to reproduce
    print(f"kit constants (late-bound): CONV_WAVE_SHOTS={KIT.CONV_WAVE_SHOTS} "
          f"S1_CAP={KIT.S1_CAP} | sealed order: {len(order)} candidates")

    total_rows, jobs = 0, []
    for k in KIT.KS:
        key = f"n{a.n}_k{k}"
        if key not in verd:
            print(f"  {key}: no verdict — skipping"); continue
        alive_rows = verd[key]["alive_rows"]
        if not alive_rows:
            print(f"  {key}: 0 alive — resolved, nothing to top up"); continue
        # ROW INDEX -> CANDIDATE via my sealed order. The decoders cannot do this and
        # must not be able to; that is what keeps their verdicts order-blind.
        alive = [order[i] for i in alive_rows]
        if max(alive_rows) >= len(order):
            print(f"  REFUSING {key}: row index {max(alive_rows)} exceeds order length "
                  f"{len(order)} — the verdict and my sweep order disagree.")
            return 3
        e = sec["instances"][str(a.n)][str(k)]
        pubs, man, meta = KIT.build_conv_job(a.n, k, e["terms"], e["coeffs"],
                                             wave=a.wave, alive=alive, seed=seed)
        # blindness: the manifest goes to the decoders
        blob = str(man)
        leaked = [t for t in e["terms"] if t in blob]
        if leaked:
            raise AssertionError(f"BLINDNESS BREACH: manifest leaks {leaked}")
        total_rows += len(alive)
        print(f"  {key}: {len(alive):3d} alive rows -> {len(pubs)} pubs "
              f"({len(alive)*KIT.CONV_WAVE_SHOTS:,} shots this wave)")
        jobs.append((k, pubs, man, alive_rows))

    shots = total_rows * KIT.CONV_WAVE_SHOTS
    print(f"\n  n={a.n} wave-{a.wave}: {total_rows} alive rows x {KIT.CONV_WAVE_SHOTS} "
          f"= {shots:,} shots")
    print(f"  (NOT quoting a QPU figure — chair C4796 network rule: measured only. "
          f"I will measure this wave on landing.)")

    if a.dry_run:
        print("\nDRY-RUN: nothing submitted.")
        return 0

    svc = _get_ibm_service()
    backend = svc.backend(a.backend)
    print(f"\n{backend.name}: operational={backend.status().operational} "
          f"pending={backend.status().pending_jobs}")
    for k, pubs, man, alive_rows in jobs:
        tp = [(transpile(qc, backend, optimization_level=1, seed_transpiler=144), rows, s)
              for qc, rows, s in pubs]
        job = SamplerV2(mode=backend).run(tp)
        man["job_id"] = job.job_id(); man["backend"] = a.backend
        man["alive_rows_in"] = alive_rows
        outp = os.path.join(RESULTS,
                            f"exp144_conv_n{a.n}_k{k}_w{a.wave}_manifest.json")
        if os.path.exists(outp):
            print(f"REFUSING: {os.path.basename(outp)} exists — would overwrite a record.")
            return 3
        with open(outp, "w") as f:
            json.dump(man, f, indent=1)
        print(f"  n={a.n} k={k}: job {job.job_id()} -> {os.path.basename(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
