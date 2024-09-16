from configuration.config import REGION

LAUNCH_TEMPLATE_NAME = "app-launch-template"
LAUNCH_TEMPLATE_AMI = 'ami-0182f373e66f89c85'  ## ??  (Double-check the actual AMI ID)
LAUNCH_TEMPLATE_TYPE = 't2.micro'
IAM_ROLE = 'EmployeeWebApp'

LAUNCH_TEMPLATE_CREATE_PARAMS = {
    'iam_role': IAM_ROLE,
    'image_id': LAUNCH_TEMPLATE_AMI,
    'instance_type': LAUNCH_TEMPLATE_TYPE,
}

LAUNCH_TEMPLATE_DATA_PARAMS = {
    'ImageId': LAUNCH_TEMPLATE_AMI,
    'InstanceType': LAUNCH_TEMPLATE_TYPE,
}

recreate_template = True    # If launch-template already exist

# key-pair-configuration
create_new_key_pair = True  # if not already exist
delete_key_pair = True


KEY_PAIR_NAME = 'key-pair'


def lunch_template_script_stress(s3_bucket_name: str) -> str:
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
export DEFAULT_AWS_REGION={REGION}

# Enable admin tools for stress testing
export SHOW_ADMIN_TOOLS=1

# Install dependencies
npm install

# Start your app
npm start
"""
    return script
