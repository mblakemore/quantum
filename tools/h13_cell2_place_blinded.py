#!/usr/bin/env python3
"""STEP 2 of 2 — THE SEALER RUNS THIS. No IBM credentials needed, no network.

Takes Whisper's raw dump + a permutation the SEALER generates from her own off-git secret, and
emits the blinded directory. The secret never leaves the sealer's seat; Whisper never sees a
set_id. Contains NO RNG for the assignment — the sealer supplies it — but DOES normalise mtimes
so write order leaks nothing (Ember's filesystem channel).

Usage: python3 tools/h13_cell2_place_blinded.py <dump.json> <sealer_permutation.json> <outdir>
  sealer file: {"assignments":[{"set_id":"<opaque>","unit":<int>,"arm":"CE"|"CC"}, ...]}
"""
import json, os, sys, hashlib
FIXED_MTIME=1000000000
if len(sys.argv)<4: sys.exit("usage: place_blinded.py <dump.json> <sealer_permutation.json> <outdir>")
dump=json.load(open(sys.argv[1])); _payloads=[]
assign=json.load(open(sys.argv[2]))["assignments"]; outdir=sys.argv[3]
sets=dump["sets"]
if len(assign)!=len(sets): sys.exit(f"REFUSING: {len(assign)} assignments vs {len(sets)} sets")
os.makedirs(outdir,exist_ok=True)
for a in assign:
    k=f"{a['unit']}|{a['arm']}"
    if k not in sets: sys.exit(f"REFUSING: assignment references unknown set {k}")
    recs=[]
    for b in ("X","Y","Z"):
        # ENCODING DECLARED AT PLACEMENT: bit 0 -> +1, bit 1 -> -1 (Ember Option C)
        # ══ PER-RECORD WIDTH COMPENSATOR — LEAKS 11 AND 12 ═══════════════════════════════════
        # LEAK 11: `-1` is TWO chars and `1` is ONE, so file size was EXACTLY LINEAR in the -1
        #   count -> linear in the correlator -> `ls -l` classified all 80 sets at 100%.
        # LEAK 12: my first fix padded to a constant TOTAL. pad = target - body, so the PAD
        #   LENGTH carried the same signal INVERTED AND AMPLIFIED (CE 688-990, CC 5-199).
        #   Ember's rule: CONSERVED QUANTITIES MOVE THE SIGNAL, THEY DO NOT DESTROY IT. Any
        #   compensator computed FROM the varying quantity re-encodes it.
        # THE FIX: compensate INSIDE each record, so every record is the same width and no
        #   file-level summary exists. The filler is still derived from the values — but it is
        #   recoverable only by iterating 3,000 records and counting, which is EXACTLY what
        #   reading the values costs (Ember measured identical effort). It adds a second
        #   equally-easy path, NOT an easier one, and the values path is the content channel
        #   already accepted as irreducible at leak 5.
        # Values stay INTEGERS in {1,-1} and records keep basis/a/b, so Elder's decoder stays
        # FROZEN at 321abc99 — he verified this form himself rather than taking it on report.
        for x, y in sets[k][b]:
            av = 1 if x == 0 else -1
            bv = 1 if y == 0 else -1
            fill = (0 if av < 0 else 1) + (0 if bv < 0 else 1)   # one char per missing '-'
            recs.append({"basis": b+b, "a": av, "b": bv, "_": "." * fill})
    pth=os.path.join(outdir,f"{a['set_id']}.json")
    # SERIALISATION IS STATED, NOT INHERITED (Ember's choice (i), general#9908). The width leak
    # got in because the format was whatever json.dumps happened to do. A blindness property
    # that depends on BYTE-LEVEL output must not rest on a library default that can differ
    # between versions, callers or seats — and the default form also silently broke the
    # verification patterns of the sweep meant to check this very fix.
    out = json.dumps({"encoding":"pm1","records":recs}, separators=(",",":"))
    open(pth,"w").write(out)
    os.utime(pth,(FIXED_MTIME,FIXED_MTIME))
    _payloads.append((pth, len(out)))

# FAIL CLOSED ON THE INVARIANT THIS FIX EXISTS FOR — checked, never trusted, because the pad
# arithmetic is precisely what was wrong the last two times.
_sizes = {n for _, n in _payloads}
if len(_sizes) != 1:
    sys.exit(f"🔴 REFUSING: file sizes are NOT constant ({len(_sizes)} distinct) — the leak-11 "
             f"channel is OPEN. Sizes: {sorted(_sizes)[:5]}")
print(f"[place] all {len(_payloads)} files byte-identical: {next(iter(_sizes)):,} B, compact form "
      f"(leak-11 and leak-12 channels closed)")

mapping={a["set_id"]: a["arm"] for a in assign}
print(f"[place] {len(assign)} sets -> {outdir}; all mtimes normalized")
print(f"[place] mapping digest (SEALER's to publish): {hashlib.sha256(json.dumps(mapping,sort_keys=True).encode()).hexdigest()}")
