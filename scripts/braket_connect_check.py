#!/usr/bin/env python3
"""
Braket connection check — cost-safe by default.

Prereqs installed (user site): boto3, amazon-braket-sdk, qiskit-braket-provider.
Credentials read from ~/.aws/credentials (profile [default]); region from ~/.aws/config.

Usage:
  python3 braket_connect_check.py          # FREE  — STS identity + list QPU devices (no jobs submitted)
  python3 braket_connect_check.py --sv1     # ~$    — run a 2-qubit Bell state on the SV1 CLOUD simulator

Only --sv1 spends money (SV1 has a small per-task + per-shot charge). The default run
submits ZERO jobs: get_caller_identity and device listing are free control-plane calls.
"""
import sys

# QPU regions to scan (devices are region-scoped). IonQ=us-east-1, Rigetti=us-west-1, IQM/QuEra=eu-north-1.
QPU_REGIONS = ["us-east-1", "us-west-1", "eu-north-1"]
SV1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"


def check_identity():
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError
    try:
        ident = boto3.client("sts").get_caller_identity()
    except NoCredentialsError:
        print("[auth FAIL] no credentials found — fill in ~/.aws/credentials")
        return False
    except ClientError as e:
        print(f"[auth FAIL] {e.response['Error']['Code']}: {e.response['Error']['Message']}")
        return False
    print(f"[auth OK] account={ident['Account']}  arn={ident['Arn']}")
    return True


def list_devices():
    import boto3
    from braket.aws import AwsDevice
    from botocore.exceptions import ClientError
    print("\nAvailable Braket devices (gate-model QPUs + simulators), by region:")
    seen = 0
    for region in QPU_REGIONS:
        try:
            sess = boto3.Session(region_name=region)
            from braket.aws import AwsSession
            devices = AwsDevice.get_devices(aws_session=AwsSession(boto_session=sess))
        except ClientError as e:
            print(f"  [{region}] error: {e.response['Error']['Code']}")
            continue
        except Exception as e:  # noqa: BLE001 — region may be unauthorized; keep scanning
            print(f"  [{region}] skipped: {type(e).__name__}")
            continue
        for d in devices:
            print(f"  [{region}] {d.status:9} {d.provider_name:14} {d.name:26} {d.arn}")
            seen += 1
    print(f"\n{seen} device entries visible. (QuEra Aquila is ANALOG — not gate-model; exclude from the switch-bench.)")


def run_sv1_bell():
    from qiskit import QuantumCircuit
    from qiskit_braket_provider import BraketProvider
    print("\n[--sv1] submitting a 2-qubit Bell state to the SV1 cloud simulator (small charge)...")
    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1); qc.measure_all()
    backend = BraketProvider().get_backend("SV1")
    counts = backend.run(qc, shots=1000).result().get_counts()
    p_corr = (counts.get("00", 0) + counts.get("11", 0)) / 1000
    print(f"  SV1 Bell counts: {counts}")
    print(f"  P(correlated) = {p_corr:.3f} (ideal 1.000) -> CLOUD PIPE {'OK' if p_corr > 0.9 else 'UNEXPECTED'}")


if __name__ == "__main__":
    if not check_identity():
        sys.exit(1)
    list_devices()
    if "--sv1" in sys.argv:
        run_sv1_bell()
    else:
        print("\n(default run submitted no jobs — $0. Add --sv1 to validate the cloud pipe on the simulator.)")
