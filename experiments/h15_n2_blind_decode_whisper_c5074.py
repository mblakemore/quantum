#!/usr/bin/env python3
"""H15 N2 — WHISPER'S BLIND DECODER, FROZEN PRE-FLIGHT (C5074).

The decode seat's mirror of Elder's frozen grader (quantum@6094497): nothing
invented at decode time, written FROM SCRATCH against the PUBLIC contract only
(kit manifest + bus record) — deliberately without reading Elder's harness,
so the two seats stay independent.

CONTRACT (all public, all pre-flight):
  - Row schedule: cal j at floor((j+0.5)*696/64); 632 graded rows fill the
    rest in sealed order (kit manifest, quantum@eec1941).
  - Cal design: rows j=32..47 are known-ALT arm=never; j=48..63 known-ALT
    arm=always (kit cal_rows() order: 16 auto-ALT, 16 auto-NULL, 16 never,
    16 always).
  - THE CAL CONTRACT PINS THE PARSE: under the correct actuator read,
    never-rows -> 0 and always-rows -> 1, deterministically. The decoder
    tries each candidate parse and REFUSES (fail-closed, no output file)
    unless exactly one parse satisfies the contract on ALL 32 arm rows.
  - Response = actuator bit per graded row, in GRADED (sealed) order.
  - Output: decisions JSON + its sha256, to be posted BEFORE any unseal.

This decoder never sees labels, never sees the commitment preimage, and reads
nothing but the raw per-row measurement records.

Input format (--bank <path>): JSON with either
  {"rows": ["<mem-string>", ...]}     one qiskit memory string per row, flight order
or
  {"rows": [{"mem": "<mem-string>"}, ...]}
Memory string = qiskit registers space-separated, MSB-left per register.
$0. No submission path. No account import.
"""
import argparse
import hashlib
import json
import sys

TOTAL, M, C = 696, 632, 64


def cal_positions():
    return sorted(set(int((j + 0.5) * TOTAL / C) for j in range(C)))


def parse_candidates(mem):
    """Candidate reads of the actuator bit from a memory string.
    Kit register order (creation): bell(8), dec(1), act(1) -> qiskit prints
    reversed: 'act dec bell'. Candidates cover both end-registers, both bit
    orders, so the cal contract - not an assumption - picks the parse."""
    parts = mem.split()
    cands = {}
    if len(parts) >= 2:
        cands["first_field"] = parts[0]
        cands["last_field"] = parts[-1][0]
        cands["last_field_lsb"] = parts[-1][-1]
    flat = mem.replace(" ", "")
    cands["flat_first"] = flat[0]
    cands["flat_last"] = flat[-1]
    return {k: v for k, v in cands.items() if v in "01"}


def decode(bank_rows):
    assert len(bank_rows) == TOTAL, f"bank has {len(bank_rows)} rows, need {TOTAL}"
    mems = [r["mem"] if isinstance(r, dict) else r for r in bank_rows]
    cpos = cal_positions()
    never_pos = [cpos[j] for j in range(32, 48)]
    always_pos = [cpos[j] for j in range(48, 64)]
    # cal-contract parse selection, fail-closed
    winners = []
    for name in parse_candidates(mems[0]):
        ok = all(parse_candidates(mems[p]).get(name) == "0" for p in never_pos) \
            and all(parse_candidates(mems[p]).get(name) == "1" for p in always_pos)
        if ok:
            winners.append(name)
    if not winners:
        sys.exit("REFUSE (fail-closed): no parse satisfies the cal contract. "
                 "No output written.")
    # winners that agree on EVERY row are aliases of one parse-class; genuine
    # divergence anywhere = ambiguity = refuse.
    seqs = {name: tuple(parse_candidates(m).get(name) for m in mems)
            for name in winners}
    if len(set(seqs.values())) != 1:
        sys.exit(f"REFUSE (fail-closed): {len(winners)} contract-satisfying "
                 f"parses DIVERGE on the bank ({winners}) — need one class. "
                 "No output written.")
    parse = winners[0]
    cset = set(cpos)
    graded = [int(parse_candidates(mems[p])[parse])
              for p in range(TOTAL) if p not in cset]
    assert len(graded) == M
    return parse, graded


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True)
    ap.add_argument("--out", default="/droid/repos/quantum/results/"
                    "h15_n2_whisper_blind_decode.json")
    ap.add_argument("--selftest", action="store_true",
                    help="run on a simulated fake flight instead of a bank")
    a = ap.parse_args()
    if a.selftest:
        sys.path.insert(0, "/droid/repos/quantum/experiments")
        from h15_n2_public_kit_whisper_c5074 import build_flight, fake_secrets
        from h15_n1_synapse_incircuit_whisper_c5074 import SIM
        secrets = fake_secrets()
        circs, rowmap = build_flight(secrets)
        res = SIM.run(circs, shots=1, memory=True).result()
        bank_rows = [res.get_memory(i)[0] for i in range(TOTAL)]
        parse, graded = decode(bank_rows)
        truth = [1 if r["label"] == "ALT" else 0 for r in secrets]
        acc = sum(int(g == t) for g, t in zip(graded, truth)) / M
        print(f"SELFTEST: parse={parse} graded_n={len(graded)} "
              f"fake-truth accuracy={acc:.4f} (expect ~0.73)")
        sys.exit(0)
    bank = json.load(open(a.bank))
    parse, graded = decode(bank["rows"])
    payload = {"card": "h15_n2_whisper_blind_decode", "cycle": "C5074",
               "parse_selected_by_cal_contract": parse,
               "graded_responses_sealed_order": graded,
               "n_graded": len(graded),
               "mean_response": sum(graded) / len(graded)}
    blob = json.dumps(payload, sort_keys=True).encode()
    payload["decisions_sha256"] = hashlib.sha256(blob).hexdigest()
    json.dump(payload, open(a.out, "w"), indent=1)
    print(f"DECISIONS HASH (post PRE-UNSEAL): {payload['decisions_sha256']}")
    print(f"wrote {a.out}")
