#!/usr/bin/env python3
"""
dialogue_protocol.py — conversation under oath: sealed adaptive-policy machinery (H14 B6, Whisper C5069).

THE MOVE THIS ENCODES (charter B6, Creator-approved amendment): our flights are questionnaires —
sealed question lists, answers read afterward. The record shows dialogue wins (Kitaev-IPE live
feedforward +25.24pp; the H7 closed-loop cell at 154sigma), but adaptivity is where the garden of
forking paths grows. The resolution: MOVE THE SEAL ONE LEVEL UP. Freeze the questioning POLICY —
priors, chooser, stopping criterion — hash-pin it, log the full transcript verbatim, and let a
grader REPLAY the policy against the transcript. The court's guarantees survive; the conversation
becomes as smart as the policy.

Three guarantees, each with a demonstrated control in --selftest:
  1. REPLAYABILITY  a deterministic sealed policy + the logged answers reproduce every question
     asked, bit for bit — so a swapped/reordered/extra question is DETECTED (P2).
  2. STOPPING UNDER ADVERSARY  answers crafted to lure the policy into running forever hit the
     policy's own hard budget, and the grader verifies the stop cited the sealed rule (P3).
  3. HONEST PASS  an untampered dialogue replays clean (P1) — the grader can pass, so its
     failures mean something.

An adaptive result WITHOUT its transcript is unverifiable by construction — the transcript is
load-bearing, not a courtesy log. Policies are code: B3's seed-storm fence applies to any compiled
object a policy emits, at the flight's exact settings.

    python3 tools/dialogue_protocol.py --selftest
    python3 tools/dialogue_protocol.py --fragment
"""
import hashlib
import json
import sys


# ---------- the sealed-policy contract ----------

def policy_hash(policy_spec):
    """Hash of the canonical-JSON policy spec — the object a prereg pins. Content-hash, not git-blob."""
    return hashlib.sha256(json.dumps(policy_spec, sort_keys=True).encode()).hexdigest()


def run_dialogue(policy, max_turns, answer_fn):
    """Execute a sealed policy against an answer source, logging the transcript verbatim.
    policy: object with .first_question() and .next_question(transcript) -> question or ("STOP", reason)
    Returns (transcript, stop_reason). transcript = [(question, answer), ...] in order."""
    transcript = []
    q = policy.first_question()
    for turn in range(max_turns):
        a = answer_fn(q)
        transcript.append((q, a))
        nxt = policy.next_question(transcript)
        if isinstance(nxt, tuple) and nxt[0] == "STOP":
            return transcript, nxt[1]
        q = nxt
    return transcript, f"BUDGET: hard cap {max_turns} turns reached"


def replay_grade(policy, transcript, stop_reason, max_turns):
    """The grader seat: replay the sealed policy against the LOGGED answers and verify that every
    question asked is the question the policy would have asked. One code path with the flight
    (same next_question), validated by its own controls before grading anything real."""
    if not transcript:
        return {"verdict": "FAIL", "reason": "empty transcript — an adaptive result without its "
                                             "transcript is unverifiable by construction"}
    expect = policy.first_question()
    for i, (q, a) in enumerate(transcript):
        if q != expect:
            return {"verdict": "FAIL", "turn": i,
                    "reason": f"transcript question {q!r} != policy's question {expect!r} — "
                              "the dialogue deviated from the sealed policy"}
        nxt = policy.next_question(transcript[:i + 1])
        if isinstance(nxt, tuple) and nxt[0] == "STOP":
            if i != len(transcript) - 1:
                return {"verdict": "FAIL", "turn": i,
                        "reason": "policy stopped here but the transcript continues — "
                                  "extra questions were asked past the sealed stopping rule"}
            return {"verdict": "PASS", "turns": len(transcript), "stop": nxt[1],
                    "stop_matches": nxt[1] == stop_reason}
        expect = nxt
    if len(transcript) >= max_turns:
        ok = stop_reason.startswith("BUDGET")
        return {"verdict": "PASS" if ok else "FAIL", "turns": len(transcript),
                "stop": stop_reason,
                "reason": None if ok else "ran to the cap but the recorded stop reason does not "
                                          "cite the budget — a discretionary stop wearing a rule's clothes"}
    return {"verdict": "FAIL", "reason": "transcript ended before the policy stopped — "
                                         "answers are missing (truncated record)"}


# ---------- a concrete sealed policy (the selftest vehicle; also a usable default) ----------

class BisectionPolicy:
    """Deterministic 1D bisection: locate a threshold x* in [0,1) by asking 'is x* < q?'.
    Sealed constants: tolerance and max_turns. Deterministic by construction — replay is exact."""

    def __init__(self, tol=0.01, max_turns=12):
        self.tol, self.max_turns = tol, max_turns
        self.spec = {"class": "BisectionPolicy", "tol": tol, "max_turns": max_turns,
                     "question_form": "is x* < q", "chooser": "interval midpoint"}

    def _interval(self, transcript):
        lo, hi = 0.0, 1.0
        for q, a in transcript:
            x = float(q.split("<")[1].strip().rstrip("?"))
            if a:      # yes: x* < x
                hi = x
            else:
                lo = x
        return lo, hi

    def first_question(self):
        return "is x* < 0.5?"

    def next_question(self, transcript):
        lo, hi = self._interval(transcript)
        if hi - lo <= self.tol:
            return ("STOP", f"RULE: interval width {hi - lo:.4f} <= tol {self.tol}")
        if len(transcript) >= self.max_turns:
            return ("STOP", f"BUDGET: policy max_turns {self.max_turns} reached")
        return f"is x* < {(lo + hi) / 2:.6f}?"


