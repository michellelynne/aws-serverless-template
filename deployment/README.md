Creating Deployment Pipeline
==============================================

This explains the steps to create an automatic ci/cd pipeline with multiple environments for your serverless app. 
It will automatically deploy when you update the branch. For example, merge code to staging, it will create a complete stand alone 
staging environment in a few minutes. 
 
It uses a variety of methods to demonstrate the different ways to use the services. Future plans include simplifying this into one step. 

## Services
* [GitHub](https://www.github.com)
* [IAM](https://console.aws.amazon.com/iam/home)
* [CodePipeline](https://console.aws.amazon.com/codesuite/codepipeline/home)
* [CodeBuild](https://console.aws.amazon.com/codesuite/codebuild/projects)
* [Cloudformation](https://console.aws.amazon.com/cloudformation/home)

### GitHub
Create an OAuth token and store it safely. [Instructions](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line)
Create a branch with the name of the environment you want to make, ie, qa, staging, etc.

### IAM

#### Role
Create a role that CodePipeline needs to deploy using the command line. The policy document is included.

[Using AWS CLI](https://aws.amazon.com/cli/)

```aws iam create-role --role-name code-pipeline-deploy --assume-role-policy-document 'file://deploy_assume_role_policy_document.json'```

Make sure to save the RoleArn for the pipeline

#### Policy

For the tutorial below, use [Creating Policies on the JSON Tab](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_create.html#access_policies_create-json-editor)

[Creating a Policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_create.html#access_policies_create-start)

[Policy to Use](https://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-custom-role.html)

[Attach Policy to Role](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html#add-policies-console)

### Code Pipeline

[Creating a Pipeline using CLI](https://docs.aws.amazon.com/cli/latest/reference/codepipeline/create-pipeline.html)

A template code pipeline is available at `code_pipeline.json`. Make sure to replace all the variables before deploying.

###### Variables
* $roleArn <(Arns)[https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html]> : The ARN from the Role previously created. 
* $github-name - Username on github, ie, michellelynne
* $github-repo - GitHub repo name, ie, aws-serverless-template
* $env - Environment name of the branch you created, ie qa, stagong, etc.
* $oauth_token - Personal access token you made before.