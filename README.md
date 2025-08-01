# Velero EBS Recovery Automation

This repository contains an end-to-end disaster recovery simulation using **Velero**, **AWS EBS**, **IRSA**, and a custom **Python automation script** for Kubernetes-based applications.

## 🔧 Components

- **EKS cluster** created with `eksctl`
- **IRSA-based Velero deployment** with S3 and EBS support
- **Automated restore script** to eliminate manual operator error
- **S3 cleanup tools** for versioned bucket deletion
- **Docs** covering errors, manual recovery, and automation validation

## 📁 Structure

```
.
├── automation/
│   └── velero_restore_automation.py         # Python script to automate restore and validate recovery
├── scripts/
│   └── delete_versioned_s3_bucket.sh        # Cleanup script for S3 buckets with versioning enabled
├── manifests/
│   └── velero-policy.json                   # IAM policy for Velero access
├── docs/
│   ├── EBS_Disaster_Recovery_Automation_Playbook.docx
│   ├── manual_restore_steps.md
│   └── errors_and_fixes.md
├── README.md
```

## ▶️ Getting Started

1. Clone the repo:
```bash
git clone git@github.com:<your-username>/velero-ebs-recovery-automation.git
```

2. Restore a backup with validation:
```bash
python3 automation/velero_restore_automation.py --backup aee-backup --from-ns aee --to-ns aee-a
```

## 📄 Documentation

- `manual_restore_steps.md`: Initial manual steps before automation
- `errors_and_fixes.md`: Every error encountered and how it was solved
- `EBS_Disaster_Recovery_Automation_Playbook.docx`: Full professional DR playbook

## 🧼 Cleanup

Use `scripts/delete_versioned_s3_bucket.sh` to clean versioned S3 buckets after testing.

---

## 🤝 Contributions

PRs are welcome. Please submit fixes, enhancements, or new DR scripts!


