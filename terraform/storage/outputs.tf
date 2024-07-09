output "github_audit_bucket_name" {
  value = aws_s3_bucket.github_audit_bucket.bucket
}
output "github_audit_bucket_id" {
  value = aws_s3_bucket.github_audit_bucket.id
}
