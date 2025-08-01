# Errors and Fixes During EBS DR Workflow

---

##  1. Velero pod CrashLoopBackOff

**Error:**
```
namespaces "velero" is forbidden: User "system:serviceaccount:velero:velero" cannot get resource "namespaces"
```

**Cause:** Velero's service account lacked permission to read namespace metadata.

**Fix: Added missing ClusterRoleBinding**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: velero-clusterrolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: velero
    namespace: velero
```

**Apply:**
```bash
kubectl apply -f velero-rbac.yaml
```

---

##  2. PVC Stuck in Pending

**Error:** Pod stuck in `Pending`, PVC was not binding to a volume.

**Cause:** AWS EBS CSI driver was not installed.

**Fix:**
Installed via AWS Console Add-ons or CLI:
```bash
eksctl create addon --name aws-ebs-csi-driver --cluster jcps-demo --region eu-west-1 --service-account-role-arn <role>
```

Validated `gp2` storage class:
```bash
kubectl get sc
```

---

##  3. S3 Bucket `BucketNotEmpty` Error

**Error:**
```
remove_bucket failed: s3://jcps-velero-backups An error occurred (BucketNotEmpty)
```

**Cause:** The bucket is versioned. Deleted objects still have versions or delete markers.

**Fix:**
Used cleanup script:
```bash
bash scripts/delete_versioned_s3_bucket.sh
```

Internally runs:
```bash
aws s3api list-object-versions --bucket jcps-velero-backups --output json | jq -r '.Versions[]?, .DeleteMarkers[]? | "aws s3api delete-object --bucket jcps-velero-backups --key \(.Key) --version-id \(.VersionId)"' | bash
```

---

##  4. Velero Install Fails on `--default-volumes-to-restic`

**Error:**
```
unknown flag: --default-volumes-to-restic
```

**Fix:**
Removed deprecated flag. Used the recommended flag:
```bash
--use-node-agent
```

Final working command:
```bash
velero install   --provider aws   --plugins velero/velero-plugin-for-aws:v1.8.0   --bucket jcps-velero-backups   --backup-location-config region=eu-west-1   --snapshot-location-config region=eu-west-1   --namespace velero   --service-account-name velero   --no-secret   --wait
```

---

