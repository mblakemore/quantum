"""$0 pre-seal edge RE-CERT at flight epoch (Ember, 2026-08-07).
Freeze condition (H9-P1, whisper c5003): edges PINNED n4/n6/n8,
"fly-those-or-re-cert-$0-at-flight-epoch". Pinned Jul 24; today is Aug 7.
READ-ONLY: reads backend.target calibration. Submits NOTHING."""
import sys, json
sys.path.insert(0, 'experiments'); sys.path.insert(0, 'scripts')
from run_exp66_qpu_partb import _get_ibm_service
from exp142_flight_kit import pick_layouts

PINNED = json.load(open('results/p1_kit_confirm.json'))['pinned_edges']
svc = _get_ibm_service()
bk = svc.backend('ibm_marrakesh')
print(f"backend {bk.name}  (calibration read, NO submission)\n")

for n in (4, 6, 8):
    _, _, pairs = pick_layouts(bk, n)
    now = [list(p) for p in pairs]
    was = PINNED[str(n)]
    same = [tuple(e) for e in now] == [tuple(e) for e in was]
    print(f"n={n}")
    print(f"  pinned Jul-24 : {was}")
    print(f"  picked today  : {now}")
    if same:
        print("  ✓ IDENTICAL — pin holds at this epoch")
    else:
        sw, sn = {tuple(sorted(e)) for e in was}, {tuple(sorted(e)) for e in now}
        print(f"  ⚠ MOVED — dropped {sorted(sw-sn)}  gained {sorted(sn-sw)}")
        print(f"    overlap {len(sw&sn)}/{len(sw)}")
    print()