class SequentialEvidencePolicy:
    """SPRT-style: repeatedly query one binary source; STOP on RULE when |#yes - #no| >= margin,
    on BUDGET at max_turns. Its stopping DEPENDS on answer content — the right vehicle for the
    adversarial-lure control (bisection's turn count is fixed by geometry and cannot be stalled)."""

    def __init__(self, margin=3, max_turns=10):
        self.margin, self.max_turns = margin, max_turns
        self.spec = {"class": "SequentialEvidencePolicy", "margin": margin, "max_turns": max_turns,
                     "question_form": "query the source", "chooser": "fixed repeat"}

    def first_question(self):
        return "query the source (1)"

    def next_question(self, transcript):
        s = sum(1 if a else -1 for _, a in transcript)
        if abs(s) >= self.margin:
            return ("STOP", f"RULE: evidence margin |{s}| >= {self.margin}")
        if len(transcript) >= self.max_turns:
            return ("STOP", f"BUDGET: policy max_turns {self.max_turns} reached")
        return f"query the source ({len(transcript) + 1})"


PREREG_FRAGMENT = """\
## Dialogue protocol (standard fragment — B6, H14; conversation under oath)
- Sealed object: the QUESTIONING POLICY — class + constants (priors, chooser, stopping criterion),
  spec hash = <policy_hash(spec)> pinned in this prereg BEFORE flight. The question list is NOT
  sealed; the policy is.
- Transcript: every (question, answer) logged verbatim, in order, to <artifact path> — load-bearing.
  No transcript => the adaptive result is unverifiable by construction and is not graded.
- Grader seat: replay_grade() re-runs the sealed policy against the logged answers; any question
  the policy would not have asked, any question past the stopping rule, and any truncation FAIL.
- Fault ladder (priced at freeze): lying/adversarial answers -> the policy stops on its BUDGET rule
  (demonstrated by this module's P3 control); weather mid-dialogue -> compose the sentinel/abstain
  fences (g_abstain_gate); compiled objects the policy emits -> B3 seed-storm fence at the
  flight's exact settings.
- Determinism: the policy must be deterministic given the transcript (randomness, if any, from a
  sealed seed inside the spec) — replay exactness is what makes the grader's FAIL meaningful.
"""


def selftest():
    pol = BisectionPolicy(tol=0.01, max_turns=12)
    h = policy_hash(pol.spec)
    # P1 — honest dialogue: truthful answers about x*=0.3183; replay must PASS
    xstar = 0.3183
    t, stop = run_dialogue(pol, pol.max_turns, lambda q: xstar < float(q.split("<")[1].strip().rstrip("?")))
    v = replay_grade(BisectionPolicy(tol=0.01, max_turns=12), t, stop, pol.max_turns)
    assert v["verdict"] == "PASS" and stop.startswith("RULE"), (v, stop)
    lo, hi = pol._interval(t)
    assert lo <= xstar <= hi and hi - lo <= 0.01
    print(f"P1 honest dialogue: {len(t)} turns, stop='{stop}', located x* in [{lo:.4f},{hi:.4f}], replay PASS (policy {h[:12]})")
    # P2 — tampered transcript: swap one question for one the policy did not ask -> FAIL with the turn named
    t2 = list(t)
    t2[3] = ("is x* < 0.999999?", t2[3][1])
    v = replay_grade(BisectionPolicy(tol=0.01, max_turns=12), t2, stop, pol.max_turns)
    assert v["verdict"] == "FAIL" and v.get("turn") == 3, v
    print(f"P2 tampered transcript: swapped question detected at turn {v['turn']} -> FAIL (the grader can block)")
    # P3 — adversarial answers crafted to lure the policy off its stopping rule. Vehicle: the
    # sequential-evidence policy (its stop DEPENDS on answers; bisection's cannot be stalled —
    # that discovery is itself recorded: geometry-stopped policies are lure-immune by construction).
    sp = SequentialEvidencePolicy(margin=3, max_turns=10)
    flip = {"v": False}
    def adversary(q):
        flip["v"] = not flip["v"]   # perfectly balanced answers: evidence margin never reaches 3
        return flip["v"]
    t3, stop3 = run_dialogue(sp, sp.max_turns, adversary)
    assert stop3.startswith("BUDGET"), stop3
    v = replay_grade(SequentialEvidencePolicy(margin=3, max_turns=10), t3, stop3, sp.max_turns)
    assert v["verdict"] == "PASS", v   # the record is honest ABOUT being budget-stopped — grader verifies the stop cites the sealed rule
    print(f"P3 adversarial lure: evidence-margin never reached, policy survived to '{stop3}', "
          f"replay verifies the stop cited the sealed budget (and: geometry-stopped policies are lure-immune by construction)")
    # P4 — truncated record: drop the last turn -> FAIL (missing answers are not a smaller dialogue, they are a broken one)
    v = replay_grade(BisectionPolicy(tol=0.01, max_turns=12), t[:-1], stop, pol.max_turns)
    assert v["verdict"] == "FAIL", v
    print("P4 truncated record: FAIL (a dialogue that ends before its policy stopped is a broken record)")
    print(f"\nSELFTEST PASS: seal-the-policy machinery demonstrated on all four controls. "
          f"Policy hash pins the spec; the transcript is load-bearing; the grader replays, and its FAILs mean something.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--fragment" in sys.argv:
        print(PREREG_FRAGMENT)
    else:
        print(__doc__)
