# resourceCreationDemo

**Objective**: Create an API based on AWS services that can create a VPC with multiple subnets and store the results. The API should be able to retrieve the data of created resources from the API. The code is written in Python. The API should be protected with an authentication layer and Authorization should be open to all authenticated users. 


Project Overview
This project demonstrates the creation of an API Gateway integrated with an AWS Lambda function that interacts with a DynamoDB table. The API allows users to create and store VPC and subnet details dynamically in a DynamoDB. The infrastructure is defined using an AWS CloudFormation template.

Key Features:
    API Gateway: Exposes endpoints for invoking the Lambda function.
    Lambda Function: Handles logic for creating VPCs and subnets dynamically and storing details in DynamoDB
    DynamoDB: Database for storing VPC and subnet records.
    CloudFormation: Automates the setup to create required resources using an Infrastructure-as-Code approach.

Project Files:
1. cloudFormationTemplate/cloudformation_temp.yml:
    The CloudFormation template defining all AWS resources.
2. LambdaFunctionCode/lambda_function.py:
    Lambda function code for VPC and subnet creation.
    Lambda function code to fetch VPC and subnet details.
3. post_method_payload.json:
    Payload to create VPC and subnets.
4. README.md:
    Documentation for the project.

Project Deployment Instructions:
    1. Upload the cloudformation_temp.yml file and the lambda_function.zip file to the S3 bucket.
    2. Update the bucket name and key in the CloudFormation template under the Lambda function resource.
    3. Create a CloudFormation stack, reference the S3 URL of the cloudformation_temp.yml file or upload file, and deploy API Gateway, lambda Func and dynamoDB through the CFT.
    4. Create a Cognito User Pool and configure the following:
        a. Add an App Client.
        b. Navigate to Login Pages, select Implicit Grant. Save the configuration.
    6. Create an Authorizer in API Gateway and test it by generating a new token using Cognito (ID token).
        Login page: App Client -> Login Pages -> Create new username & verify email.
    7. Configure Cognito in the Method Requests and deploy the API again.
    8. Use the access token for API authentication by adding it to the request header while triggering the API.
    9. Attached post_method_payload.json file is a body for POST request.
