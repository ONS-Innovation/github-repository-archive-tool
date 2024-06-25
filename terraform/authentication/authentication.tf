# Cognito User Pool
# Use email for sign up and verification. Cognito identity provider is used for authentication.
# Define password complexity policy and email message templates.
resource "aws_cognito_user_pool" "github_audit_user_pool" {
  name = "${var.domain}-${var.service_subdomain}-user-pool"

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 10
  }


  deletion_protection      = "INACTIVE"
  auto_verified_attributes = ["email"]
  username_attributes      = ["email"]

  verification_message_template {
    default_email_option  = "CONFIRM_WITH_LINK"
    email_message_by_link = "Please click the link below to verify your email address with the ${var.service_subdomain} tool. {##Click Here##}"
  }

  admin_create_user_config {
    allow_admin_create_user_only = true

    invite_message_template {
      email_message = "You have been added as a user to the <a href='https://${local.service_url}/'>ONS Github Audit Tool</a><br>Your username is {username} and temporary password is <strong>{####}</strong>"
      email_subject = "Your access to the ${var.service_subdomain} tool"
      sms_message   = "Your username is {username} and temporary password is <strong>{####}</strong>"
    }
  }

  schema {
    name                     = "email"
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true # false for "sub"
    required                 = true # true for "sub"
    string_attribute_constraints {  # if it is a string
      min_length = 0                # 10 for "birthdate"
      max_length = 2048             # 10 for "birthdate"
    }
  }
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.service_subdomain}-${var.domain}"
  user_pool_id = aws_cognito_user_pool.github_audit_user_pool.id
}

resource "aws_cognito_user_pool_client" "userpool_client" {
  name                                 = "${var.service_subdomain}-client"
  user_pool_id                         = aws_cognito_user_pool.github_audit_user_pool.id
  callback_urls                        = ["https://${local.service_url}/oauth2/idpresponse"]
  allowed_oauth_flows_user_pool_client = true
  generate_secret                      = true
  prevent_user_existence_errors        = "ENABLED"
  explicit_auth_flows                  = ["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid"]
  supported_identity_providers         = ["COGNITO"]
}
