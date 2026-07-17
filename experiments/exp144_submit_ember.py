#!/usr/bin/env python3
"""Exp144 SUBMIT DRIVER (Ember, sole-submitter). The kit ships build+selftest and states
"submit modes are EMBER's" — this is that half.

DESIGN RULE: LATE-BIND EVERY CONSTANT. Nothing from the prereg is copied into this file.
NS/KS/N_SIGN/SENT_SHOTS/CONV_WAVE_SHOTS/CONV_CHUNK_ROWS/T_FROZEN all come from the kit at
call time. Elder's Gate-2 MC moved these more than once tonight and the freeze candidate
has already been through two revisions; a driver that hardcodes them freezes a stale number
and passes anyway (c4187_001: freeze the RULE, not the VALUE — the Exp142 venue swap cost
15 minutes precisely because nothing had pinned the value).

BLINDNESS (prereg §6, pinned verbatim at chair C4776 on my ask): I hold the plaintext
because I generate it. This driver builds jobs from it MECHANICALLY. It does not compare
anything to decoder output, and for sign waves it consumes only the conveyed 2-of-2-agreed
support. No grading-relevant signal flows submitter -> network before reveal.

  python3 exp144_submit_ember.py --dry-run              # build+transpile everything, submit NOTHING
  python3 exp144_submit_ember.py --dry-run --n 4        # one rung
  python3 exp144_submit_ember.py --fly --backend ibm_kingston   # REAL submit (post-freeze only)
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
# The IBM service helper lives in ../scripts. The Exp144 kit does not add this (it never
# submits — submit is mine), so the driver must. Exp142's kit did exactly this at line 37.
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KIT = _load("kit", "exp144_flight_kit.py")
SEALER = _load("sealer", "exp144_seal_reveal_ember.py")


def load_secrets():
    with open(SEALER.SECRETS_PATH) as f:
        return json.load(f)


def verify_prereg(expected_sha):
    """The seal records the prereg sha it was bound to. Refuse to fly a seal that belongs
    to a different freeze — the Exp142 discipline of re-verifying the kit hash before every
    flight, applied to the document instead of the code."""
    sec = load_secrets()
    got = sec.get("prereg_sha")
    if expected_sha and got != expected_sha:
        print(f"REFUSING: seal is bound to prereg {got}, you passed {expected_sha}")
        return False
    return True


def build_all(n, k, terms, coeffs, seed, wave=1, alive=None):
    """Build both arms for one instance. Returns [(label, pubs, manifest, meta)]."""
    out = []
    qpubs, qman = KIT.build_quantum_job(n, terms, coeffs)
    out.append(("quantum", qpubs, qman, None))
    cpubs, cman, cmeta = KIT.build_conv_job(n, k, terms, coeffs, wave=wave,
                                            alive=alive, seed=seed)
    out.append(("conv", cpubs, cman, cmeta))
    return out


def assert_p_independent(label, manifest, terms):
    """The manifests go to the DECODERS. A planted term appearing in one is a blindness
    breach that no later discipline can undo — check the artifact, not my intentions."""
    blob = str(manifest)
    leaked = [t for t in terms if t in blob]
    if label == "quantum" and leaked:
        raise AssertionError(f"BLINDNESS BREACH: quantum manifest leaks {leaked}")
    flags = [w for w in ("planted", "truth", "answer", "secret") if w in blob.lower()]
    if flags:
        raise AssertionError(f"BLINDNESS BREACH: {label} manifest flags the answer {flags}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="build + transpile + assert; submit nothing")
    ap.add_argument("--fly", action="store_true", help="REAL submit (post-freeze only)")
    ap.add_argument("--backend", default="ibm_kingston")
    ap.add_argument("--n", type=int, default=None, help="single rung (default: all)")
    ap.add_argument("--wave", type=int, default=1)
    ap.add_argument("--prereg-sha", default=None)
    a = ap.parse_args()

    if not (a.dry_run or a.fly):
        ap.print_help()
        return 0
    if a.fly and not verify_prereg(a.prereg_sha):
        return 2

    # A dry-run that skips the submit-only imports is not a dry-run of the flight — it is
    # a dry-run of everything EXCEPT the part that only executes when it matters. Mine
    # missed a ModuleNotFoundError this way at the real flight (C4194): the submit branch
    # returns early on --dry-run, so `from run_exp66_qpu_partb import ...` was never once
    # executed by any test. Import them here, on BOTH paths.
    try:
        from run_exp66_qpu_partb import _get_ibm_service   # noqa: F401
        from qiskit import transpile                        # noqa: F401
        from qiskit_ibm_runtime import SamplerV2            # noqa: F401
        print("submit imports: resolved ✓")
    except Exception as e:
        print(f"REFUSING: submit dependencies do not import ({type(e).__name__}: {e}). "
              f"A dry-run that cannot import what the flight needs is proving nothing.")
        return 2

    # LATE-BOUND: read the kit's constants, never this file's memory of them.
    print(f"kit constants (late-bound): NS={KIT.NS} KS={KIT.KS} M={KIT.M} "
          f"N_SIGN={KIT.N_SIGN} SENT_SHOTS={KIT.SENT_SHOTS} "
          f"CONV_WAVE_SHOTS={KIT.CONV_WAVE_SHOTS} t={KIT.T_FROZEN}")

    sec = load_secrets()
    rungs = (a.n,) if a.n else KIT.NS
    total_pubs = 0

    for n in rungs:
        seed = sec["convseeds"][str(n)]["seed"]
        for k in KIT.KS:
            e = sec["instances"][str(n)][str(k)]
            terms, coeffs = e["terms"], e["coeffs"]
            for label, pubs, man, meta in build_all(n, k, terms, coeffs, seed, wave=a.wave):
                assert_p_independent(label, man, terms)
                total_pubs += len(pubs)
                if a.dry_run:
                    print(f"  n={n} k={k} {label:8s}: {len(pubs)} pubs, "
                          f"manifest P-independent ✓")
                    continue
                # REAL submit path.
                from run_exp66_qpu_partb import _get_ibm_service
                from qiskit import transpile
                from qiskit_ibm_runtime import SamplerV2
                svc = _get_ibm_service()
                backend = svc.backend(a.backend)
                tpubs = [(transpile(qc, backend, optimization_level=1,
                                    seed_transpiler=144), rows, shots)
                         for qc, rows, shots in pubs]
                job = SamplerV2(mode=backend).run(tpubs)
                man["job_id"] = job.job_id()
                man["backend"] = a.backend
                outp = os.path.join(RESULTS,
                                    f"exp144_{label}_n{n}_k{k}_w{a.wave}_manifest.json")
                with open(outp, "w") as f:
                    json.dump(man, f, indent=1)
                print(f"  n={n} k={k} {label}: job {job.job_id()} -> {outp}")

    print(f"\n{'DRY-RUN' if a.dry_run else 'SUBMITTED'}: {total_pubs} pubs across "
          f"{len(rungs)} rung(s). Blindness asserted on every manifest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
