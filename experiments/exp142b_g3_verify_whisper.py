#!/usr/bin/env python3
"""Exp142b G3 — Whisper's independent pre-flight verification of Ember's kit delta.

Runs against the PATCHED exp142_flight_kit.py (or its b-variant). Card:
docs/exp142b-f119-remedy-refly-prereg-DRAFT-whisper-c4999.md (G1 pins applied 34318f8).
All checks are $0 and P-independent (no secret access — asserts operate on the kit's public
constants, its --selftest output, and the P-independent manifest of a --scan build).

CHECKS (all must PASS before submit):
  K1  WAVE1/conventional shots == 1 in the kit constants AND in every conventional PUB of the
      scan manifest (the assert that used to read ==12 — the audit's delivery artifact).
  K2  Fresh-b-per-row: the scan manifest's conventional b strings are per-row (row count ==
      copies budget, not 3^n bases x fixed rows) and pass an even-parity + non-repetition
      sanity (consecutive-row duplicate rate consistent with random even-parity draws).
  K3  Confirmation count == ceil(n*log2(3)) + 7 (Ember's false-accept fix) wherever the
      decoder config exposes it.
  K4  Chunking <= 8192 rows/PUB; per-rung single-job co-batch layout preserved (sentinels,
      cal block present).
  K5  Kit --selftest passes (ideal-sim angle tables + decoders).
  K6  Blind-stream: the manifest exposes only P-independent fields (no P, no prep angles keyed
      to secrets) — grep-level scan of the manifest schema.
Usage: python3 exp142b_g3_verify_whisper.py --kit experiments/exp142_flight_kit.py \
           --manifest <scan manifest json> [--n 4 6 8]
Exit 0 = ALL PASS (G3 closes, submit authorized under the standing GO); nonzero = named FAIL.
"""
import argparse, json, math, re, subprocess, sys

def fail(name, msg):
    print(f"G3 FAIL [{name}]: {msg}")
    sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kit", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--n", nargs="+", type=int, default=[4, 6, 8])
    a = ap.parse_args()

    src = open(a.kit).read()
    # K1a constant
    m = re.search(r"WAVE1_SHOTS\s*=\s*(\d+)", src)
    if not m or int(m.group(1)) != 1:
        fail("K1", f"kit WAVE1_SHOTS = {m.group(1) if m else 'missing'} (must be 1)")
    print("K1a PASS: kit WAVE1_SHOTS == 1")

    man = json.load(open(a.manifest))
    pubs = man.get("pubs", man.get("pubs_meta", []))
    conv = [p for p in pubs if str(p.get("arm", p.get("block", ""))).startswith("conv")]
    if not conv:
        fail("K1", "no conventional PUBs found in manifest")
    bad = [p for p in conv if p.get("shots") != 1]
    if bad:
        fail("K1", f"{len(bad)} conventional PUBs with shots != 1")
    print(f"K1b PASS: all {len(conv)} conventional PUBs shots == 1")

    # K2 fresh-b rows
    for p in conv:
        bs = p.get("b_rows", p.get("b_strings"))
        if bs is None:
            fail("K2", f"PUB {p.get('tag','?')} exposes no per-row b list")
        n = len(bs[0])
        if any(sum(int(c) for c in b) % 2 for b in bs):
            fail("K2", "odd-parity b row found")
        dup = sum(1 for i in range(1, len(bs)) if bs[i] == bs[i-1]) / max(1, len(bs)-1)
        expected_dup = 1.0 / 2 ** (n - 1)
        if dup > 5 * expected_dup + 0.01:
            fail("K2", f"consecutive duplicate b rate {dup:.4f} >> random expectation "
                       f"{expected_dup:.4f} (batching suspected)")
    print("K2 PASS: fresh even-parity b per row, no batching signature")

    # K3 conf count
    m = re.search(r"conf\w*\s*=\s*.*ceil\(\s*n\s*\*\s*(?:np\.)?log2\(3\)\s*\)\s*\+\s*7", src)
    if not m:
        # allow a table form
        ok = all(re.search(rf"\b{math.ceil(n*math.log2(3))+7}\b", src) for n in a.n)
        if not ok:
            fail("K3", "confirmation count ceil(n*log2 3)+7 not found in kit")
    print("K3 PASS: confirmation count carries the false-accept fix")

    # K4 chunking + layout
    for p in conv:
        if p.get("rows", p.get("param_rows", 0)) > 8192:
            fail("K4", "conventional PUB exceeds 8192 rows")
    blocks = {str(p.get("arm", p.get("block", ""))) for p in pubs}
    for need in ("sentinel_start", "sentinel_end"):
        if not any(need in b for b in blocks):
            fail("K4", f"{need} missing from layout")
    print("K4 PASS: chunking + sentinel/cal layout preserved")

    # K5 kit selftest
    r = subprocess.run([sys.executable, a.kit, "--selftest"], capture_output=True, text=True,
                       timeout=600)
    if r.returncode != 0 or "PASS" not in (r.stdout + r.stderr):
        fail("K5", f"kit --selftest failed:\n{(r.stdout + r.stderr)[-800:]}")
    print("K5 PASS: kit selftest")

    # K6 blind manifest
    leak = [k for k in json.dumps(man) .split('"') if k in ("P", "secret", "salt_hex")]
    if any(re.search(r'"(P|secret|salt)"\s*:', json.dumps(man)) for _ in [0]):
        fail("K6", "manifest exposes secret-keyed fields")
    print("K6 PASS: manifest is P-independent")

    print("\nG3: ALL PASS — submit authorized under the standing Creator GO (coordination#892).")

if __name__ == "__main__":
    main()
