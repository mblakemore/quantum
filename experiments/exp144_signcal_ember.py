#!/usr/bin/env python3
"""Exp144 DUMMY SIGN-RECOVERY CALIBRATION (Ember, sole submitter) — chair C4812.

WHAT THIS IS: a public, known-answer hardware-capability measurement. m=3 commuting
full-weight Paulis, grid coeffs, KNOWN signs (no seed/seal — everything public). Per term:
signblock_circuit (prep +1 iQP eigenstate -> V -> measure probe Q), N_SIGN shots on the
fingerprint-gated support qubits. Elder decodes on landing for 2-of-2: per term
<Q(t)> -> recovered sign -> vs KNOWN sign -> recovery rate, compared to the 0.90 bar.

FRAMING (advisor + chair): sign blocks run on ACCEPTED support; stage-1 support is VOID.
So this is a STANDALONE capability number, NOT a gate clearing a sign-block flight that can
happen. Reported as capability.

COUPLING DISCIPLINE (c4195_001, one cycle earlier): Elder's truth-gate sim is the
interpretation key. The dummy's FRAME (sign pattern, coeffs, recovery metric, layout) must
match what his sim models, or the recovery->att->decision mapping is invalid. Those four
knobs are set FROM HIS REPLY, not chosen here. The circuit machinery + the noiseless
pre-flight gate are frame-agnostic and built now.

NOISELESS GATE (necessary, NOT sufficient): proves circuit+decode recover the KNOWN signs
at zero noise. It says nothing about whether the flown number maps to Elder's sim — that is
what the frame-match (above) buys. --fly is REFUSED unless the noiseless gate passes.

  python3 exp144_signcal_ember.py --gate                      # noiseless known-answer gate only
  python3 exp144_signcal_ember.py --dry-run --layout path     # build+transpile, submit nothing
  python3 exp144_signcal_ember.py --fly --layout path --signs +,-,+ --coeffs 0.25,0.20,0.15
"""
import argparse
import functools
import importlib.util
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KIT = _load("kit", "exp144_flight_kit.py")

# m=3 commuting full-weight at n=4 — the selftest structure Elder's sim is likeliest to
# model. XXXX, XXYY, XXZZ pairwise commute (each pair differs on an even # of sites).
N = 4
TERMS = ["XXXX", "XXYY", "XXZZ"]

I2 = np.eye(2, dtype=complex)
PM = {"I": I2, "X": np.array([[0, 1], [1, 0]], complex),
      "Y": np.array([[0, -1j], [1j, 0]], complex),
      "Z": np.array([[1, 0], [0, -1]], complex)}
_kron = lambda s: functools.reduce(np.kron, [PM[c] for c in s])


def _commutes(a, b):
    return sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y) % 2 == 0


def probe_for(target, others):
    """Q: anticommutes with target, commutes with every other term (selftest rule)."""
    return next("".join(p) for p in itertools.product("IXYZ", repeat=N)
                if set(p) != {"I"}
                and not _commutes("".join(p), target)
                and all(_commutes("".join(p), t) for t in others))


def prep_for(target, probe):
    """+1 eigenstate letters/signs of R = i*Q*P via matrix (public dummy — known answer)."""
    R = 1j * _kron(probe) @ _kron(target)
    Slab = coef = None
    for p in itertools.product("IXYZ", repeat=N):
        s = "".join(p)
        tr = np.trace(_kron(s).conj().T @ R) / 2 ** N
        if abs(abs(tr) - 1) < 1e-9:
            Slab, coef = s, float(np.real(tr)); break
    signs = [0] * N
    if coef < 0:
        signs[next(i for i, c in enumerate(Slab) if c != "I")] = 1
    return Slab, signs


def build_pubs(coeffs):
    """One signblock pub per term. coeffs carry sign (negative => negative coeff)."""
    pubs, meta = [], []
    for idx, term in enumerate(TERMS):
        others = [t for j, t in enumerate(TERMS) if j != idx]
        probe = probe_for(term, others)
        Slab, psigns = prep_for(term, probe)
        thetas = [c * KIT.T_FROZEN for c in coeffs]
        qc = KIT.signblock_circuit(N, TERMS, thetas, idx, probe, Slab, psigns)
        pubs.append((qc, probe))
        meta.append({"term": term, "coeff": coeffs[idx], "known_sign": 1 if coeffs[idx] >= 0 else -1,
                     "probe": probe, "prep": Slab, "want_Q": -math.sin(2 * thetas[idx])})
    return pubs, meta


def decode_sign(bitstrings, probe):
    """<Q> from outcomes -> recovered sign. Independent of the kit path."""
    vals = []
    for s in bitstrings:
        b = s[::-1]
        v = 1
        for i, c in enumerate(probe):
            if c != "I":
                v *= (1 - 2 * int(b[i]))
        vals.append(v)
    q = float(np.mean(vals))
    return q, (1 if q >= 0 else -1) * -1  # recovered coeff sign = -sign(<Q>) since <Q>=-sin(2th)


def noiseless_gate(coeffs):
    """KNOWN-ANSWER gate: recover every planted sign at zero noise, or REFUSE the fly."""
    from qiskit.primitives import StatevectorSampler
    pubs, meta = build_pubs(coeffs)
    smp = StatevectorSampler()
    ok = 0
    print("=== NOISELESS KNOWN-ANSWER GATE (necessary, not sufficient) ===")
    for (qc, probe), m in zip(pubs, meta):
        res = smp.run([(qc, None, 20000)]).result()
        d = res[0].data
        bits = (d.c if hasattr(d, "c") else d.meas).get_bitstrings()
        q, rec = decode_sign(bits, probe)
        hit = (rec == m["known_sign"])
        ok += hit
        print(f"  {m['term']} c={m['coeff']:+.2f} probe {probe}: <Q>={q:+.4f} "
              f"(want {m['want_Q']:+.4f}) recovered sign {rec:+d} vs known {m['known_sign']:+d} "
              f"-> {'HIT' if hit else 'MISS'}")
    print(f"  compared: {len(meta)} terms | recovered: {ok}/{len(meta)}")
    return ok == len(meta) and len(meta) > 0


