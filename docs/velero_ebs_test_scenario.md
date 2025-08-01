# 🔁 Reproducible Velero EBS Backup & Restore Scenario

This step-by-step guide walks you through setting up and testing an EBS volume snapshot recovery using Velero on AWS EKS. All commands are tested and reproducible.

---

## 📦 Requirements

- AWS CLI, `kubectl`, `eksctl`, `velero`, `jq`, and `Python 3.8+`
- An IAM role with admin access
- An S3 bucket (e.g. `jcps-velero-backups`) for storing backups
- Ubuntu EC2 instance (t3.medium or larger)
- IAM OIDC provider enabled on your EKS cluster

---

## 🛠 1. Create EKS Cluster

```bash
eksctl create cluster \
  --name jcps-demo \
  --region eu-west-1 \
  --nodegroup-name jcps-workers \
  --node-type t3.medium \
  --nodes 2 \
  --with-oidc \
  --managed
```

---

## 🔐 2. Create IAM Policy for Velero

```bash
aws iam create-policy \
  --policy-name VeleroS3EBSBackupPolicy \
  --policy-document file://manifests/velero-policy.json
```

---

## 🔗 3. Attach IAM Service Account

```bash
eksctl create iamserviceaccount \
  --name velero \
  --namespace velero \
  --cluster jcps-demo \
  --attach-policy-arn arn:aws:iam::<your-account-id>:policy/VeleroS3EBSBackupPolicy \
  --approve \
  --region eu-west-1
```

---

## 💾 4. Install Velero with AWS Plugin

```bash
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket jcps-velero-backups \
  --backup-location-config region=eu-west-1 \
  --snapshot-location-config region=eu-west-1 \
  --use-volume-snapshots=true \
  --service-account-name velero \
  --namespace velero \
  --no-secret \
  --wait
```

---

## 🧪 5. Deploy Sample Workload

```bash
kubectl create ns aee
```

Apply the following YAML to create a secret, PVC, and pod that writes to EBS:

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: etx-admin-apikey
  namespace: aee
type: Opaque
data:
  api-key: SGVsbG9Gcm9tQVBJ # "HelloFromAPI"

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: etx-pvc
  namespace: aee
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: gp2

---
apiVersion: v1
kind: Pod
metadata:
  name: etx-pod
  namespace: aee
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "echo 'Hello from AEE' > /data/hello.txt && sleep 3600"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: etx-pvc
```

Save this as `manifests/sample-etx-deployment.yaml` and apply:

```bash
kubectl apply -f manifests/sample-etx-deployment.yaml
```

---

## 📸 6. Backup the Workload

```bash
velero backup create aee-backup --include-namespaces aee --wait
```

---

## 💣 7. Simulate a Disaster

```bash
kubectl delete ns aee
```

---

## 🤖 8. Run Python Automation for Restore

```bash
python3 automation/velero_restore_automation.py --backup aee-backup --from-ns aee --to-ns aee-a
```

---

## 🔍 9. Verify Recovery

```bash
kubectl get pods,pvc,secrets -n aee-a
kubectl exec -n aee-a etx-pod -- cat /data/hello.txt
```

Expected output:

```
Hello from AEE
```

---

## 🧼 10. Clean Up (Optional)

```bash
bash scripts/delete_versioned_s3_bucket.sh
```

---

## 📁 Reference Files in This Repo

- `automation/velero_restore_automation.py`: Python restore script
- `manifests/sample-etx-deployment.yaml`: Test workload
- `docs/errors_and_fixes.md`: All issues and how we solved them
- `docs/manual_restore_steps.md`: Original manual steps

---

Ready to be used in your own AWS environment.

