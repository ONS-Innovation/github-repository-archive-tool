# GitHub Repository Archive Tool

A Python Flask application to archive outdated organisation repositories.

## Prerequisites

This project uses poetry for package management, colima a license free tool for containerisation, the AWS cli commands for interacting with cloud services and Terraform for deploying changes.

It is expected you have these tools installed before progressing further.

[Instructions to install Poetry](https://python-poetry.org/docs/)

[Instructions to install Colima](https://github.com/abiosoft/colima/blob/main/README.md)

[Instructions to install AWS cli tool](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

[Terraform to configure AWS](https://developer.hashicorp.com/terraform/install)

See the section on deployment for specific requirements and prerequisites to deploy to AWS.

## Documentation

This project uses MkDocs for documentation which gets deployed to GitHub Pages at a repository level.

For more information about MkDocs, see the below documentation.

[Getting Started with MkDocs](https://www.mkdocs.org/getting-started/)

There is a guide to getting started on this repository's GitHub Pages site.

## Setup - Run outside of Docker

Prior to running outside of Docker ensure you have the necessary environment variables setup locally where you are running the application. E.g in linux or OSX you can run the following, providing appropriate values for the variables:

```bash
export AWS_ACCESS_KEY_ID=MYACCESSKEYID
export AWS_SECRET_ACCESS_KEY=MYSECRETACCESSKEY
export AWS_DEFAULT_REGION=eu-west-2
export AWS_SECRET_NAME=<aws_secret_name>
export GITHUB_ORG=ONS-Innovation
export GITHUB_APP_CLIENT_ID=<github_app_client_id>
export AWS_ACCOUNT_NAME=sdp-sandbox
```

1. Navigate into the project's folder and create a virtual environment

    ```bash
    python3 -m venv <environment_name>
    ```

2. Activate the environment

    ```bash
    source <environment_name>/bin/activate
    ```

3. Install the required dependencies

    ```bash
    make install
    ```

4. Get the repo-archive-github.pem file and copy to the source code root directory (see "Getting a .pem file" below).

5. When running the project locally, you need to edit `get_s3_client()` within `storage_interface.py`.

    When creating an instance of `boto3.session()`, you must pass which AWS credential profile to use, as found in `~/.aws/credentials`.

    When running locally:

    ```python
    session = boto3.Session(profile_name="<profile_name>")
    s3 = session.client("s3")
    ```

    When running from a container:

    ```python
    session = boto3.Session()
    s3 = session.client("s3")
    ```

6. Run the project

    ```bash
    poetry run python3 repoarchivetool/app.py
    ```

## Building a docker image

Build and tag the image

```bash
docker build -t repo-archive-tool .
```

Check the image is available locally

```bash
docker images
```

Example output:

```bash
REPOSITORY                                                      TAG       IMAGE ID       CREATED          SIZE
repo-archive-tool                                               latest    d9c802cef7eb   11 seconds ago   332MB
```

Run the image locally mapping local host port (5000) to container port (5000) and passing in AWS credentials to download a .pem file from the AWS Secrets Manager to the running container.

The credentials used in the below command are for a user in AWS that has permissions to retrieve secrets from AWS Secrets Manager.

```bash
docker run -p 5000:5000 \                
-e AWS_ACCESS_KEY_ID=<aws_access_key_id> \
-e AWS_SECRET_ACCESS_KEY=<aws_secret_access_key_id> \
-e AWS_DEFAULT_REGION=eu-west-2 \
-e AWS_SECRET_NAME=<aws_secret_name> \
-e GITHUB_ORG=ONS-Innovation \
-e GITHUB_APP_CLIENT_ID=<github_app_client_id> \
-e AWS_ACCOUNT_NAME=sdp-sandbox
repo-archive-tool
```

To check the container is running

```bash
docker ps 
```

Example output

```bash
CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS          PORTS                                       NAMES
e85a3ce5fecf   repo-archive-tool   "/app/start_repo_too…"   27 seconds ago   Up 25 seconds   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   cranky_yalow
```

To view the running application in a browser navigate to

```bash
Running on http://127.0.0.1:5000
```

To stop the running container either use the container ID:

```bash
docker stop e85a3ce5fecf
```

or the container name

```bash
docker stop cranky_yalow
```

## Storing the container on AWS Elastic Container Registry (ECR)

When you make changes to the application a new container image must be pushed to ECR.

These instructions assume:

1. You have a repository set up in your AWS account named sdp-repo-archive.
2. You have created an AWS IAM user with permissions to read/write to ECR (e.g AmazonEC2ContainerRegistryFullAccess policy) and that you have created the necessary access keys for this user.  The credentials for this user are stored in ~/.aws/credentials and can be used by accessing --profile <aws-credentials-profile\>, if these are the only credentials in your file then the profile name is _default_

You can find the AWS repo push commands under your repository in ECR by selecting the "View Push Commands" button.  This will display a guide to the following (replace <aws-credentials-profile\>, <aws-account-id\> and <version\> accordingly):

1. Get an authentication token and authenticate your docker client for pushing images to ECR:

    ```bash
    aws ecr --profile <aws-credentials-profile> get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.eu-west-2.amazonaws.com
    ```

2. Tag your latest built docker image for ECR (assumes you have run _docker build -t sdp-repo-archive ._ locally first)

    ```bash
    docker tag sdp-repo-archive:latest <aws-account-id>.dkr.ecr.eu-west-2.amazonaws.com/sdp-repo-archive:<version>
    ```

    **Note:** To find the <version\> to build look at the latest tagged version in ECR and increment appropriately

3. Push the version up to ECR

    ```bash
    docker push <aws-account-id>.dkr.ecr.eu-west-2.amazonaws.com/sdp-repo-archive:<version>
    ```

## Deployment to AWS

The deployment of the service is defined in Infrastructure as Code (IaC) using Terraform.  The service is deployed as a container on an AWS Fargate Service Cluster.

### Deployment Prerequisites

When first deploying the service to AWS the following prerequisites are expected to be in place or added.

#### Underlying AWS Infrastructure

The Terraform in this repository expects that underlying AWS infrastructure is present in AWS to deploy on top of, i.e:

- Route53 DNS Records
- Web Application Firewall and appropriate Rules and Rule Groups
- Virtual Private Cloud with Private and Public Subnets
- Security Groups
- Application Load Balancer
- ECS Service Cluster

That infrastructure is defined in the repository [sdp-infrastructure](https://github.com/ONS-Innovation/sdp-infrastructure)

#### Bootstrap IAM User Groups, Users and an ECSTaskExecutionRole

The following users must be provisioned in AWS IAM:

- ecr-user
  - Used for interaction with the Elastic Container Registry from AWS cli
- ecs-app-user
  - Used for terraform staging of the resources required to deploy the service

The following groups and permissions must be defined and applied to the above users:

- ecr-user-group
  - EC2 Container Registry Access
- ecs-application-user-group
  - Cognito Power User
  - Dynamo DB Access
  - EC2 Access
  - ECS Access
  - ECS Task Execution Role Policy
  - Route53 Access
  - S3 Access
  - Cloudwatch Logs All Access (Custom Policy)
  - IAM Access
  - Secrets Manager Access

Further to the above an IAM Role must be defined to allow ECS tasks to be executed:

- ecsTaskExecutionRole
  - See the [AWS guide to create the task execution role policy](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html)

#### Bootstrap for Terraform

To store the state and implement a state locking mechanism for the service resources a Terraform backend is deployed in AWS (an S3 object and DynamoDbTable).  Details can be found in the infrastructure repository above.

#### Bootstrap for Secrets Manager

The Github Audit and Repo service requires access to an associated Github App secret, this secret is created when the Github App is installed in the appropriate Github Organisation.  The contents of the generated pem file is stored in the AWS Secret Manager and retrieved by this service to interact with Github securely.

AWS Secret Manager must be set up with a secret:

- /sdp/tools/repoarchive/repo-archive-github.pem
  - A plaintext secret, containing the contents of the .pem file created when a Github App was installed.

#### Running the Terraform

There are associated README files in each of the Terraform modules in this repository.  When first staging the service Terraform must be run in the following order:

- terraform/storage/main.tf
  - This provisions the persistent storage used by the service.
- terraform/authentication/main.tf
  - This provisions the Cognito authentication used by the service.
- terraform/service/main.tf
  - This provisions the resources required to launch the service.

The reasoning behind splitting the terraform into separate areas is to allow a more flexible update of the application without the need to re-stage authentication or persistent storage.

Depending upon which environment you are deploying to you will want to run your terraform by pointing at an appropriate environment tfvars file.  

Example service tfvars file:
[service/env/sandbox/example_tfvars.txt](https://github.com/ONS-Innovation/code-repo-archive-tool/terraform/service/env/sandbox/example_tfvars.txt)

Example authentication tfvars file:
[authentication/env/sandbox/example_tfvars.txt](https://github.com/ONS-Innovation/code-repo-archive-tool/terraform/authentication/env/sandbox/example_tfvars.txt)

Example storage tfvars file:
[storage/env/sandbox/example_tfvars.txt](https://github.com/ONS-Innovation/code-repo-archive-tool/terraform/storage/env/sandbox/example_tfvars.txt)

#### Provision Users

When the service is first deployed an admin user must be created in the Cognito User Pool that was created when the authentication terraform was applied.

New users are manually provisioned in the AWS Console:

- Navigate to Cognito->User Pools and select the pool created for the service
- Under the Users section select _Create User_ and choose the following:
  - _Send an email invitation_
  - Enter the _ONS email address_ for the user to be added
  - Select _Mark email address as verified_
  - Under _Temporary password_ choose:
    - Generate a password
  - Select _Create User_

An email invite will be sent to the selected email address along with a one-time password which is valid for 10 days.

### Updating the running service using Terraform

If the application has been modified and the changes do not require the Cognito authentication or S3 store to be removed and re-staged (i.e _most_ application level changes) then the following can be performed:

- Build a new version of the container image and upload to ECR as per the instructions earlier in this guide.
- Change directory to the **service terraform**

  ```bash
  cd terraform/service
  ```

- In the appropriate environment variable file env/sandbox/sandbox.tfvars, env/dev/dev.tfvars or env/prod/prod.tfvars
  - Change the _container_ver_ variable to the new version of your container.
  - Change the _force_deployment_ variable to _true_.

- Initialise terraform for the appropriate environment config file _backend-dev.tfbackend_ or _backend-prod.tfbackend_ run:

  ```bash
  terraform init -backend-config=env/dev/backend-dev.tfbackend -reconfigure
  ```

  The reconfigure options ensures that the backend state is reconfigured to point to the appropriate S3 bucket.

  **_Please Note:_** This step requires an **AWS_ACCESS_KEY_ID** and **AWS_SECRET_ACCESS_KEY** to be loaded into the environment if not already in place.
  This can be done using:

  ```bash
  export AWS_ACCESS_KEY_ID="<aws_access_key_id>"
  export AWS_SECRET_ACCESS_KEY="<aws_secret_access_key>"
  ```

- Refresh the local state to ensure it is in sync with the backend

  ```bash
  terraform refresh -var-file=env/dev/dev.tfvars
  ```

- Plan the changes, ensuring you use the correct environment config (depending upon which env you are configuring):

  E.g. for the dev environment run

  ```bash
  terraform plan -var-file=env/dev/dev.tfvars
  ```

- Apply the changes, ensuring you use the correct environment config (depending upon which env you are configuring):

  E.g. for the dev environment run

  ```bash
  terraform apply -var-file=env/dev/dev.tfvars
  ```

- When the terraform has applied successfully the running task will have been replaced by a task running the container version you specified in the tfvars file

## Destroying Service Resources

The resources for the service are applied using separate terraform for the main service, storage and authentication.  

### Destroy Only the Main Service Resources

The separation of the terraform enables the main service to be destroyed independent of the storage and authentication.  This allows any data to persist and means the user list for the application does not have to be reconstructed.

- Delete the service resources by running the following ensuring your reference the correct environment files for the backend-config and var files:

  ```bash
  cd terraform/service

  terraform init -backend-config=env/dev/backend-dev.tfbackend -reconfigure

  terraform refresh -var-file=env/dev/dev.tfvars

  terraform destroy -var-file=env/dev/dev.tfvars
  ```

### Destroy All of the Service Resources

To destroy all resources the destroy **must happen in the following order, storage, service and finally authentication** :

- Ensure that all data can be deleted in S3 and if so, _manually delete any objects_ and the _versioned objects_ in S3.

- Update the lifecycle rule in the storage.tf to prevent_destroy=false.  This is a temporary change whilst resources are destroyed and must be reverted once complete.

- Delete the storage resources by running the following ensuring your reference the correct environment files for the backend-config and var files:
  
  ```bash
  cd terraform/storage

  terraform init -backend-config=env/dev/backend-dev.tfbackend -reconfigure

  terraform refresh -var-file=env/dev/dev.tfvars

  terraform destroy -var-file=env/dev/dev.tfvars
  ```

- Delete the service resources by running the following ensuring your reference the correct environment files for the backend-config and var files:

  ```bash
  cd terraform/service

  terraform init -backend-config=env/dev/backend-dev.tfbackend -reconfigure

  terraform refresh -var-file=env/dev/dev.tfvars

  terraform destroy -var-file=env/dev/dev.tfvars
  ```

- Delete the authentication resources by running the following ensuring your reference the correct environment files for the backend-config and var files:

  ```bash
  cd terraform/authentication

  terraform init -backend-config=env/dev/backend-dev.tfbackend -reconfigure

  terraform refresh -var-file=env/dev/dev.tfvars

  terraform destroy -var-file=env/dev/dev.tfvars
  ```

## Linting and Formatting
To view all commands
```bash
make all
```

Before you can use any linting tools, you must have the dev dependencies installed
```bash
make install-dev
```

To clean residue files
```bash
make clean
```

To format your code
```bash
make format
```

To run all linting tools
```bash
make lint
```

To run a specific linter (black, ruff, pylint)
```bash
make black
make ruff
make pylint
```

To run mypy (static type checking)
```bash
make mypy
```