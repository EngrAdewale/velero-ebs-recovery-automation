#!/bin/bash

BUCKET_NAME="jcps-velero-backups"

echo "Checking if jq is installed..."
if ! command -v jq &> /dev/null; then
    echo "Installing jq..."
    sudo apt update && sudo apt install -y jq
fi

echo "Removing all versions and delete markers from S3 bucket: $BUCKET_NAME"

aws s3api list-object-versions --bucket $BUCKET_NAME --output json | jq -r '.Versions[]?, .DeleteMarkers[]? | "aws s3api delete-object --bucket $BUCKET_NAME --key \(.Key) --version-id \(.VersionId)"' | bash

echo "Deleting bucket..."
aws s3 rb s3://$BUCKET_NAME --force
