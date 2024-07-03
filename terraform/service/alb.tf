# Update the Application Load Balancer to forward appropriate requests
# to the backend service running in ECS Fargate.
# Create target group, used by ALB to forward requests to ECS service
resource "aws_lb_target_group" "github_audit_fargate_tg" {
  name        = "${var.service_subdomain}-fargate-tg"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.terraform_remote_state.ecs_infrastructure.outputs.vpc_id
}

# Get the highest priority of the existing listener rules
resource "null_resource" "get_highest_priority" {
  provisioner "local-exec" {
    command = <<EOT
aws elbv2 describe-rules --region ${var.region} --listener-arn ${data.terraform_remote_state.ecs_infrastructure.outputs.application_lb_https_listener_arn} --query 'Rules[*].Priority' --output json | jq '[.[] | select(test("^[0-9]+$")) | tonumber] | max' > highest_alb_listener_priority.txt
EOT
  }

  # Ensure the highest priority is retrieved on each apply
  triggers = {
    always_run = "${timestamp()}"
  }
}

data "local_file" "highest_priority" {
  depends_on = [null_resource.get_highest_priority]
  filename   = "highest_alb_listener_priority.txt"
}

locals {
  highest_priority = jsondecode(data.local_file.highest_priority.content)
}

# Create a listener rule to forward requests to the target group ensuring the 
# priority takes into account the existing rules 
resource "aws_lb_listener_rule" "github_audit_listener_rule" {
  listener_arn = data.terraform_remote_state.ecs_infrastructure.outputs.application_lb_https_listener_arn
  priority = local.highest_priority + 1

  condition {
    host_header {
      values = ["${local.service_url}"]
    }
  }

  action {
    type = "authenticate-cognito"

    authenticate_cognito {
      user_pool_arn       = data.terraform_remote_state.ecs_auth.outputs.github_audit_user_pool_arn
      user_pool_client_id = data.terraform_remote_state.ecs_auth.outputs.github_audit_user_pool_client_id
      user_pool_domain    = data.terraform_remote_state.ecs_auth.outputs.github_audit_user_pool_domain
    }
  }

  action {
    target_group_arn = aws_lb_target_group.github_audit_fargate_tg.arn
    type             = "forward"
  }
}

# Create a listener rule to forward requests to the target group
resource "aws_lb_listener_rule" "success_rule" {
  listener_arn = data.terraform_remote_state.ecs_infrastructure.outputs.application_lb_https_listener_arn
  priority     = local.highest_priority + 2

  condition {
    host_header {
      values = ["${local.service_url}"]
    }
  }

  condition {
    path_pattern {
      values = ["/success"]
    }
  }

  action {
    target_group_arn = aws_lb_target_group.github_audit_fargate_tg.arn
    type             = "forward"
  }
}

# Create a listener rule to forward requests to the target group
resource "aws_lb_listener_rule" "exempt_rule" {
  listener_arn = data.terraform_remote_state.ecs_infrastructure.outputs.application_lb_https_listener_arn
  priority     = local.highest_priority + 3

  condition {
    host_header {
      values = ["${local.service_url}"]
    }
  }

  condition {
    path_pattern {
      values = ["*set_exempt_date*"]
    }
  }

  action {
    target_group_arn = aws_lb_target_group.github_audit_fargate_tg.arn
    type             = "forward"
  }
}
