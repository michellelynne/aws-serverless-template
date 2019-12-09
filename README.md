# Description 

This project is designed to show examples of how to use various features with AWS serverless.
Feel free to add issues if you have any questions or are looking for services not documented yet.


```bash
.
├── README.md                         <-- This instructions file
├── items_buildspec.yml               <-- CodeBuild specifications for CI/CD
├── items_template.yaml               <-- SAM Template
├── deploy_service_policy.json        <-- IAM Policy for a role to deploy service.
├── items                             <-- Source code for a lambda function
│   ├── __init__.py
│   ├── app.py                        <-- Lambda function code
│   ├── requirements-dev.txt          <-- Requirements for local env.
│   ├── requirements.txt              <-- Requirements for deploy
│   ├── items_open_api.yaml           <-- Swagger/OpenAPI specifications
└── tests                             <-- Unit tests
    └── items
        ├── __init__.py
        └── test_items.py
```

## Local Environment

### Create virtualenv and install requirements

* [Python 3 installed](https://www.python.org/downloads/)

```bash
virtualenv -p python3 items-venv
source items-venv/bin/activate
pip install -r items/requirements-dev.txt
```

### Run unit tests

```bash
pytest tests
```

## Deploy to AWS

If not already setup, create a new AWS account. This will house all the environments. 
It is never possible to automate every step of a new project because AWS needs to be told where the code is.
These will only need to be done once. Here are the manual steps.

```bash
Create an AWS account. Connect the AWS Account to this GitHub repository.
``` 

## Setup Config

After the new AWS account is created, in order to deploy, you need an account with appropriate permissions.
Once you have it, create these config files on your local machine. In this example I use the test account name "personal", but it can have any name.
Before running any AWS commands to set the profile in the terminal. 

```bash
~/.aws/config
[personal]
region=us-east-1
output=json

~/.aws/credentials 
[personal]
aws_access_key_id=$KEY
aws_secret_access_key=$SECRET

export AWS_PROFILE=personal
``` 


## CodeBuild Project

### Create Policy

**Save the ARN from this output to attach to the role.**

```bash
aws iam create-policy --policy-name templates-items-deploy --policy-document file://deploy_service_policy.json
```


### Create Role

**Save the ARN from this output to attach to the build.**


```bash
aws iam create-role --role-name templates-items-deploy --assume-role-policy-document file://code_build_trust_policy.json
```


### Attach Policy to Role


```bash
aws iam attach-role-policy --policy-arn $ARN, --role-name templates-items-deploy
```

### Create CodeBuild


aws codebuild create-project --cli-input-json file://code_build_create_project.json --service-role $ARN

### Create Build using CodeBuild
 
Make sure to use the correct json for environment you want to build.

--environment-variables-override controls the environment. If you want to create an ad-hoc environment,
create a new json environment_variables file. This is useful for standing up personal environments for testing.

--source-version controls the source branch. In this example it uses master, but you can use any branch name. 

```bash
aws codebuild start-build --project-name templates-items --environment-variables-override file://environment_variables/dev.json --source-version master
```

#### After Build Tasks

#### Upload Secrets
A secrets manager secret was created to hold all the secrets for each env. 
Pull any needed secrets and update the secret. 

```bash
aws secretsmanager update-secret --secret-id "templates/items/$ENV" --secret-string '{"a_secret":"UPDATE_ME"}'
```
#### Get API Keys

In order to access the created API, you will need an API key. One has been automatically been generated for each environment.
It is not set to expire or rotate. It currently has a usage plan of 1/second.
It is created via the included template, so if any features need to change, please change it there.

First get a list of keys:

```bash
aws apigateway get-api-keys
```

Then find the key labeled "ItemsAPIKey". Grab the id and use it to get the actual key value:

```bash
aws apigateway get-api-key --api-key $ID --include-value
```

Now make sure to securely store that key. 

#### Integration Tests

To test the API, you need the endpoint url. In this example I have filled in the stack and API names, but any can be entered.

```bash
aws cloudformation describe-stacks --stack-name templates-items --query 'Stacks[].Outputs[?OutputKey==`ItemsApi`]' --output table
``` 

### TODOs

* Domain forwarding
* Tests
* Swagger 3.0
* Create an endpoint that gets from 3rd party service and saves encrypted to database
* Add Sentry

#### Create Build Manually

Here's the commands to test manually without Code Build

```bash
# Deploy
# Create S3 bucket
aws s3 mb s3://templates-items-$NAME

# Build requirements into directory.
sam build --template items_template.yaml --build-dir .aws-sam/build

# Package Lambda function defined locally and upload to S3 as an artifact
sam package --output-template-file packaged.yaml --s3-bucket $BUCKET-NAME

# Deploy SAM template as a CloudFormation stack
#Includes example of parameter overrides, but not necessary. Space separated. 
sam deploy  --template-file packaged.yaml --stack-name $BUCKET-NAME --capabilities CAPABILITY_IAM --parameter-overrides Stage=$NAME
```

Here's how to test CodeBuild locally, but it's not great. Highly recommend using AWS instead.

```bash
# Test Code Build Locally
cd aws-codebuild-docker-images/ubuntu/standard/2.0/
docker build -t aws/codebuild/standard:2.0 .
codebuild_build.sh -i aws/codebuild/standard:2.0 -a /templates-items/artifacts -s /templates-items/
```

#### Troubleshooting

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called sam logs. sam logs lets you fetch logs generated by your Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
sam logs -n ItemsFunction --stack-name templates-items --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Cleanup

In order to delete our Serverless Application recently deployed you can use the following AWS CLI Command:

```bash
aws cloudformation delete-stack --stack-name templates-items
```

### Local API to run integration tests.

This currently does not work because SAM local does not recognize the external Swagger/OpenAPI file.
Leaving this documentation in if they decide to make the change. If this needs to work,
you can more the api info inline to the SAM template. This is also dangerous because it
uses the live AWS tools instead of local versions.  For testing I recommend instead
spinning up a new environment in AWS and testing via Postman or cURL. Instructions for that under Deploy to AWS.

* [Docker installed](https://www.docker.com/community-edition)

```bash
sam build --template items_template.yaml --build-dir .aws-sam/build
sam local start-api
```