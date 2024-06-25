# Create a service running on fargate with a task definition and service definition
terraform {
  backend "s3" {
    bucket         = "sdp-dev-tf-state"
    key            = "sdp-dev-ecs-github-audit-auth/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "terraform-state-lock"
  }

}
