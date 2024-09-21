import time

import boto3
import json
import zipfile
import io

from botocore.exceptions import ClientError

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

            # Wait until the role is fully propagated
            self.wait_for_role(role_name)

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

            # Wait until the Lambda function is active
            self.wait_for_lambda_active()

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

    def wait_for_role(self, role_name, timeout=60, interval=5):
        """Wait until the IAM role is available."""
        start_time = time.time()
        while True:
            try:
                self.iam_client.get_role(RoleName=role_name)
                self.logger.info(f"IAM role {role_name} is now available.")
                break
            except self.iam_client.exceptions.NoSuchEntityException:
                if time.time() - start_time > timeout:
                    self.logger.error(f"Timeout waiting for IAM role {role_name} to become available.")
                    raise
                self.logger.debug(f"Waiting for IAM role {role_name} to become available...")
                time.sleep(interval)
            except ClientError as e:
                self.logger.error(f"Unexpected error while waiting for IAM role: {e}")
                raise

    def wait_for_lambda_active(self, timeout=60, interval=5):
        """Wait until the Lambda function is in Active state."""
        start_time = time.time()
        while True:
            try:
                response = self.lambda_client.get_function(FunctionName=self._function_name)
                state = response['Configuration']['State']
                if state == 'Active':
                    self.logger.info(f"Lambda function {self._function_name} is now active.")
                    break
                else:
                    if time.time() - start_time > timeout:
                        self.logger.error(
                            f"Timeout waiting for Lambda function {self._function_name} to become active.")
                        raise TimeoutError(
                            f"Lambda function {self._function_name} did not become active within {timeout} seconds.")
                    self.logger.debug(f"Lambda function {self._function_name} is in state {state}. Waiting...")
                    time.sleep(interval)
            except self.lambda_client.exceptions.ResourceNotFoundException:
                if time.time() - start_time > timeout:
                    self.logger.error(f"Timeout waiting for Lambda function {self._function_name} to become available.")
                    raise
                self.logger.debug(f"Lambda function {self._function_name} not found. Waiting...")
                time.sleep(interval)
            except ClientError as e:
                self.logger.error(f"Unexpected error while waiting for Lambda function: {e}")
                raise