#!/usr/bin/env python3
"""P1 First-Contact BLIND SUBMIT (Ember C4215) — injects the sealed P into the court-inspected scaffold.

Ember-only (prep angles depend on the secret P). Uses Whisper's court-inspected P-independent scaffold
(exp142_p1_flight_scaffold_whisper_c5003.build_flight @ eb76930, cleared by Elder #1260 + Ember #1263)
UNCHANGED — this file only SEALS a fresh all-Paulis∖{I} P, transpiles onto the PINNED G3 edges, and
submits. The committed manifest is P-INDEPENDENT (verified byte-identical across secrets); the secret
P + salt live OFF-GIT (chmod 600). Blind: siblings get the manifest + outcome bitstrings, never P.

  --dry-run           : DUMMY P, build via the real submit path, integrity-assert, job-count. NO seal, NO QPU.
  --submit --n N      : seal a fresh P (OS entropy), SHA-256 commit (hash public, P+salt off-git),
                        build_flight on pinned edges, submit blind, write P-independent manifest.
"""
import argparse, json, os, sys, hashlib, secrets as pysecrets
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142_p1_flight_scaffold_whisper_c5003 as SC   # court-inspected, imported UNCHANGED

GRID = (4, 6, 8)
C_PER_BASIS = SC.C_PER_BASIS
SECRET = os.path.expanduser("~/.ember-p1-secrets.json")   # OFF-GIT, chmod 600


def seal_pauli(n, rng):
    """Uniform over all-Paulis∖{I} (I-sites allowed; not the all-I identity)."""
    while True:
        P = "".join(rng.choice(list("IXYZ"), n))
        if P.count("I") < n:
            return P


def commit_hash(P, salt):
    return hashlib.sha256((P + "|" + salt).encode()).hexdigest()


