#!/usr/bin/env python3
"""Exp142 canonical shot-accounting table — owner: Whisper (runbook item 3),
cross-check: Elder. Reads ONLY committed manifests + answer files; no result
payloads touched (blindness-safe, P-independent).

Emits one markdown table per rung: per-wave SUBMITTED conventional shots
(rows x shots from manifests), cumulative CONSUMED (SPRT-walked, from the
answers file at each decode stage), quantum meter/budget, and status.

Usage: python3 exp142_shot_accounting.py [--out table.md]
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")

RUNGS = [4, 6, 8, 10]
B_Q = {4: 60, 6: 80, 8: 90, 10: 110}

# manifest filename per (n, wave) — wave-3+ carry Ember's post-submit rename
def manifest_path(n, wave):
    cands = [f"exp142_wave{wave}_n{n}_manifest.json",
             f"exp142_wave{wave}_n{n}_manifest_ember.json"]
    for c in cands:
        p = os.path.join(RES, c)
        if os.path.exists(p):
            return p
    return None

# answers file per (n, stage): stage 1 = wave1 decode, 2 = wave1+2, 3 = wave1+2+3, ...
def answers_path(n, stage):
    name = f"exp142_wave1_n{n}_answers.json" if stage == 1 else \
           f"exp142_wave1{stage}_n{n}_answers.json"
    p = os.path.join(RES, name)
    return p if os.path.exists(p) else None


def conv_submitted(man):
    tot = 0
    for p in man["pubs"]:
        if p["kind"].startswith("conv_wave") or man.get("wave", 1) >= 2:
            tot += p["rows"] * p["shots"]
    return tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()

    lines = ["# Exp142 canonical shot accounting (conventional arm) — generated, do not hand-edit",
             "",
             "Consumed = SPRT-walked consumed_per_basis_total at each decode stage "
             "(cumulative). Submitted = rows x shots from committed manifests. "
             "Graded denominator per prereg s5 (meeting-fixed): 5 x m99_ideal(n) == B_q(n).",
             ""]
    for n in RUNGS:
        lines.append(f"## n = {n}  (quantum budget B_q = {B_Q[n]})")
        lines.append("")
        lines.append("| wave | conv submitted (this wave) | cumulative submitted | consumed after decode | conv status after decode |")
        lines.append("|------|---------------------------|----------------------|-----------------------|--------------------------|")
        cum = 0
        wave = 1
        while True:
            mp = manifest_path(n, wave)
            if mp is None:
                break
            man = json.load(open(mp))
            sub = conv_submitted(man)
            cum += sub
            a_p = answers_path(n, wave)
            if a_p:
                a = json.load(open(a_p))
                consumed = a["conventional"]["overage_submitted"]
                ident = a["conventional"]["identified"]
                meter = a["conventional"]["meter_median"]
                status = (f"IDENTIFIED, meter_median={meter}" if ident
                          else "open")
                qm = a["quantum"]
            else:
                consumed, status, qm = "—", "(not decoded)", None
            lines.append(f"| {wave} | {sub:,} | {cum:,} | {consumed if isinstance(consumed,str) else format(consumed,',')} | {status} |")
            wave += 1
        if qm:
            lines.append("")
            lines.append(f"Quantum arm: meter {qm['meter']} of budget {qm['shots_budget']} "
                         f"(answered wave 1, unchanged thereafter).")
        lines.append("")
    out = "\n".join(lines)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out + "\n")
        print(f"table -> {args.out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
