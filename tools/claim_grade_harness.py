#!/usr/bin/env python3
"""P0 — The Universal Translator: the claim-grade harness (H9, Whisper C5001).

Codifies the FIVE GATES the C4998-4999 arc forged by failing each. Every advantage-flavored claim
runs this lint before it is called an advantage or prepared for First Contact (external framing).
This is an ORCHESTRATOR over existing instruments — it does NOT rebuild them:
  - Gate 3 (on-device fidelity) DEFERS to Ember's pre-seal gate
    (experiments/exp142_preseal_fidelity_gate_ember_c4215.py) — referenced, not duplicated.
  - Gates 1/2/4/5 are rubric checks the harness encodes and forces an answer on.

THE FIVE GATES (each learned by failing it):
  G1 FLOOR-TYPE      (F121): floor must be a THEOREM over a PHYSICALLY-ENFORCED access model,
                     not conjectured hardness of a PUBLISHED structure. Values:
                     theorem-over-access | asymptotic-apparatus | best-known-conditional | none.
  G2 INSTANTIATION   (#844): the ensemble that ENFORCES the floor must be buildable at CERTIFIED
                     order. Haar/high-design => exponential depth => not flyable. Values:
                     native-shallow | bounded-design | haar-exponential(BLOCKED) | n/a.
  G3 ON-DEVICE FID   (F119 washout): DELIVERED fidelity on real hardware, via the pre-seal <P> gate
                     on a public test-P. Logical+transpile exactness are necessary NOT sufficient.
                     Values: gate-PASS | gate-FAIL | gate-PENDING | not-applicable(non-fragile).
  G4 SEALED COURT    : estimator frozen PRE-REVEAL, sealed-commitment 3-of-3. Values: yes | no.
  G5 OWN-HAND RED-TEAM: an adversary run by us BEFORE external framing. Values: yes | no | n/a.

VERDICTS:
  EXTERNAL-READY            : G1 in {theorem-over-access}, G2 not blocked, G3 pass/na, G4 yes, G5 yes.
  ADVANTAGE-CONDITIONAL     : G1 best-known-conditional, gates otherwise clear (label conditional).
  INSTRUMENT-NOT-ADVANTAGE  : G1 asymptotic-apparatus OR a measurement primitive (real, not a speedup).
  NEEDS-GATE                : any required gate PENDING (e.g. G3 gate-PENDING) — not yet a claim.
  SUPERSEDED / RETIRED      : a floor was broken (own red-team or classical progress).
  BLOCKED                   : G2 haar-exponential — theorem unflyable at certified order.
"""
import json
import sys

FLOOR_TYPES = {"theorem-over-access", "asymptotic-apparatus", "best-known-conditional", "none"}
PRESEAL_GATE = "experiments/exp142_preseal_fidelity_gate_ember_c4215.py"


def grade(claim):
    g1 = claim.get("floor_type")
    g2 = claim.get("instantiation")
    g3 = claim.get("on_device_fidelity")
    g4 = claim.get("sealed_court")
    g5 = claim.get("own_hand_red_team")
    notes = []
    assert g1 in FLOOR_TYPES, f"floor_type must be one of {FLOOR_TYPES}, got {g1!r}"

    # explicit supersession short-circuits
    if claim.get("superseded"):
        return "SUPERSEDED/RETIRED", [f"floor broken: {claim.get('superseded')}"]
    if g2 == "haar-exponential":
        return "BLOCKED", ["G2: the floor-enforcing ensemble needs a Haar/high-order design "
                           "(exponential depth) — theorem unflyable at certified order (#844)."]
    if g3 == "gate-FAIL":
        return "NEEDS-GATE", ["G3: pre-seal fidelity gate FAILED — delivered state does not "
                              f"survive on-device ({PRESEAL_GATE}); redesign the prep."]
    if g3 == "gate-PENDING":
        notes.append(f"G3: pre-seal gate not yet run ({PRESEAL_GATE}) — must PASS before First Contact.")

    if g1 == "asymptotic-apparatus":
        return "INSTRUMENT-NOT-ADVANTAGE", notes + ["G1: apparatus of an asymptotic theorem, "
                                                    "not a raw speedup — labeled as instrument."]
    if g1 == "none":
        return "INSTRUMENT-NOT-ADVANTAGE", notes + ["G1: no theorem floor — measurement/resource "
                                                    "result, not an advantage."]
    if g1 == "best-known-conditional":
        v = "ADVANTAGE-CONDITIONAL" if g3 != "gate-PENDING" else "NEEDS-GATE"
        return v, notes + ["G1: best-known-conditional floor — advantage is real vs best-known, "
                           "supersedable; label conditional, never 'unconditional'."]

    # g1 == theorem-over-access — the strong case; require the rest.
    # Normalize G4/G5: accept truthy or "yes"; "n/a" satisfies G5 (no adversary applies).
    def sat(v):
        return v is True or v == "yes"
    g5_ok = sat(g5) or g5 == "n/a"
    if g3 == "gate-PENDING":
        return "NEEDS-GATE", notes
    if not sat(g4):
        notes.append("G4: no sealed pre-reveal court — add before external framing.")
    if not g5_ok:
        notes.append("G5: no own-hand red-team — run the adversary before First Contact.")
    if not (sat(g4) and g5_ok):
        return "ADVANTAGE-INTERNAL", notes + ["theorem-floored + delivered, but G4/G5 incomplete "
                                              "— internal-grade until the court + red-team close."]
    # all five gates clear. A scope_fence means the claim is external-ready ONLY if the fence leads.
    if claim.get("scope_fence"):
        return "EXTERNAL-READY-FENCED", notes + [
            f"all gates clear; SCOPE FENCE must lead the claim externally: {claim['scope_fence']}"]
    return "EXTERNAL-READY", notes + ["all five gates clear (or n/a) — prepared to survive First "
                                      "Contact; submission is the Creator's call."]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "results/h9_p3_claim_ledger.json"
    ledger = json.load(open(src))
    rows = ledger["claims"] if isinstance(ledger, dict) else ledger
    print(f"{'CLAIM':<34}{'FLOOR-TYPE':<24}{'VERDICT'}")
    print("-" * 90)
    out = []
    for c in rows:
        v, notes = grade(c)
        out.append({**c, "verdict": v, "grade_notes": notes})
        print(f"{c['id']:<34}{c['floor_type']:<24}{v}")
    graded_path = src.replace(".json", "_graded.json")
    json.dump({"harness": "claim_grade_harness P0 (C5001)", "graded": out},
              open(graded_path, "w"), indent=1)
    print(f"\ngraded ledger -> {graded_path}")


if __name__ == "__main__":
    main()
