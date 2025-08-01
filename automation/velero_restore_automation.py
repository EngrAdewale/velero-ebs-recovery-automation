import subprocess
import argparse
import time

def run_restore(backup_name, from_ns, to_ns, restore_name=None):
    if not restore_name:
        restore_name = f"{backup_name}-restore-{int(time.time())}"
    print(f"Starting restore from backup '{backup_name}' into namespace '{to_ns}'...")
    cmd = [
        "velero", "restore", "create", restore_name,
        "--from-backup", backup_name,
        "--namespace-mappings", f"{from_ns}:{to_ns}",
        "--wait"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("Restore completed successfully.")
    else:
        print("Restore failed.")
        print(result.stderr)
        exit(1)
    return restore_name

def verify_restore(namespace, pod_name="etx-pod", pvc_name="etx-pvc", secret_name="etx-admin-apikey"):
    checks = {
        "Pod Running": ["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "jsonpath={.status.phase}"],
        "PVC Bound": ["kubectl", "get", "pvc", pvc_name, "-n", namespace, "-o", "jsonpath={.status.phase}"],
        "Secret Exists": ["kubectl", "get", "secret", secret_name, "-n", namespace, "-o", "jsonpath={.metadata.name}"],
        "File Content": ["kubectl", "exec", "-n", namespace, pod_name, "--", "cat", "/data/hello.txt"]
    }
    for desc, cmd in checks.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            output = result.stdout.strip()
            print(f"{desc}: {output if output else 'Not found or empty'}")
        except Exception as e:
            print(f"{desc}: ERROR: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Velero EBS restore and verification")
    parser.add_argument("--backup", required=True, help="Velero backup name")
    parser.add_argument("--from-ns", required=True, help="Source namespace")
    parser.add_argument("--to-ns", required=True, help="Target (restored) namespace")
    parser.add_argument("--restore-name", help="Optional custom restore name")
    args = parser.parse_args()
    restore_name = run_restore(args.backup, args.from_ns, args.to_ns, args.restore_name)
    time.sleep(10)
    verify_restore(args.to_ns)