def integrity_check(man, pubs, n):
    """P-INDEPENDENCE + arms + shots discipline + job-count. Manifest must be byte-identical to a
    DIFFERENT-P build (the blind invariant), carry both arms, all shots=1, emission=3^n."""
    # (1) P-independence: rebuild with a different dummy P, manifest json must be byte-identical
    _, man2 = SC.build_flight(n, seal_pauli(n, np.random.default_rng(7)), np.random.default_rng(7),
                              c_per_basis=man["c_per_basis"])
    _, man3 = SC.build_flight(n, seal_pauli(n, np.random.default_rng(8)), np.random.default_rng(8),
                              c_per_basis=man["c_per_basis"])
    assert json.dumps(man2) == json.dumps(man3), "manifest DEPENDS ON P — blind leak!"
    # (2) both arms present + emission 3^n
    kinds = [p["kind"] for p in man["pubs"]]
    assert "quantum" in kinds and "c1_covering" in kinds, "missing an arm"
    assert man["emission_bases"] == 3 ** n, f"emission {man['emission_bases']} != 3^n"
    # (3) shots==1 on every data arm
    assert all(p["shots"] == 1 for p in man["pubs"] if p["kind"] in ("quantum", "c1_covering")), "shots!=1"
    # (4) no angle/prep leak in the manifest
    s = json.dumps(man)
    assert not any(k in s for k in ("theta", "qt", "qp", "prep", "sign", "salt")), "angle/secret in manifest"
    arm_jobs = sum(1 for p in man["pubs"] if p["kind"] in ("quantum", "c1_covering"))
    return arm_jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--n", type=int)
    ap.add_argument("--backend", default="ibm_fez")
    args = ap.parse_args()

    if args.dry_run:
        print(f"P1 SUBMIT DRY-RUN (C_PER_BASIS={C_PER_BASIS}; DUMMY P, no seal, no QPU):")
        total = 0
        for n in GRID:
            Pdummy = seal_pauli(n, np.random.default_rng(100 + n))
            pubs, man = SC.build_flight(n, Pdummy, np.random.default_rng(100 + n), c_per_basis=C_PER_BASIS)
            aj = integrity_check(man, pubs, n)
            total += aj
            # copies: Q gets BQ Bell samples; C1 gets C_PER_BASIS per basis (per-candidate = C*coverage)
            print(f"  n={n}: emission={man['emission_bases']}=3^n | arm-jobs={aj} "
                  f"(Q BQ={K.BQ[n]} rows + C1 {3**n}bases×{C_PER_BASIS}) | integrity PASS "
                  f"(manifest P-independent, both arms, shots=1, no leak)")
        print(f"  TOTAL arm-jobs across {GRID} = {total}  vs ~240 Creator auth -> "
              f"{'UNDER ✓' if total <= 240 else 'OVER — re-auth'}. NO QPU, NO seal by dry-run.")
        return 0

    if args.submit:
        if args.n is None:
            print("--submit requires --n"); return 2
        n = args.n
        # ---- SEAL: fresh all-Paulis P from OS entropy, SHA-256 commit, secret OFF-GIT ----
        os_rng = np.random.default_rng()          # OS entropy
        P = seal_pauli(n, os_rng)
        salt = pysecrets.token_hex(32)
        h = commit_hash(P, salt)
        store = json.load(open(SECRET)) if os.path.exists(SECRET) else {}
        store[f"p1_allpaulis:{n}"] = {"P": P, "salt": salt, "hash": h}
        with open(SECRET, "w") as f:
            json.dump(store, f, indent=1)
        os.chmod(SECRET, 0o600)
        print(f"n={n} SEALED: commit hash (PUBLIC) = {h}  [P+salt off-git in {SECRET}, chmod 600]")

        # ---- build via the court-inspected scaffold on PINNED edges ----
        from run_exp66_qpu_partb import _get_ibm_service
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2
        svc = _get_ibm_service(); backend = svc.backend(args.backend)
        q_layout, conv_layout, bell_pairs = K.pick_layouts(backend, n)   # pinned G3 edges (re-cert clean)
        pubs, man = SC.build_flight(n, P, os_rng, c_per_basis=C_PER_BASIS)
        integrity_check(man, pubs, n)
        print(f"  built: {man['emission_bases']}=3^n bases, {man['n_jobs_est']} arm-jobs, pinned edges={bell_pairs}")

        # transpile each pub on its arm's layout, submit
        sampler = SamplerV2(mode=backend); jobs = []
        for (circ, rows, shots), meta in zip(pubs, man["pubs"]):
            k = meta["kind"]
            il = (q_layout if k == "quantum"
                  else conv_layout if k == "c1_covering"
                  else list(bell_pairs[0]))          # sentinels
            tqc = transpile(circ, backend, initial_layout=il, optimization_level=1, seed_transpiler=142)
            pub = (tqc, rows, shots) if rows is not None else (tqc, None, shots)
            job = sampler.run([pub])
            jobs.append({"job_id": job.job_id(), "kind": k, "rows": meta.get("rows", 1)})
            print(f"  job {len(jobs)}: {job.job_id()} [{k}]")

        manifest = {"experiment": "exp142_p1_first_contact_refly", "n": n, "commit_hash": h,
                    "scaffold": "whisper_c5003_eb76930", "backend": args.backend,
                    "bell_pairs": bell_pairs, "conv_layout": conv_layout, "c_per_basis": C_PER_BASIS,
                    "emission_bases": man["emission_bases"], "c1_basis_of_row": man["c1_basis_of_row"],
                    "jobs": jobs, "committer": "Ember (DC15E)", "blind": "P off-git; manifest P-independent"}
        outp = os.path.join(HERE, "..", "results", f"exp142_p1_n{n}_manifest.json")
        json.dump(manifest, open(outp, "w"), indent=1)
        print(f"n={n} SUBMITTED: {len(jobs)} jobs. P-independent manifest -> {outp} (hash {h[:16]}…)")
        return 0

    print("use --dry-run or --submit --n N")
    return 0


if __name__ == "__main__":
    sys.exit(main())
