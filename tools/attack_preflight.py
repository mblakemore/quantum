#!/usr/bin/env python3
"""THE PROBLEM-SPECIFIC ATTACK SIDE — a pre-flight that fires our own known attacks at a claim.

WHY THIS EXISTS. The stabilizer-rank solver measures how long a classical computer needs to
SIMULATE the circuit. That is a CEILING on the classical cost, not an advantage — my own C4996
red-team put a ~7,000x gap between that ceiling and a problem-specific attack (the planted MM
problem falls to a 41-query linear-structure solve in ~0.25 ms against an 1,818 s simulation floor;
F121 retired, 3/3 court seats). So the solver alone cannot license an advantage claim. This is the
other side.

WHAT THE already-built CHECK FOUND, and it is the reason this is a harness and not a new attack:
FOUR red-team artifacts already exist across three DCs, each written for ONE experiment —

    exp_hss_redteam_whitebox_attack.py        Whisper C4996   F121  -> RETIRED
    exp142_f119_redteam_audit_ember_c4215.py  Ember   C4215   F119  -> SUPERSEDED as-executed
    exp142_f119_delivery_attack_ember_c4215.py     "      "      "
    exp144_baseline_redteam_mc_elder_c6510.py Elder   C6510   SS4   -> SURVIVED

Three attack CLASSES, discovered independently, four firings in one week, three claims killed or
qualified and one survival. Nothing collected them, so each new claim re-derives the questions or
misses them. The gap is not another attack — it is that the attacks are not a checklist.

WHAT THIS IS NOT, stated first because the failure mode is believing otherwise: IT CANNOT FIND
NOVEL ATTACKS. It fires the classes that have already broken our claims. A claim that passes has
survived our known attacks and nothing more — the C4996 attack itself was novel when it fired, and
no checklist would have contained it beforehand. Passing is a floor, not a certificate.

DESIGN NOTE: "unknown" blocks exactly as "yes" does. A claim cannot pass by not having looked.

Usage:
    python3 tools/attack_preflight.py --list
    python3 tools/attack_preflight.py --claim myclaim.json
    python3 tools/attack_preflight.py --interactive-template > myclaim.json
"""
import argparse
import json
import sys

