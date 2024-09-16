import base64
import os
from botocore.exceptions import ClientError

import configuration.ec2_config
from configuration.ec2_config import KEY_PAIR_NAME as KEY_NAME


class LaunchTemplateManager:
    def __init__(self, ec2_client, name, region, logger):
        self._key_pair_name = None
        self._name = name
        self._region = region
        self._response = None
        self._client = ec2_client
        self._logger = logger

    @property
    def id(self):
        if not self._response:
            raise ValueError('Trying accesse id while self._response.id=None')

        return self._response['LaunchTemplate']['LaunchTemplateId']

    @staticmethod
    def lunch_template_script_stress(s3_bucket_name: str, region: str) -> str:
        script = f"""#!/bin/bash -ex

# Update yum
yum -y update

#Install nodejs
yum -y install nodejs

#Install stress tool (for load balancing testing)
yum -y install stress

# Create a dedicated directory for the application
mkdir -p /var/app

# Get the app from Amazon S3
wget https://aws-tc-largeobjects.s3-us-west-2.amazonaws.com/ILT-TF-100-TECESS-5/app/app.zip

# Extract it into a desired folder
unzip app.zip -d /var/app/
cd /var/app/

# Configure S3 bucket details
export PHOTOS_BUCKET={s3_bucket_name}

# Configure default AWS Region
export DEFAULT_AWS_REGION={region}

# Enable admin tools for stress testing
export SHOW_ADMIN_TOOLS=1

# Install dependencies
npm install

# Start your app
npm start
"""
        return script

    def create_launch_template(self,
                               iam_role: str,
                               user_data_script: str,
                               image_id: str,
                               instance_type: str,
                               security_group_id: list[str],
                               ):
        try:
            # Step 1: Check if the launch template exists
            if self.launch_template_exists():
                self._response = self.load_existing_launch_template()
                if configuration.ec2_config.recreate_template:
                    self.delete_launch_template()
                else:
                    return

            # Step 2: Create a new key pair if needed
            if configuration.ec2_config.create_new_key_pair:
                self.create_key_pair(KEY_NAME)

            # Step 3: Create the launch template
            self._response = self._create_new_launch_template(iam_role, user_data_script, image_id, instance_type,
                                                        security_group_id)
            self._logger.info(f"Launch Template created, ID: {self._response['LaunchTemplate']['LaunchTemplateId']}")

        except ClientError as e:
            self._logger.error(f"Failed to create Launch Template {self._name}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error creating Launch Template {self._name}: {e}")
            raise

    def launch_template_exists(self) -> bool:
        """Check if the launch template exists."""
        try:
            existing_template = self._client.describe_launch_templates(
                LaunchTemplateNames=[self._name]
            )
            if existing_template['LaunchTemplates']:
                self._logger.info(f"Launch template {self._name} already exists.")
                return True
        except self._client.exceptions.ClientError:
            self._logger.info(f"Launch template {self._name} does not exist.")
        return False

    def load_existing_launch_template(self) -> dict:
        """Load an existing launch template if it exists."""
        self._logger.info(f"Loading existing launch template {self._name}.")
        existing_template = self._client.describe_launch_templates(
            LaunchTemplateNames=[self._name]
        )
        response = {'LaunchTemplate': existing_template['LaunchTemplates'][0],
                    'ResponseMetadata': existing_template['ResponseMetadata']}  # making structure as boto3 response
        return response

    def _create_new_launch_template(self,
                                    iam_role: str,
                                    user_data_script: str,
                                    image_id: str,
                                    instance_type: str,
                                    security_group_id: list[str]) -> dict:
        """Create a new launch template."""
        encoded_script = base64.b64encode(user_data_script.encode('utf-8')).decode('utf-8')
        self._logger.info(f"Creating Launch Template: {self._name}")
        response = self._client.create_launch_template(
            LaunchTemplateName=self._name,
            LaunchTemplateData={
                'ImageId': image_id,
                'InstanceType': instance_type,
                'KeyName': KEY_NAME,
                'UserData': encoded_script,
                'NetworkInterfaces': [
                    {
                        'AssociatePublicIpAddress': True,
                        'DeviceIndex': 0,
                        'Groups': security_group_id
                    }
                ],
                'IamInstanceProfile': {
                    'Name': iam_role
                },
                'MetadataOptions': {
                    'HttpTokens': 'optional',
                    'HttpEndpoint': 'enabled'
                }
            }
        )
        return response

    def clean_resources(self):
        self.delete_key_pair()
        self.delete_launch_template()

    def delete_launch_template(self):
        template_id = None  # For exception handling purposes
        try:
            template_id = self.id
            self._logger.info(f"Deleting launch template with ID: {template_id}")
            self._client.delete_launch_template(LaunchTemplateId=template_id)
            self._logger.info(f"Launch template deleted: {template_id}")
            self._response = None
        except (ClientError, ValueError) as e:
            self._logger.error(f"Failed to delete launch template {template_id}: {e}")

    def is_key_pair_exists(self, key_name):
        try:
            self._logger.info(f"Checking if key pair '{key_name}' exists...")
            # print("later: unmask line82")  //debug
            response = self._client.describe_key_pairs(KeyNames=[key_name])
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
                self._logger.info(f"Key pair '{key_name}' does not exist.")
                return False
            self._logger.info(f"Error checking if key pair exists: {e}")
            raise e
            # return False  # new code linefor debug
        except Exception as e:
            self._logger.error(f"Some unexpected error occurred in is_key_pair_exists: {e}")
            raise e

    def create_key_pair(self, key_name='my-key-pair'):
        if self.is_key_pair_exists(key_name):
            self._logger.info(f"Key Pair with name '{key_name}' already exists. Skipping creation.")
            self._key_pair_name = key_name
            return key_name

        try:
            self._logger.info(f"Creating key pair '{key_name}'...")
            response = self._client.create_key_pair(KeyName=key_name)
            key_material = response['KeyMaterial']

            try:
                with open(f'{key_name}.pem', 'w') as file:
                    file.write(key_material)
                os.chmod(f'{key_name}.pem', 0o600)

                self._logger.info(f"Key Pair '{key_name}' created and saved to {key_name}.pem")
            except Exception as e:
                self._logger.warning(f"Could not create {key_name}.pem, {e}")

            self._key_pair_name = key_name
            return key_name

        except ClientError as e:
            self._logger.error(f"An error occurred while creating the key pair: {e}")
            raise

    # Additional methods can be added for updating templates, describing templates, etc.
    def delete_key_pair(self):
        try:
            self._logger.info(f"Deleting key pair '{self._key_pair_name}'...")
            self._client.describe_key_pairs(KeyNames=[self._key_pair_name])
            self._client.delete_key_pair(KeyName=self._key_pair_name)
            self._logger.info(f"Key Pair '{self._key_pair_name}' deleted")
            self._key_pair_name = None
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
                self._logger.warning(f"Key Pair '{self._key_pair_name}' not found and cannot be deleted")
            else:
                self._logger.error(f"An error occurred while deleting the key pair: {e}")
