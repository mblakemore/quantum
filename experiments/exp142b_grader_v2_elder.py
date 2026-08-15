#!/usr/bin/env python3
"""Exp142b GRADER v2 (Elder C6620, grader seat) — the re-freeze meter, run pre-reveal.

The v1 freeze (exp142_grader.py, Whisper C4746) prohibits silent edits to itself; this v2 file
sits BESIDE it carrying the re-freeze rulings, all pinned pre-flight in the court record:
  - SPRT decoder, 3/3-confirmed (Ember #919, Whisper #920, Elder #921): LLR += ln(p0/.5) on
    parity-pass / ln((1-p0)/.5) on fail; ACCEPT at A = n*ln3 + ln100; ELIMINATE at B = ln(0.005),
    eliminated candidates frozen out. p0 = MEASURED cal-block parity-pass rate (never assumed).
  - BILLING (prereg "pinned now so grade time cannot re-litigate it"): decoder replays the
    committed schedule in order; bill per rep = TOTAL rows replayed up to SPRT-accept. Rows flown
    beyond the stop are apparatus. Meter statistic = MEDIAN over the M=20 reps (mean+IQR reported).
  - CENSORING: a rep with no accept within its 2187 committed rows is REPORTED, not dropped;
    >1/20 flags the sizing (Elder proviso).
  - Q ARM (Elder pin 2): billed as measured two-copy count to identification via the FROZEN
    v1 decoder (exp142_decode_meter.quantum_decode: Gate-2 ML + stable-prefix meter — the
    smallest m after which the winner never changes). Ratio (G1 pin 2) =
    median(conv executed) / median(Q executed), realized counts of BOTH arms,
    best-known-CONDITIONAL label. (Copies-currency variant ratio/2 reported in a note, never
    the headline — the prereg convention wins; the variant is stated so no reader is surprised.)
  - Bit-order and Bell (x,z)-role conventions are pinned EMPIRICALLY against the cal block /
    rep-0 consistency and printed — never assumed silently (the Z-vs-S method).

Usage: python3 exp142b_grader_v2_elder.py            # meter, pre-reveal
       python3 exp142b_grader_v2_elder.py --reveal   # + commitment verify + P grade (post-seal)
"""
import glob, hashlib, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
N = 4
CANDS = ["".join(p) for p in __import__("itertools").product("XYZ", repeat=N)]  # 81, index order fixed
A_ACC = N * math.log(3) + math.log(100)
B_ELIM = math.log(0.005)
BELL_MAP = {(0, 0): "I", (1, 0): "X", (1, 1): "Y", (0, 1): "Z"}

def load():
    man = json.load(open(os.path.join(RES, "exp142b_n4_manifest.json")))
    sch = json.load(open(os.path.join(RES, "exp142b_n4_schedule.json")))
    pubs = [None] * len(man["pubs"])
    for j in man["jobs"]:
        raw = json.load(open(os.path.join(RES, f"exp142b_n4_raw_{j['job_id']}.json")))
        for k, p in enumerate(raw["pubs"]):
            pubs[j["pub_lo"] + k] = p["c"]
    assert all(p is not None for p in pubs), "pub coverage gap"
    return man, sch, pubs

def parity_pass(bits_str, b_str, reverse):
    z = [int(c) for c in (bits_str[::-1] if reverse else bits_str)]
    return (sum(z) - sum(int(c) for c in b_str)) % 2 == 0

def measure_p0(man, pubs):
    """Cal block -> measured p0, and the bit-order convention pinned by the data."""
    out = {}
    for reverse in (True, False):
        npass = ntot = 0
        for i, p in enumerate(man["pubs"]):
            if p["kind"] != "cal": continue
            for row in pubs[i]:
                npass += parity_pass(row, p["b"], reverse); ntot += 1
        out[reverse] = (npass / ntot, ntot)
    best = max(out, key=lambda k: abs(out[k][0] - 0.5))
    p0, ntot = out[best]
    print(f"cal block: p0={p0:.4f} (n={ntot}) with reverse={best}; other convention gave {out[not best][0]:.4f}")
    assert abs(p0 - 0.5) > 0.2, "cal parity ~chance under BOTH bit orders — convention unresolved, REFUSE"
    if p0 < 0.5:  # sign convention inverted — refuse rather than flip silently
        raise SystemExit("cal parity-pass < 0.5 — b-convention inverted; refusing to guess")
    return p0, best