# ─────────────────────────────────────────────────────────────────────────────
# THE REGISTRY. Each entry is a class that has actually fired at one of our claims.
# Adding a class = adding an entry. Preconditions are questions about the CLAIM, and
# any answer of "yes" or "unknown" makes the class APPLY.
# ─────────────────────────────────────────────────────────────────────────────
ATTACKS = [
    {
        "id": "planted-structure-leak",
        "combinator": "all",   # the attack needs BOTH a public structure AND a simulation-priced baseline. A public instance alone is fine — F113's 2D-HLF instance is public by construction and makes no runtime claim.
        "name": "Attack the problem's algebra, not the circuit",
        "exploits": (
            "A planted/hidden secret compiled INTO the circuit whose defining algebraic property "
            "leaks it under direct classical query. The MM property — f(x,.) is a linear character "
            "in y with slope x — leaks the shift's x-half from k queries and the y-half from k more."
        ),
        "precondition": [
            ("structure_public", "Is the planted structure (the generator, g, the bent function) "
                                 "PUBLIC or derivable from the published circuit?"),
            ("baseline_is_simulation", "Is the classical baseline priced as cost-to-SIMULATE the "
                                       "circuit rather than cost-to-SOLVE the problem?"),
        ],
        "must_answer": (
            "What is the best classical algorithm for the PROBLEM, given everything the paper "
            "publishes? Run it. Report its wall-clock against the quantum arm."
        ),
        "history": "Whisper C4996 — F121 RETIRED. 41 queries, ~0.25 ms vs an 1,818 s simulation "
                   "floor. ~7,000x. Confirmed 3/3 court seats.",
        "artifact": "experiments/exp_hss_redteam_whitebox_attack.py",
    },
    {
        "id": "idealized-hard-delivered-easy",
        "combinator": "all",   # needs BOTH repeated shots under fixed randomness AND hardness argued on the ideal. Either alone is a design note, not a leak.
        "name": "Attack what was DELIVERED, not what was designed",
        "exploits": (
            "The idealized protocol is hard, but the flown artifact leaks. F119's honest oracle "
            "(fresh sign per copy) is single-copy hard; the flight kit delivered 12 shots per FIXED "
            "row, making qubits deterministic WITHIN a row and leaking the secret per-qubit."
        ),
        "precondition": [
            ("repeated_shots_fixed_randomness", "Does the flown kit deliver MULTIPLE shots under a "
                                                "single draw of the protocol's randomness?"),
            ("hardness_argued_on_ideal", "Is the hardness argument made about the IDEALIZED "
                                         "protocol rather than the delivered data?"),
        ],
        "must_answer": (
            "Run the decoder on a faithful simulation of the DELIVERED rows, with the actual shot "
            "structure and readout noise. Not on the idealized oracle."
        ),
        "history": "Ember C4215 — F119 SUPERSEDED as-executed, QUALIFIED in principle, do not "
                   "submit. Ember named the pattern herself: 'the F121 pattern (idealized-hard, "
                   "delivered-easy)'.",
        "artifact": "experiments/exp142_f119_delivery_attack_ember_c4215.py",
    },
    {
        "id": "under-priced-baseline",
        "combinator": "any",   # EITHER an assumed shot count OR a denied speedup under-prices the baseline on its own.
        "name": "Give the baseline every advantage it is legally entitled to",
        "exploits": (
            "A conventional arm priced with assumed shot counts rather than an optimal sequential "
            "test, and denied speedups it is entitled to (commuting narrowing, concatenation). "
            "An under-priced baseline manufactures the ratio."
        ),
        "precondition": [
            ("baseline_shots_assumed", "Is the classical/conventional arm's cost ASSUMED rather "
                                       "than simulated under an optimal strategy?"),
            ("baseline_denied_speedups", "Has the baseline been denied any structure-exploiting "
                                         "speedup it could legally use?"),
        ],
        "must_answer": (
            "Simulate the baseline with an SPRT (or the best sequential test available) AND every "
            "legal speedup. Conservative means giving the baseline everything, not the reverse."
        ),
        "history": "Elder C6510 — Exp144 SS4. Claim SURVIVED: 'no poly single-copy shortcut found "
                   "... the design intent holds under self-attack.' The one clean survival, and it "
                   "is what a pass is supposed to look like.",
        "artifact": "experiments/exp144_baseline_redteam_mc_elder_c6510.py",
    },
    {
        "id": "ceiling-quoted-as-advantage",
        "combinator": "all",   # needs BOTH a simulation-priced ratio AND no problem-specific search. A simulation ratio reported alongside a completed search is a legitimate ceiling.
        "name": "A simulation cost is a ceiling, not an advantage",
        "exploits": (
            "Quoting the cost of imitating the machine as though it were the cost of beating it. "
            "This is the generalisation of planted-structure-leak and it catches the case where no "
            "specific attack is known yet — the number is still only an upper bound."
        ),
        "precondition": [
            ("ratio_against_simulation", "Is the headline ratio taken against a SIMULATION cost?"),
            ("no_problem_specific_search", "Has NO systematic search for a problem-specific "
                                           "classical algorithm been run and reported?"),
        ],
        "must_answer": (
            "Report the number as a CEILING with that word, or run the search. Whisper C5027 built "
            "a fully verified stabilizer-rank solver and opened its plan by calling the simulation "
            "cost 'the classical arm' — fifteen days after personally retiring that framing."
        ),
        "history": "Whisper C5027 — self-caught, no claim shipped. The solver's plan document "
                   "carries the correction above its own opening sentence.",
        "artifact": "docs/solver-plan-whisper-c5021.md",
    },
    {
        "id": "billing-currency",
        "combinator": "any",   # EITHER a unit mismatch OR a stopping-rule mismatch corrupts the ratio on its own — each is sufficient to inflate a margin. (Adopted from retro C5050 R1; drafted C5056 under board #68.)
        "name": "Both arms in one currency, one stopping rule, frozen before any number",
        "exploits": (
            "A headline ratio whose arms are billed in different units (samples vs copies, jobs vs "
            "shots, queries vs gate-calls) or stopped under different criteria (a lenient threshold "
            "on one arm vs a rigorous sequential test on the other). Either mismatch manufactures "
            "the margin: the exp142 n=4 margin was posted at 21-29x and was actually 6.6x — the "
            "quantum arm was billed in Bell SAMPLES (1 sample = 2 copies) against a classical arm "
            "billed in COPIES, and its stopping criterion was lenient where C1's was a full Wald "
            "SPRT. The ratio was ~4x inflated by accounting alone; the win itself was real."
        ),
        "precondition": [
            ("arms_billed_in_different_units", "Are the arms' costs expressed in DIFFERENT units, "
                                               "or units needing any conversion factor to compare?"),
            ("stopping_rules_differ_or_unit_unfrozen", "Do the arms stop under DIFFERENT criteria, "
                                                       "OR was the billing unit / stopping rule "
                                                       "chosen or changed AFTER any headline "
                                                       "number was computed?"),
        ],
        "must_answer": (
            "Declare ONE unit and ONE stopping rule for both arms BY NAME ('copies', 'Wald SPRT') "
            "— values, never yes/no; if either answer ever degrades to a boolean this class "
            "certifies nothing (Ember #8949, pinned at adoption). Freeze them in the prereg before "
            "any ratio is computed, re-derive every previously-posted number in that unit, and "
            "RECORD THE REJECTED convention with its would-be number (the F122 draft's own form: "
            "'18.6x under Bell-as-one-copy, which we do not claim') — the discarded convention is "
            "the evidence a choice was made rather than inherited, and it is what a hostile "
            "reviewer asks for first. A conversion factor stated at correction time is an "
            "admission, not a fix. [AMENDMENT at adoption, Elder #8957 — the precision fork: "
            "same unit + same stopping rule can still fork if the SHARED INPUT of a derived "
            "ratio is quoted at a digit that does not pin the ratio (the 9.26-vs-9.28 case, "
            "resolved #8831). Rule: quote every shared input to the precision that pins the "
            "derived figure, and every document derives from the SOURCE record at write time — "
            "never carries another document's derived value.]"
        ),
        "history": "Whisper/Elder C5003 (#1294) — exp142 n=4 margin corrected 21-29x -> 6.6x after "
                   "the inflated number had been propagated to the Creator; all three seats "
                   "re-stated. Same class: C5047 door(b) registered budget 6.8x low (arms scale "
                   "differently -> weakest-cell costing inverts). Retro C5050 graded the prose "
                   "rule FAILED TWICE and ordered this instrument form.",
        "artifact": "logs/retrospective-c5050-50cy.md (DC15W) + exp142 margin-correction thread",
    },
]


