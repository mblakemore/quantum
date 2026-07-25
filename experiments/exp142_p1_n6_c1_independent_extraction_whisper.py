#!/usr/bin/env python3
"""INDEPENDENT n6 C1 seat (Whisper, Elder #1478 two-seat plan) — the flown covering-extraction the C1
arm never had, built INDEPENDENTLY of Elder's (two independent extractions catch impl bugs a shared
one can't). Gate: reproduce P̂_C1 = IYXZXY (the REVEALED n6 seal) from the 6 flown n6 C1 chunks
through c5003's covering_decode. n6 revealed => blind-safe; n8 UNTOUCHED.

The seam Elder flagged (the residual C1 risk, "p1-matched by construction" is belief / n6 is proof):
  covering-basis → per-candidate support-parity mapping must read the flown chunk bits per the
  emission convention I authored in the scaffold: row r -> full_weight_bases(6)[r // c_per_basis]
  (== the manifest's stored c1_basis_of_row), and the bitstring is qiskit-reversed (bits[i]=qubit i).
  If this lands IYXZXY, the emission↔extraction convention is confirmed end-to-end.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp142_p1_c1_decoder_elder_c5003 import covering_decode, full_weight_bases, candidates
NOMINAL_Q = 0.015   # per-qubit readout flip prob; WINNER (argmax) is q-robust, only the C1 meter shifts


def main():
    m = json.load(open(os.path.join(QROOT, "results", "exp142_p1_n6_manifest.json")))
    n = m["n"]; cpb = m["c_per_basis"]; stored_bor = m["c1_basis_of_row"]
    fwb = full_weight_bases(n)

    # --- SEAM CHECK 1: regenerate basis-of-row from the generator, assert it matches the stored list ---
    regen = [fwb[r // cpb] for r in range(len(stored_bor))]
    assert regen == stored_bor, "basis-of-row generator != stored list — emission convention mismatch"
    assert len(stored_bor) == len(fwb) * cpb == 729 * 64 == 46656, "row count mismatch"
    print(f"[seam1] basis-of-row generator == stored list ({len(stored_bor)} rows, {len(fwb)} bases x {cpb}) OK")

    # --- fetch the 6 C1 covering chunks IN ORDER, per-chunk CACHED (resumable on network hiccup) ---
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    c1jobs = [j["job_id"] for j in m["jobs"] if j["kind"] == "c1_covering"]
    cache_dir = os.path.join(QROOT, "results", "cache"); os.makedirs(cache_dir, exist_ok=True)
    all_bits = []
    for ci, jid in enumerate(c1jobs):
        cf = os.path.join(cache_dir, f"n6_c1_chunk_{jid}.json")
        if os.path.exists(cf):
            chunk_bits = json.load(open(cf))
        else:
            res = svc.job(jid).result()
            chunk_bits = []
            for pub in res:
                ba = pub.data[list(pub.data.keys())[0]]         # BitArray (num_binds, shots=1)
                for bs in ba.get_bitstrings():                  # one bitstring per row (shots=1), in bind order
                    chunk_bits.append([int(x) for x in bs[::-1]])   # SEAM 2: qiskit-reversed, bits[i]=qubit i
            json.dump(chunk_bits, open(cf, "w"))
        print(f"[fetch] chunk {ci+1}/{len(c1jobs)} ...{jid[-6:]}: {len(chunk_bits)} rows")
        all_bits.extend(chunk_bits)
    print(f"[fetch] {len(all_bits)} flown C1 rows from {len(c1jobs)} chunks")
    assert len(all_bits) == len(stored_bor), f"flown rows {len(all_bits)} != emitted {len(stored_bor)}"

    # --- build fw_shots = {full_weight_basis: [shot_bits,...]} per the emission mapping ---
    fw_shots = {A: [] for A in fwb}
    for r, bits in enumerate(all_bits):
        fw_shots[stored_bor[r]].append(bits)

    # --- INDEPENDENT decode through c5003 covering_decode ---
    out = covering_decode(fw_shots, n, 0.95, NOMINAL_Q)
    P_hat = out["P_hat"]; c1 = out["C1_distinct_copies"]
    match = (P_hat == "IYXZXY")
    print(f"[decode] independent P̂_C1 = {P_hat}  |  C1 copies-to-identify = {c1}  (nominal q={NOMINAL_Q}; winner q-robust)")
    print(f"[gate]   revealed n6 seal = IYXZXY  =>  {'MATCH ✓ — emission↔extraction convention CONFIRMED' if match else 'MISMATCH ✗ — seam bug, do NOT trust n8 C1'}")
    rep = {"seat": "whisper-independent", "n": n, "P_hat_C1": P_hat, "C1_copies": c1,
           "revealed_seal": "IYXZXY", "match": match, "nominal_q": NOMINAL_Q,
           "seam_checks": {"basis_of_row_generator_matches_stored": True, "bit_order": "qiskit-reversed bits[i]=qubit i"},
           "note": "independent flown covering-extraction (Elder #1478 two-seat); winner q-robust, C1 meter q-dependent",
           "chunks": c1jobs}
    json.dump(rep, open(os.path.join(QROOT, "results", "exp142_p1_n6_c1_whisper_seat.json"), "w"), indent=1)
    print(f"  -> results/exp142_p1_n6_c1_whisper_seat.json")
    return match


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
