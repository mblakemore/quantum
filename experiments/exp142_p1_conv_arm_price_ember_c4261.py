"""Whisper #6169 ask: price the CONVENTIONAL arm too. READ-ONLY."""
import sys, json
sys.path.insert(0,'experiments'); sys.path.insert(0,'scripts')
from run_exp66_qpu_partb import _get_ibm_service
from exp142_flight_kit import pick_layouts
bk=_get_ibm_service().backend('ibm_marrakesh')
t=bk.target
ro={q:(t["measure"][(q,)].error or 0.0) for (q,) in t["measure"].keys()}
pin=json.load(open('results/p1_kit_confirm.json'))
print(f"kit-confirm pins recorded: {list(pin.keys())}")
print(f"  conventional pin present? {'conv_layout' in pin}  <-- NO conv pin was ever recorded\n")
for n in (4,6,8):
    q_layout, conv_layout, pairs = pick_layouts(bk,n)
    errs=[ro[q] for q in conv_layout]
    # what the quantum arm's qubits cost on the SAME readout axis, for symmetry
    qerrs=[ro[q] for q in q_layout]
    print(f"n={n}  conv_layout today = {conv_layout}")
    print(f"      readout err: worst {max(errs):.5f}  mean {sum(errs)/len(errs):.5f}")
    print(f"      quantum-arm qubits on same axis: worst {max(qerrs):.5f} mean {sum(qerrs)/len(qerrs):.5f}")
    print(f"      both returns came from ONE pick_layouts call -> same calibration epoch")
    print()
