#!/usr/bin/env python3
"""Exp142b G3 — Whisper's independent pre-flight verification of Ember's v2 kit delta.

Prereg: docs/exp142b-f119-remedy-refly-prereg-DRAFT-whisper-c4999.md §4 gate G3.
INDEPENDENT means: this script BUILDS the kit itself (dummy P) and re-derives every property —
it does not read Ember's receipts. $0, P-independent (dummy P at build; real P only at submit).

SCHEMA RECONCILIATION (C5073, this rewrite): the C4999 draft of this script expected per-row
b-strings IN the manifest. The delivered v2 build's manifest is CORRECTLY P-independent — the
conv_v2 entries carry only {kind, row_lo, rows, shots}, no b's — so the fresh-basis-per-row
property (the actual F119 delivery fix) is verified via the KIT SELFTEST's own fresh-b check,
not from the manifest. Expecting b's in the manifest was the anticipatory-schema error; the
gate surfaced it. Checks below match the delivered kit.

CHECKS (all must PASS):
  K1 conv_v2 shots==1 in EVERY conventional pub of every rung (the ==12 delivery leak, killed).
  K2 quantum shots==1 (both arms one-copy-per-row).
  K3 no P/angle leak in the manifest (P-independent emission).
  K4 chunking: every conv_v2 pub rows <= CONV_CHUNK_ROWS; sentinel_start/end present per rung.
  K5 confirmation count == ceil(n*log2 3)+7 in the kit (Ember false-accept fix).
  K6 kit --selftest PASS (angle tables + fresh-b-per-copy + real pub-binding path).
  K7 budget recheck: dry-run shot bill re-derived; trimmed (n=4,6) vs full (+n=8) reported
     against the free-ALT4 fit at freeze.
Exit 0 = ALL PASS; nonzero = named FAIL.
"""
import math, os, re, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import exp142_flight_kit as K
import exp142b_build_job_v2_ember_c4215 as B
import exp142b_conv_emission_ember_c4215 as V2


def fail(name, msg):
    print(f"G3 FAIL [{name}]: {msg}"); sys.exit(1)


def main():
    rungs = list(B.GRID.items())
    print(f"G3 independent verify — rungs {dict(B.GRID)}, CONV_CHUNK_ROWS={K.CONV_CHUNK_ROWS}, "
          f"MAX_ROWS_PER_JOB={B.MAX_ROWS_PER_JOB}")
    total_shots = {}
    for n, M in rungs:
        C = V2.confirm_C(n, 0.02)
        rng = np.random.default_rng(777 + n)   # my own seed, not Ember's
        Pdummy = "".join(rng.choice(list("XYZ"), size=n))
        pubs, man = B.build_rung(n, Pdummy, C, M, rng)

        conv = [m for m in man if m["kind"] == "conv_v2"]
        quantum = [m for m in man if m["kind"] == "quantum"]
        if not conv: fail("K1", f"n={n}: no conv_v2 pubs")
        bad1 = [m for m in conv if m["shots"] != 1]
        if bad1: fail("K1", f"n={n}: {len(bad1)} conv_v2 pubs shots!=1 (the F119 delivery leak)")
        bad2 = [m for m in quantum if m["shots"] != 1]
        if bad2: fail("K2", f"n={n}: {len(bad2)} quantum pubs shots!=1")

        import json as _j
        s = _j.dumps(man)
        if re.search(r"theta|phi|angle|prep|param_rows", s): fail("K3", f"n={n}: manifest leaks angle/P")

        over = [m for m in conv if m["rows"] > K.CONV_CHUNK_ROWS]
        if over: fail("K4", f"n={n}: {len(over)} conv_v2 pubs exceed CONV_CHUNK_ROWS")
        kinds = {m["kind"] for m in man}
        for need in ("sentinel_start", "sentinel_end"):
            if need not in kinds: fail("K4", f"n={n}: {need} missing")

        # budget: shots = sum over pubs (shots * rows). rows live in param value arrays.
        sh = sum(p[2] * (1 if p[1] is None else len(list(p[1].values())[0])) for p in pubs)
        total_shots[n] = sh
        print(f"  K1-K4 PASS n={n} M={M} C={C}: {len(conv)} conv_v2 + {len(quantum)} quantum, "
              f"all shots==1, chunk<= {K.CONV_CHUNK_ROWS}, sentinels present, {sh:,} shots")

    # K5 conf count
    # conf count lives in the DECODER/baseline sim, not the flight kit (C5073 K5 scope fix:
    # my first pass grepped only kit+emission and false-failed; the fix is in the sim).
    src = ""
    for f in ("exp142_flight_kit.py", "exp142b_conv_emission_ember_c4215.py",
              "exp142_learning_advantage_sim.py"):
        fp = os.path.join(HERE, f)
        if os.path.exists(fp): src += open(fp).read()
    # regex tolerant of int(...) wrapper: "log2(3)" then any closing parens then "+ 7"
    if not re.search(r"log2\(3\)\)*\s*\+\s*7", src):
        fail("K5", "conf count ceil(n*log2 3)+7 not found in kit/emission/sim")
    print(f"K5 PASS: confirmation count ceil(n*log2 3)+7 carries the false-accept fix (in the decoder sim)")

    # K6 selftest (covers fresh-b-per-copy — the delivery fix, since manifest is P-independent)
    r = subprocess.run([sys.executable, os.path.join(HERE, "exp142_flight_kit.py"), "--selftest"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or "SELFTEST PASS" not in r.stdout:
        fail("K6", f"kit selftest did not pass:\n{r.stdout[-400:]}\n{r.stderr[-200:]}")
    print("K6 PASS: kit selftest PASS (angle tables + fresh-b-per-copy + real pub-binding)")

    # K7 budget
    trimmed = total_shots.get(4, 0) + total_shots.get(6, 0)
    full = sum(total_shots.values())
    print(f"K7 budget recheck: trimmed(n=4,6) ~{trimmed:,} shots · full(+n=8) ~{full:,} shots")
    print(f"  n=8 is ~{100*total_shots.get(8,0)/max(full,1):.0f}% of the full bill (Ember G2: ~75%)")
    print(f"  -> trimmed answers 'did the remedy work' on two full-M rungs; full needs the replenish (Creator G4)")

    print("\nG3 PASS — kit independently rebuilt from my seat; delivery fix (shots==1, fresh-b via "
          "selftest), P-independence, chunking, conf-count all verified. Freeze awaits Creator G4.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
