# S3 Application Configuration
# Note: The application stores objects in the bucket hence prevent_destroy = true
# If a terraform destroy is required then the bucket needs to be empty and the 
# terraform below changed to prevent_destroy = false
#
# Separating out the long term storage of the application from the service itself
# allows for the service to be destroyed and recreated without losing the data
resource "aws_s3_bucket" "github_audit_bucket" {
  bucket = "${var.domain}-${var.service_subdomain}-tool"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.github_audit_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "blocked" {
  bucket = aws_s3_bucket.github_audit_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encrypt_by_default" {
  bucket = aws_s3_bucket.github_audit_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
