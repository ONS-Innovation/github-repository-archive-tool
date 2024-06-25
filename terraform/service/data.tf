# Get the ecs infrastructure outputs from the remote state data source
data "terraform_remote_state" "ecs_infrastructure" {
  backend = "s3"
  config = {
    bucket = "sdp-dev-tf-state"
    key    = "sdp-dev-ecs-infra/terraform.tfstate"
    region = "eu-west-2"
  }
}

data "terraform_remote_state" "ecs_auth" {
  backend = "s3"
  config = {
    bucket = "sdp-dev-tf-state"
    key    = "sdp-dev-ecs-github-audit-auth/terraform.tfstate"
    region = "eu-west-2"
  }
}


data "aws_route53_zone" "route53_domain" {
  name = local.url
}


