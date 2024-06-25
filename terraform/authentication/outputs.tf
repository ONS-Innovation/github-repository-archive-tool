output "github_audit_user_pool" {
  value = aws_cognito_user_pool.github_audit_user_pool.name
}

output "github_audit_user_pool_id" {
  value = aws_cognito_user_pool.github_audit_user_pool.id
}

output "github_audit_user_pool_arn" {

  value = aws_cognito_user_pool.github_audit_user_pool.arn

}

output "github_audit_user_pool_domain" {
  value = aws_cognito_user_pool_domain.main.domain
}

output "github_audit_user_pool_client" {
  value = aws_cognito_user_pool_client.userpool_client.name
}

output "github_audit_user_pool_client_id" {
  value = aws_cognito_user_pool_client.userpool_client.id
}
