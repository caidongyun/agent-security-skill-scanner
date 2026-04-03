# Business scenario: cloud
# Generated: 2026-04-02 10:47:53.106174

#!/bin/bash
# AWS 管理
aws s3 cp ./data s3://my-bucket/
aws ec2 describe-instances
aws lambda invoke --function-name myFunc output.json
echo "AWS 操作完成"
