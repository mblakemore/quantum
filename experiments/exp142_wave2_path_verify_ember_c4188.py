#!/usr/bin/env python3
"""Exp142 wave-2 SUBMIT-PATH external verify (Ember C4188).

The frozen kit's selftest covers wave-1 builds only; --submit-wave2 has never
flown. Same risk class as Amendment A1 (c4186_001: a test is only as good as
the path it exercises). This script exercises build_job(wave=2) with the REAL
committed alive lists and a DUMMY P (no secrets touched), then pushes the n=4
and n=6 pubs through StatevectorSampler — the same pub-tuple coercion path as
runtime SamplerV2 (selftest-3 method).

Checks per rung:
  S1 structure: pubs are conv chunks only (no sentinel/cal/quantum), shots=12,
     chunk rows sum == len(alive), manifest b_strings count == len(alive),
     chunking at 8192 correct (n=10 -> 8192+2107).
  S2 binding (n=4, n=6 sim): with P_dummy = alive[0], rows for basis==P_dummy
     give all-even parity vs b-string; rows for basis!=P_dummy give mixed
     parity. A positional-binding scramble fails the deterministic check.

Kit is imported read-only; nothing frozen is modified.
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


rng = np.random.default_rng(4188)

for n in (4, 6, 8, 10):
    alive = json.load(open(os.path.join(
        RES, f"exp142_wave1_n{n}_alive.json")))["alive_bases"]
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

    if n in (4, 6):
        from qiskit.primitives import StatevectorSampler
        sv = StatevectorSampler(seed=4188)
        res = sv.run([(c, r, 24) for c, r, _ in pubs]).result()
        # per-row parity stats vs b-strings, real coercion path
        row0 = 0
        det_bad, offdiag_mixed, offdiag_total = 0, 0, 0
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
            row0 += nrows
        check("S2 true-basis rows all-even parity", det_bad == 0,
              f"{det_bad} bad rows")
        check("S2 off-basis rows mixed parity",
              offdiag_mixed >= 0.9 * offdiag_total,
              f"{offdiag_mixed}/{offdiag_total} mixed")

print("WAVE2-PATH VERIFY:", "PASS" if FAIL == 0 else f"FAIL ({FAIL})")
sys.exit(1 if FAIL else 0)