def resolve_layout(kind):
    """Physical qubits for logical 0..3. 'path' = connected min-CX 4-chain (right for a
    CX-heavy V); 'idle' = 4 best idle-ranked §8 qubits; 'transpiler' = let it choose."""
    if kind == "transpiler":
        return None
    with open(os.path.join(RESULTS, "exp144_layout_gated_ember.json")) as f:
        g = json.load(f)
    if kind == "idle":
        flat = [q for e in g["eligible"] for q in e["pair"]]
        return flat[:N]
    if kind == "path":
        # a connected 4-qubit chain among eligible qubits, chosen on landing from
        # backend coupling — placeholder until --fly resolves it against the real map.
        return "PATH"
    raise ValueError(kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true", help="run the noiseless known-answer gate only")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--coeffs", default="0.25,0.20,0.15",
                    help="per-term magnitudes (grid); sign taken from --signs")
    ap.add_argument("--signs", default="+,+,+",
                    help="per-term KNOWN sign pattern, e.g. +,-,+ (frame — set from Elder's sim)")
    ap.add_argument("--layout", default="path", choices=["path", "idle", "transpiler"])
    ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()

    mags = [float(x) for x in a.coeffs.split(",")]
    sgn = [1 if s.strip().startswith("+") else -1 for s in a.signs.split(",")]
    if not (len(mags) == len(sgn) == len(TERMS)):
        print(f"REFUSING: need {len(TERMS)} coeffs and signs"); return 2
    coeffs = [m * s for m, s in zip(mags, sgn)]
    print(f"frame: terms={TERMS} coeffs={coeffs} layout={a.layout} N_SIGN={KIT.N_SIGN}")

    if a.gate:
        return 0 if noiseless_gate(coeffs) else 1

    # Any fly/dry-run must pass the known-answer gate first.
    if not noiseless_gate(coeffs):
        print("REFUSING: noiseless known-answer gate FAILED — circuit/decode is wrong, "
              "no QPU spent."); return 1

    _pubs, meta = build_pubs(coeffs)
    if a.dry_run:
        print("\nDRY-RUN: gate passed, nothing submitted.")
        for m in meta:
            print(f"  {m['term']} c={m['coeff']:+.2f} probe {m['probe']} prep {m['prep']}")
        return 0

    if not a.fly:
        ap.print_help(); return 0

    try:
        from run_exp66_qpu_partb import _get_ibm_service
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2
    except Exception as e:
        print(f"REFUSING: submit deps do not import ({type(e).__name__}: {e})"); return 2

    svc = _get_ibm_service()
    backend = svc.backend(a.backend)
    layout = resolve_layout(a.layout)
    if layout == "PATH":
        layout = _connected_chain(backend, a.layout)
    print(f"\n{backend.name}: operational={backend.status().operational} "
          f"pending={backend.status().pending_jobs} | layout={layout}")

    pubs, meta = build_pubs(coeffs)
    tp = [(transpile(qc, backend, initial_layout=layout, optimization_level=1,
                     seed_transpiler=144), None, KIT.N_SIGN) for qc, _ in pubs]
    outp = os.path.join(RESULTS, "exp144_signcal_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists — would overwrite a record."); return 3
    job = SamplerV2(mode=backend).run(tp)
    out = {"exp": "144-signcal-dummy", "n": N, "terms": TERMS,
           "coeffs": coeffs, "known_signs": sgn, "layout_kind": a.layout, "layout": layout,
           "n_sign": KIT.N_SIGN, "job_id": job.job_id(), "backend": a.backend,
           "cobatched": True, "meta": meta,
           "_note": "DUMMY sign-recovery calibration (chair C4812). PUBLIC, known signs. "
                    "Standalone hardware-capability number (stage-1 support is VOID, so this "
                    "gates nothing downstream). Elder decodes for 2-of-2 vs the 0.90 bar."}
    with open(outp, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\n  SUBMITTED: job {job.job_id()} -> {os.path.basename(outp)}")
    print(f"  known signs (public): {dict(zip(TERMS, sgn))}")
    print(f"  (no QPU figure — measured on landing, C4796 rule)")
    return 0


def _connected_chain(backend, kind):
    """Pick a 4-qubit connected chain, preferring eligible §8 qubits, minimizing CX depth."""
    cmap = backend.coupling_map
    with open(os.path.join(RESULTS, "exp144_layout_gated_ember.json")) as f:
        elig = {q for e in json.load(f)["eligible"] for q in e["pair"]}
    adj = {}
    for e in cmap:
        a, b = (e[0], e[1]) if not hasattr(e, "__getitem__") else (e[0], e[1])
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)

    def walk(path):
        if len(path) == N:
            return list(path)
        for nb in sorted(adj.get(path[-1], ()), key=lambda q: (q not in elig, q)):
            if nb not in path:
                r = walk(path + [nb])
                if r:
                    return r
        return None

    for start in sorted(adj, key=lambda q: (q not in elig, q)):
        r = walk([start])
        if r:
            return r
    return None


if __name__ == "__main__":
    sys.exit(main())