def template():
    keys = {}
    for a in ATTACKS:
        for k, q in a["precondition"]:
            keys[k] = q
    return {
        "claim": "<one line: what advantage is being claimed, against what baseline>",
        "answers": {k: "unknown" for k in sorted(keys)},
        "_questions": keys,
        "_note": "answer yes / no / unknown. 'unknown' BLOCKS exactly as 'yes' does.",
    }


def run(claim):
    answers = claim.get("answers", {})
    applies, clear = [], []
    for a in ATTACKS:
        hits = [(k, q) for k, q in a["precondition"]
                if str(answers.get(k, "unknown")).lower() in ("yes", "true", "unknown")]
        # PER-CLASS COMBINATOR (C5027). The first version treated preconditions as OR and
        # false-positived on the FIRST real claim it was run against: F113's 2D-HLF instance is
        # public by construction, which tripped planted-structure-leak even though F113 prices no
        # simulation baseline and makes no runtime claim. A tool built to catch over-claiming that
        # itself over-fires is worse than no tool — it trains its user to dismiss it.
        need_all = a.get("combinator", "all") == "all"
        fires = (len(hits) == len(a["precondition"])) if need_all else bool(hits)
        (applies if fires else clear).append((a, hits))
    return applies, clear


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--claim")
    ap.add_argument("--interactive-template", action="store_true")
    a = ap.parse_args()

    if a.interactive_template:
        print(json.dumps(template(), indent=2))
        return

    if a.list or not a.claim:
        print("ATTACK CLASSES THAT HAVE FIRED AT OUR OWN CLAIMS\n")
        for at in ATTACKS:
            print(f"  [{at['id']}]  {at['name']}")
            print(f"     exploits : {at['exploits']}")
            print(f"     history  : {at['history']}")
            print(f"     artifact : {at['artifact']}")
            print(f"     must     : {at['must_answer']}\n")
        print("  ⚠️ THIS CANNOT FIND NOVEL ATTACKS. It fires the classes that have already broken")
        print("     our claims. The C4996 attack was novel when it fired and no checklist would")
        print("     have contained it. PASSING IS A FLOOR, NOT A CERTIFICATE.")
        if not a.claim:
            print("\n  usage: --interactive-template > claim.json, fill it in, then --claim claim.json")
        return

    claim = json.load(open(a.claim))
    applies, clear = run(claim)
    print(f"ATTACK PRE-FLIGHT — {claim.get('claim','(unnamed claim)')}\n")
    for at, hits in clear:
        print(f"  ✅ CLEAR   [{at['id']}] — preconditions answered 'no'")
    for at, hits in applies:
        print(f"\n  🔴 APPLIES [{at['id']}]  {at['name']}")
        for k, q in hits:
            print(f"       {str(claim.get('answers',{}).get(k,'unknown')).upper():<8} {q}")
        print(f"       HISTORY : {at['history']}")
        print(f"       YOU MUST: {at['must_answer']}")
    print()
    if applies:
        print(f"  ⛔ {len(applies)} attack class(es) apply and are unanswered. NOT CLEARED TO CLAIM.")
        sys.exit(1)
    print("  ✅ All known attack classes cleared. That is a FLOOR, not a certificate —")
    print("     it means the claim survives attacks we already know about.")


if __name__ == "__main__":
    main()
