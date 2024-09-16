import boto3
import json
import zipfile
import io
from AwsDataResources import S3Manager
from utils.Logger import Logger
from configuration import lambda_config


class LambdaManagerEmployee:
    def __init__(self, function_name, role_name, lambda_client, iam_client, s3_client, logger):
        self._role_name = role_name
        self._function_name = function_name
        self.lambda_client = lambda_client
        self.iam_client = iam_client
        self.s3_client = s3_client
        self.logger = logger

    def create_lambda_role(self, role_name):
        try:
            assume_role_policy_document = json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })

            try:
                role = self.iam_client.get_role(RoleName=role_name)
                self.logger.info(f"Role {role_name} already exists, using the existing role.")
            except self.iam_client.exceptions.NoSuchEntityException:
                role = self.iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=assume_role_policy_document
                )
                self.logger.info(f"Created IAM role {role_name}")

            policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            self.iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

            s3_policy_arn = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
            self.iam_client.attach_role_policy(RoleName=role_name, PolicyArn=s3_policy_arn)

            return role['Role']['Arn']
        except Exception as e:
            self.logger.error(f"Error creating IAM role: {e}")
            raise

    def create_or_update_lambda_function(self, lambda_code,
                                         role_arn,
                                         bucket_name,
                                         zip_file_url,
                                         lambda_client_create_function_params: dict = lambda_config.LAMBDA_CLIENT_CREATE_FUNCTION):
        try:
            # Create a ZIP file with the Lambda function code
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as z:
                z.writestr('lambda_function.py', lambda_code)
            zip_buffer.seek(0)

            # Check if the Lambda function already exists
            try:
                self.lambda_client.get_function(FunctionName=self._function_name)
                self.logger.info(f"Function {self._function_name} already exists. Updating the function.")
                response = self.lambda_client.update_function_code(
                    FunctionName=self._function_name,
                    ZipFile=zip_buffer.read()
                )
            except self.lambda_client.exceptions.ResourceNotFoundException:
                self.logger.info(f"Function {self._function_name} does not exist. Creating a new function.")

                response = self.lambda_client.create_function(
                    FunctionName=self._function_name,
                    Role=role_arn,
                    Code={'ZipFile': zip_buffer.read()},
                    Environment={
                                    'Variables': {
                                        'DEST_BUCKET': bucket_name,
                                        'ZIP_FILE_URL': zip_file_url
                                    }
                                },
                    **lambda_client_create_function_params
                )

            self.logger.info(f"Created or updated Lambda function {self._function_name}")
            return response
        except Exception as e:
            self.logger.error(f"Error creating or updating Lambda function: {e}")
            raise

    def invoke_lambda_function(self):
        try:
            response = self.lambda_client.invoke(
                FunctionName=self._function_name,
                InvocationType='Event'
            )
            self.logger.info(f"Invoked Lambda function {self._function_name}")
            return response
        except Exception as e:
            self.logger.error(f"Error invoking Lambda function: {e}")
            raise

    def clean_up(self):
        try:
            self.lambda_client.delete_function(FunctionName=self._function_name)
            self.iam_client.detach_role_policy(RoleName=self._role_name,
                                               PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
            self.iam_client.detach_role_policy(RoleName=self._role_name,
                                               PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess')
            self.iam_client.delete_role(RoleName=self._role_name)
            self.logger.info(f"Cleaned up Lambda function and IAM role {self._role_name}")
        except Exception as e:
            self.logger.error(f"Error cleaning up resources: {e}")
            raise

    def deploy_lambda(self, lambda_code, role_name, bucket_name, zip_file_url, lambda_client_create_function_params):

        role_arn = self.create_lambda_role(role_name)
        # self.create_lambda_function(function_name, role_arn, bucket_name, zip_file_url)
        self.create_or_update_lambda_function(lambda_code=lambda_code,
                                              role_arn=role_arn,
                                              bucket_name=bucket_name,
                                              zip_file_url=zip_file_url,
                                              lambda_client_create_function_params=lambda_client_create_function_params)
        self.invoke_lambda_function()

#
# if __name__ == '__main__':
#     logger = Logger()  # Initialize logger
#
#     s3_resource = boto3.resource('s3')  # Initialize S3 resource
#     s3_client = boto3.client('s3')  # Initialize S3 client
#     lambda_client = boto3.client('lambda')  # Initialize Lambda client
#     iam_client = boto3.client('iam')  # Initialize IAM client
#     zip_file_url = 'https://ap-southeast-1-tcprod.s3.ap-southeast-1.amazonaws.com/courses/ILT-TF-100-TECESS/v5.5.8.prod-3b017a1e/lab-3/scripts/sample-photos.zip'
#
#     from configuration import s3_config  # Import S3 configuration
#
#     s3_manager = S3Manager(
#         s3=s3_resource,
#         s3_client=s3_client,
#         bucket_name=s3_config.S3_BUCKET_BASE_NAME,
#         region=s3_config.REGION,
#         logger=logger
#     )
#
#     lambda_manager = LambdaManagerEmployee(
#         lambda_client=lambda_client,
#         iam_client=iam_client,
#         s3_client=s3_client,
#         logger=logger
#     )
#
#     try:
#         s3_manager.setup()  # Setup S3 resources
#
#         # Deploy Lambda function with source and destination buckets
#         # source_bucket = 'https://ap-southeast-1-tcprod.s3.ap-southeast-1.amazonaws.com/courses/ILT-TF-100-TECESS/v5.5.8.prod-3b017a1e/lab-3/scripts/sample-photos.zip'
#         source_bucket = "ap-southeast-1-tcprod"  # Source bucket from the URL
#         lambda_manager.deploy_lambda(bucket_name=s3_manager.bucket_dns_name, zip_file_url=zip_file_url)
#     except Exception as e:
#         logger.debug(e)  # Log any errors that occur
#     finally:
#         s3_manager.clean_resources()  # Clean up S3 resources
#         # lambda_manager.clean_resources()  # Clean up Lambda resources
