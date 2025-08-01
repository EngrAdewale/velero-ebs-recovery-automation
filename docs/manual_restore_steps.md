# Manual Restore Steps Before Automation

This document outlines the original manual process for recovering a Kubernetes application using Velero with EBS volume snapshots.

---

##  1. Create Namespace and Workload

```bash
kubectl create ns aee
kubectl apply -f etx-deployment.yaml
```

- PVC bound to AWS EBS
- Secret added manually
- Pod writes to `/data/hello.txt`

---

##  2. Backup with Velero

```bash
velero backup create aee-backup --include-namespaces aee --wait
```

---

##  3. Simulate Disaster

```bash
kubectl delete ns aee
```

---

##  4. Restore Backup

```bash
velero restore create aee-restore   --from-backup aee-backup   --namespace-mappings aee:aee-a   --wait
```

---

##  5. Validate Recovery

```bash
kubectl get pod -n aee-a
kubectl get pvc -n aee-a
kubectl get secret -n aee-a
kubectl exec -n aee-a etx-pod -- cat /data/hello.txt
```

---

##  Pain Points

- Human error during restore command
- Forgot `--namespace-mappings`
- Manual pod checks were time-consuming
