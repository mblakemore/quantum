#!/bin/bash
# aer_gpu_env.sh — environment shim for the from-source ROCm/gfx1201 qiskit-aer GPU build.
# Built by Ember C3754. Activates the GPU-capable AerSimulator on AMD RDNA4 (gfx1201).
#
# WHY THIS EXISTS: the GPU wheel was linked against an ILP64 OpenBLAS (numpy.libs,
# symbols suffixed _64_) whose DT_NEEDED soname the loader resolves BY NAME, but Aer
# calls the unsuffixed LP64 symbols (dlamch_, dgemm_). The stock pip qiskit-aer ships an
# LP64 OpenBLAS that provides those symbols. So we LD_PRELOAD the LP64 lib (wins symbol
# resolution) while keeping the ILP64 dir on LD_LIBRARY_PATH (satisfies the soname).
# Cleaner long-term fix = rebuild the wheel against an LP64 BLAS; this shim avoids that.
#
# USAGE:  source aer_gpu_env.sh   then run python normally, OR
#         ./aer_gpu_env.sh python3 your_script.py
#
# BREAK-EVEN (Ember C3754 benchmark, QuantumVolume d10, single precision):
#   <=22 qubits -> CPU wins (GPU kernel-launch overhead dominates)
#   ~24-25 qubits = break-even
#   25q 1.60x, 28q 1.77x GPU speedup (modest — RDNA4 is not a compute card)
#   => Route to GPU ONLY at >=25 qubits. Small-qubit work (e.g. Exp53 7-9q) stays on CPU.

AER_GPU_VENV="$HOME/aer-gpu-venv"
STOCK_LIBS="$HOME/.local/lib/python3.12/site-packages/qiskit_aer.libs"
STOCK_BLAS="$STOCK_LIBS/libopenblas-r0-f650aae0.3.3.so"
ILP64_DIR="/archive/mike-home/repos/xtts_v2/venv/lib/python3.11/site-packages/numpy.libs"

# shellcheck disable=SC1091
source "$AER_GPU_VENV/bin/activate"
export LD_PRELOAD="$STOCK_BLAS${LD_PRELOAD:+:$LD_PRELOAD}"
export LD_LIBRARY_PATH="$STOCK_LIBS:$ILP64_DIR:/opt/rocm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# If args were passed, exec them; otherwise assume `source`d for interactive use.
if [ "$#" -gt 0 ]; then
  exec "$@"
fi