def conv_meter(man, sch, pubs, p0, reverse):
    """Pinned SPRT replay per rep. Returns per-rep dicts."""
    lw, lf = math.log(p0 / 0.5), math.log((1 - p0) / 0.5)
    reps = []
    for gi, p in enumerate(man["pubs"]):
        if p["kind"] != "conv_v2": continue
        rows = pubs[gi]; plan = sch["pubs"][gi]
        assert len(rows) == len(plan) == 2187
        llr = {c: 0.0 for c in CANDS}; alive = set(CANDS)
        accepted = None; bill = None
        for r, (out_bits, meta) in enumerate(zip(rows, plan), start=1):
            Abasis = meta["A"]
            if Abasis not in alive: continue
            ok = parity_pass(out_bits, meta["b"], reverse)
            llr[Abasis] += lw if ok else lf
            if llr[Abasis] >= A_ACC: accepted, bill = Abasis, r; break
            if llr[Abasis] <= B_ELIM: alive.discard(Abasis)
        reps.append({"rep": p["rep"], "P_hat": accepted, "bill_rows": bill,
                     "censored": accepted is None,
                     "alive_at_end": len(alive) if accepted is None else None})
    return reps

def q_meter(man, pubs):
    """Q arm via the FROZEN decoder (one code path, zero reimplementation):
    exp142_decode_meter.quantum_decode — Gate-2 ML decoder + stable-prefix meter, the frozen
    'measured two-copy count to identification' (Elder pin 2). My first TWO attempts at a fresh
    implementation were wrong physics (per-qubit marginals are uniform under the fresh-even-
    parity-sign protocol; identification lives in the parity constraint the frozen decoder
    encodes) — kept in git as the record of why the frozen path is called, not rewritten."""
    from exp142_decode_meter import quantum_decode
    out = []
    for gi, p in enumerate(man["pubs"]):
        if p["kind"] != "quantum": continue
        d = quantum_decode(pubs[gi], N)
        out.append({"rep": p["rep"], "P_hat": d["P_hat"], "bill_samples": d["meter"],
                    "shots_flown": d["shots_budget"]})
    return out

def verify_commitment():
    r = json.load(open(os.path.join(RES, "exp142b_n4_REVEAL_ember.json")))
    c = json.load(open(os.path.join(HERE, "..", r["commitment_file"])))
    pre = bytes.fromhex(r["salt_hex"]) + f"exp142|{r['ensemble']}|{r['n']}|{r['P']}".encode()
    digest = hashlib.sha256(pre).hexdigest()
    ok = (digest == c["hash_sha256"]) and (c.get("ensemble") == r["ensemble"]) and (int(c["n"]) == int(r["n"]))
    return ok, r["P"]

def main():
    man, sch, pubs = load()
    p0, reverse = measure_p0(man, pubs)
    conv = conv_meter(man, sch, pubs, p0, reverse)
    q = q_meter(man, pubs)
    cbills = [r["bill_rows"] for r in conv if not r["censored"]]
    qbills = [r["bill_samples"] for r in q if r["bill_samples"]]
    cens = sum(r["censored"] for r in conv)
    conv_med = float(np.median(cbills)); q_med = float(np.median(qbills))
    ratio = conv_med / q_med
    consensus = {r["P_hat"] for r in conv if r["P_hat"]} | {r["P_hat"] for r in q if r["P_hat"]}
    print(f"CONV: {len(cbills)}/20 accepted, censored {cens} ({'FLAG >1/20' if cens > 1 else 'within 1/20'}), "
          f"median bill {conv_med:.0f} rows (mean {np.mean(cbills):.0f}, IQR {np.percentile(cbills,25):.0f}-{np.percentile(cbills,75):.0f})")
    print(f"CONV P_hat set: { {r['P_hat'] for r in conv if r['P_hat']} }")
    print(f"Q: median bill {q_med:.0f} two-copy samples (mean {np.mean(qbills):.2f}), "
          f"P_hat set: { {r['P_hat'] for r in q if r['P_hat']} }")
    print(f"REALIZED RATIO (pinned, both executed arms): {conv_med:.0f}/{q_med:.0f} = {ratio:.0f}x "
          f"(copies-currency variant {ratio/2:.0f}x — note, never headline)")
    art = {"card": "exp142b_n4_grader_v2_elder", "cycle": "C6620", "p0_measured": p0,
           "bit_reverse": reverse, "A": A_ACC, "B": B_ELIM,
           "conv": conv, "q": q, "conv_median": conv_med, "q_median": q_med,
           "censored": int(cens), "ratio_realized": ratio,
           "consensus_P": sorted(consensus)}
    if "--reveal" in sys.argv:
        ok, P = verify_commitment()
        art["reveal"] = {"commitment_ok": bool(ok), "P": P,
                         "conv_correct": all(r["P_hat"] == P for r in conv if r["P_hat"]),
                         "q_correct": all(r["P_hat"] == P for r in q if r["P_hat"])}
        print(f"REVEAL: commitment {'VERIFIED' if ok else 'FAILED'}; true P = {P}; "
              f"conv all-correct={art['reveal']['conv_correct']}, q all-correct={art['reveal']['q_correct']}")
    out = os.path.join(RES, "exp142b_n4_grader_v2_elder.json")
    json.dump(art, open(out, "w"), indent=1)
    print(f"-> {out}")

if __name__ == "__main__":
    main()
