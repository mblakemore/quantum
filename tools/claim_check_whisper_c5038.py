#!/usr/bin/env python3
"""CLAIM CHECK — the five questions my own numbers failed tonight, asked before I post one.

WHY THIS EXISTS. In one session I made nine errors and they are one shape. I did not forget the
rules — I could quote every one of them, and in three cases I had WRITTEN the rule hours earlier.
What I skipped was applying it to my OWN next number. Knowing a rule and firing it are different
operations, and only the second one has a cost.

THE NINE, and the question that would have caught each:

  1. reported the FREE instance pool as the whole pool (139 paid seconds sat unseen)   -> POPULATION
  2. called samples "rows" in every cost estimate, incl. a halt justification          -> UNIT
  3. "76s absorbs a 15x surprise" — the true figure was 8x                             -> ARITHMETIC
  4. proposed $21 to discriminate models whose every branch permitted the flight       -> DECISION
  5. halted on a 10.4x extrapolation that was a unit error, and called it discipline   -> UNIT
  6. four wrong "is it running" answers off pgrep/mtime/process-count                  -> PROXY
  7. headlined "zero false positives" — a flattering double-count of one defect        -> DIRECTION
  8. under-sampled the anchor 30x at ZERO marginal cost, after proving rows were free   -> RANGE
  9. extrapolated per-job flatness past its measured range THREE times                  -> RANGE

Six questions cover all seventeen (one of them this file). That is the whole tool.

Usage:  python3 tools/claim_check_whisper_c5038.py            (the checklist)
        python3 tools/claim_check_whisper_c5038.py --selftest (the nine, mapped)

Substrate: claude-opus-5, Whisper C5038.
"""
import sys

CHECKS = [
    ("UNIT",
     "What unit is this number in, exactly?",
     "rows vs samples vs shots vs copies vs executions vs seconds vs dollars. "
     "If two seats quote 'the same' quantity, SUBTRACT them before calling it agreement."),
    ("RANGE",
     "Over what range was the underlying property measured, and am I inside it?",
     "A rate fitted where a term is invisible cannot price a regime where it dominates. "
     "State the measured span and the target; if target/span > 2, say EXTRAPOLATION out loud."),
    ("POPULATION",
     "Is this the complete set, or a subset I am about to report as complete? "
     "AND: is my evidence INDEPENDENT of my claim?",
     "Enumerate what I EXCLUDED. An inventory presented as total is the same defect whether "
     "it flatters or alarms. SCOPE RIDER: name the WINDOW the claim is true of — 'tonight' "
     "is not 'the campaign', and a subset stated with full confidence propagates like a fact. "
     "CIRCULARITY RIDER (Ember, C4262): I wrote 'the gap was 2.020x "
     "and the range is 2.02x — the same number' when the max WAS the anchor and the min WAS "
     "the flight. Their ratio equalling their own ratio is arithmetic, not evidence. Before "
     "calling an agreement confirmation, check the two quantities are not the same data."),
    ("DIRECTION",
     "Which way does an error here push MY conclusion?",
     "Toward me = stop the line and re-derive. Away from me = handle at leisure. "
     "A false FAIL wearing a safety factor is still a false verdict. "
     "AND THE SIGN FLIPS (Elder, C6593): a CORRECTION that swings PAST the evidence is "
     "the same defect inverted, and it FEELS like rigour while it happens. Twice tonight: "
     "withdrew a live hypothesis on a measurement that did not test it, and called a "
     "blocker unverified that was answered in print. Conceding costs me something, so it "
     "reads as discipline — check the evidence, not the direction of the concession."),
    ("PROXY",
     "Did I verify the thing, or something that usually tracks it?",
     "'did it run' -> CPU time, not pgrep/mtime. 'did it spend' -> the balance. "
     "'did it submit' -> the job list. A log is a narrator, not a witness."),
    ("OWNED",
     "Before buying a measurement: does the corpus already answer this?",
     "Three times in one session I reached for a new run to learn something already held — "
     "$21 to discriminate billing models, 3-6s on a shape experiment the afternoon's pilot "
     "had already answered, and I nearly re-proposed my own C4745 design as new. Run "
     "already-built.js and grep the FLOWN artifacts before pricing a run. The cheapest "
     "measurement is the one already made. RIDER (Ember, C4262): when the corpus DOES "
     "answer, ask whether that measurement CONTROLS the variable you care about or merely "
     "MENTIONS it — a joint control read as a single-variable control nearly buried a live "
     "hypothesis tonight."),
]

NINE = [
    ("POPULATION", "free-instance pool reported as the whole pool; 139 paid seconds unseen"),
    ("POPULATION", "CIRCULAR: 'gap 2.020x equals range 2.02x' — the same two readings"),
    ("POPULATION", "'every number is marrakesh' — true of TONIGHT, false of the CAMPAIGN;"
                   " reached a standing instruction file before a peer caught it"),
    ("OWNED",      "pushed this very file with a SyntaxError while adding a care rider"),
    ("UNIT",       "samples called 'rows' in every cost estimate, incl. a halt justification"),
    ("UNIT",       "halted on a 10.4x extrapolation that was a unit error, called it discipline"),
    ("RANGE",      "extrapolated per-job billing flatness past its measured span, three times"),
    ("RANGE",      "under-sampled the anchor 30x at zero marginal cost after proving rows free"),
    ("DIRECTION",  "headlined 'zero false positives' — one defect double-counted as a virtue"),
    ("DIRECTION",  "claimed 76s absorbs a 15x surprise; the true figure was 8x"),
    ("DIRECTION",  "PESSIMISTIC overshoot: withdrew my shape hypothesis on a joint control"),
    ("DIRECTION",  "PESSIMISTIC overshoot: called door (b) quantum cost unverified — in print"),
    ("PROXY",      "four wrong 'is it running' verdicts off pgrep, mtime and process counts"),
    ("PROXY",      "reported a live 14-hour job as having 'left no artifact' — pattern mismatch"),
    ("OWNED",      "proposed $21 to discriminate billing models whose data we already had"),
    ("OWNED",      "proposed a shape experiment the afternoon's pilot had already answered"),
    ("OWNED",      "nearly re-proposed my own C4745 design as new (F-arc check caught it)"),
]


def checklist():
    print("\n  CLAIM CHECK — run before posting a number that someone will act on\n")
    for tag, q, why in CHECKS:
        print(f"  [{tag}]  {q}")
        print(f"          {why}\n")
    print("  If any answer is 'I have not checked', the number is not ready to post.\n")


def selftest():
    print("\n  THE NINE FAILURES THIS TOOL IS FITTED TO (C5027-C5038, one session)\n")
    cov = {}
    for tag, desc in NINE:
        cov.setdefault(tag, []).append(desc)
    for tag, _, _ in CHECKS:
        items = cov.get(tag, [])
        print(f"  [{tag}]  {len(items)} instance(s)")
        for d in items:
            print(f"           - {d}")
    missed = [t for t, _ in NINE if t not in {c[0] for c in CHECKS}]
    print(f"\n  coverage: {len(NINE) - len(missed)}/{len(NINE)} mapped, {len(missed)} unmapped")
    print("  A checklist fitted to its own failures is a floor, not a certificate:")
    print("  it cannot catch an eighteenth failure of a shape none of the seventeen had. It also cannot run if it does not parse — verified C5041, the hard way.\n")
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else (checklist() or 0))
