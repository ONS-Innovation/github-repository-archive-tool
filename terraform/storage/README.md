# Storage Terraform

This terraform must be run to provision the S3 bucket store required for the Github Audit Tool.

The IaC is separated from the service terraform so that the file store can persist if the service is destroyed.  This gives greater flexibility, e.g allowing the service to be destroyed to save costs without losing the data that has been output by the tool.

It also acts as a nice fire break between someone accidentally destroying the S3 buckets.

## Prerequisites

The store is bootstrapped with a separate terraform state key so that S3 and Service state files are separated.

## Apply the Terraform

The S3 bucket must exist before a user tries to use the service. Ideally this terraform would be run first, ahead of the service terraform.

```bash
cd terraform/storage 

terraform init -backend-config=env/prod/backend-prod.tfbackend -reconfigure

terraform validate

terraform plan -var-file=env/prod/prod.tfvars

terraform apply -var-file=env/prod/prod.tfvars
```

## Resources

The IaC creates an S3 bucket called **_aws-env-name_-_service-name_-tool**, e.g sdp-dev-github-audit-tool
