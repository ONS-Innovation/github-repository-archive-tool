# Authentication Terraform

This terraform must be run to provision the Cognito authentication required for the Github Audit Tool.

The IaC is separated from the main service terraform so that the user information can persist if the service is destroyed.  This gives greater flexibility, e.g allowing the service to be destroyed to save costs without losing the user data associated with the tool.

It also acts as a nice fire break between someone accidentally destroying the user resources.

Once the terraform is applied then a user must be manually provisioned using the AWS console.

## Prerequisites

The authentication resource is bootstrapped with a separate terraform state key so that authentication, S3 and Service state files are separated.

## Apply the Terraform

The Cognito user resources must exist before a user tries to use the service. Ideally this terraform would be run ahead of the service terraform.

```bash
cd terraform/authentication 

terraform init -backend-config=env/prod/backend-prod.tfbackend -reconfigure

terraform refresh -var-file=env/prod/prod.tfvars

terraform validate

terraform plan -var-file=env/prod/prod.tfvars

terraform apply -var-file=env/prod/prod.tfvars
```

## Resources

The IaC creates the following resources:

- Cognito user pool
- Cognito user pool domain
- Cognito user pool management

## Additional setup

This terraform only create the Cognito resources, the **provisioning (and deprovisioning) of users is handled manually in the AWS console**, see the top level README for details.
