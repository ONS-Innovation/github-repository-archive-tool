#! /bin/sh

# Retrieve the Github App secret from AWS Secret Manager
# and store the value in a file.
# If running the script on local dev use: --profile <aws_credential_profile> to 
# specify the credentials to use.
aws secretsmanager get-secret-value --secret-id "/sdp/tools/repoarchive/repo-archive-github.pem" --region eu-west-2 --query SecretString --output text > ./repo-archive-github.pem

# Start the application
poetry run python repoarchivetool/app.py