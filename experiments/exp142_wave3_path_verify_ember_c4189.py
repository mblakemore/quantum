#!/usr/bin/env python3
"""Exp142 wave-3 SUBMIT-PATH external verify (Ember C4189).

--submit-wave2 is now flight-proven (wave-2 flew C4188), but the wave-3 lists
hit two input shapes the C4188 verify never exercised (c4188_001: enumerate
the coverage boundary before first use):
  * SINGLETON alive list (n=4 has exactly 1 base) — classic ndarray-squeeze /
    chunking edge; every prior build used lists of length >= 10.
  * len=2 list (n=6).
Also: with a singleton list the C4188 off-basis mixed-parity check is VACUOUS
(there is no basis != P), so this script adds an OUT-OF-LIST dummy-P build
(S3) whose rows must ALL be mixed-parity — restoring the negative branch.

Same method as exp142_wave2_path_verify_ember_c4188.py: kit imported
read-only, REAL committed wave-3 alive lists (2-of-2 converged, 3rd-verified
Whisper==Elder 4/4 this cycle), DUMMY P only (no secrets touched), sim pushes
pubs through StatevectorSampler pub-tuple coercion (selftest-3 method).

Checks per rung:
  S1 structure: conv chunks only, shots=12, chunk rows sum == len(alive),
     b_strings count == len(alive), chunk count correct.
  S2 binding (n=4,6,8 sim; in-list dummy): basis==P_dummy rows all-even
     parity vs b-string, basis!=P_dummy rows mixed (skipped-as-vacuous when
     len(alive)==1).
  S3 negative (n=4,6 sim; OUT-of-list dummy): zero all-even rows.
"""
import json
import os
import sys
import importlib.util

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "kit", os.path.join(HERE, "exp142_flight_kit.py"))
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)

RES = os.path.join(HERE, "..", "results")
FAIL = 0


def check(label, cond, detail=""):
    global FAIL
    tag = "PASS" if cond else "FAIL"
    if not cond:
        FAIL += 1
    print(f"  [{tag}] {label}{(' — ' + detail) if detail else ''}")


def out_of_list_dummy(alive, n):
    """A syntactically valid Pauli basis string guaranteed not in alive."""
    rot = {"X": "Y", "Y": "Z", "Z": "X"}
    cand = rot[alive[0][0]] + alive[0][1:]
    while cand in alive:
        cand = rot[cand[0]] + cand[1:]
    return cand


def parity_stats(pubs, manifest, alive, P_dummy, n, seed):
    from qiskit.primitives import StatevectorSampler
    sv = StatevectorSampler(seed=seed)
    res = sv.run([(c, r, 24) for c, r, _ in pubs]).result()
    row0 = 0
    det_bad = 0
    alleven_offbasis = 0
    offdiag_mixed, offdiag_total = 0, 0
    for pi, (c, r, _) in enumerate(pubs):
        nrows = manifest["pubs"][pi]["rows"]
        data = res[pi].data
        reg = list(data.keys())[0] if hasattr(data, "keys") else "c"
        bits = getattr(data, reg).get_bitstrings()
        for ri in range(nrows):
            basis = alive[row0 + ri]
            b = np.array([int(ch) for ch in
                          manifest["conv_b_strings"][row0 + ri]])
            odd = 0
            for s in bits[ri * 24:(ri + 1) * 24]:
                v = np.array([int(ch) for ch in
                              s.replace(" ", "")[::-1][:n]])
                odd += int((v.sum() - b.sum()) % 2)
            if basis == P_dummy:
                det_bad += (odd != 0)
            else:
                offdiag_total += 1
                offdiag_mixed += (0 < odd < 24)
                alleven_offbasis += (odd == 0)
        row0 += nrows
    return det_bad, offdiag_mixed, offdiag_total, alleven_offbasis


rng = np.random.default_rng(4189)

for n in (4, 6, 8, 10):
    alive = json.load(open(os.path.join(
        RES, f"exp142_wave3_n{n}_alive_whisper.json")))["alive_bases"]
    P_dummy = alive[0]  # in-list dummy: exercises the deterministic branch
    pubs, manifest = kit.build_job(n, P_dummy, rng, alive_bases=alive, wave=2)

    print(f"n={n}: alive={len(alive)}, pubs={len(pubs)}")
    kinds = [m["kind"] for m in manifest["pubs"]]
    check("S1 conv-only pubs", all(k == "conv_wave2" for k in kinds),
          f"kinds={set(kinds)}")
    check("S1 shots=12 per chunk",
          all(m["shots"] == kit.WAVE1_SHOTS == 12 for m in manifest["pubs"]))
    rows_total = sum(m["rows"] for m in manifest["pubs"])
    check("S1 chunk rows sum == alive", rows_total == len(alive),
          f"{rows_total} vs {len(alive)}")
    check("S1 b_strings count == alive",
          len(manifest["conv_b_strings"]) == len(alive))
    exp_chunks = (len(alive) + kit.CONV_CHUNK_ROWS - 1) // kit.CONV_CHUNK_ROWS
    check("S1 chunk count", len(pubs) == exp_chunks,
          f"{len(pubs)} vs {exp_chunks}")
    check("S1 named_rows dict binding",
          all(isinstance(p[1], dict) for p in pubs))

    if n in (4, 6, 8):
        det_bad, mixed, total, alleven_off = parity_stats(
            pubs, manifest, alive, P_dummy, n, seed=4189)
        check("S2 true-basis rows all-even parity", det_bad == 0,
              f"{det_bad} bad rows")
        if total == 0:
            print("  [SKIP] S2 off-basis mixed — VACUOUS (singleton list); "
                  "covered by S3 below")
        else:
            check("S2 off-basis rows mixed parity",
                  mixed >= 0.9 * total, f"{mixed}/{total} mixed")

    if n in (4, 6):
        P_out = out_of_list_dummy(alive, n)
        pubs3, man3 = kit.build_job(n, P_out, rng,
                                    alive_bases=alive, wave=2)
        det_bad3, _, total3, alleven3 = parity_stats(
            pubs3, man3, alive, P_out, n, seed=4189)
        check("S3 out-of-list P: zero all-even rows",
              alleven3 == 0 and total3 == len(alive),
              f"{alleven3} all-even of {total3}")

print("WAVE3-PATH VERIFY:", "PASS" if FAIL == 0 else f"FAIL ({FAIL})")
sys.exit(1 if FAIL else 0)
