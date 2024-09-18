from configuration.config import REGION

# Common Constants
ANYWHERE_IPV4 = "0.0.0.0/0"  # CIDR block representing "anywhere" for inbound/outbound rules

# VPC Configuration
CIDR_BLOCK = "10.0.0.0/16"  # CIDR block for the VPC
VPC_NAME = "Employee-directory-app-VPC"  # Name tag for the VPC

# Internet Gateway Configuration
IGW_NAME = "Employee-directory-app-igw"  # Name tag for the Internet Gateway

# Route Table Configuration
RT_NAME = "Employee-directory-app-rt"  # Name tag for the Route Table

# Subnets Configuration
AVAILABILITY_ZONES = [REGION + 'a', REGION + 'b']
SUBNETS_PARAMS = [
    {"subnet_name": "PublicSubnetA", "cidr_block": "10.0.0.0/24", "availability_zone": AVAILABILITY_ZONES[0]},
    {"subnet_name": "PublicSubnetB", "cidr_block": "10.0.1.0/24", "availability_zone": AVAILABILITY_ZONES[1]},
]

# Security Group Configuration
SG_NAME = "Employee-directory-security-group"  # Name tag for the Security Group
SG_DESCRIPTION = "Allows HTTP requests and SSH connections."

SG_PARAMS = {
    'Description': SG_DESCRIPTION
}

WEB_INBOUND_RULE = {  # Security group inbound rule
    'IpProtocol': 'tcp',
    'FromPort': 80,
    'ToPort': 80,
    'IpRanges': [{'CidrIp': ANYWHERE_IPV4, 'Description': 'Allow web requests from anywhere'}]
}

SSH_INBOUND_RULE = {  # Security group inbound rule
    'IpProtocol': 'tcp',
    'FromPort': 22,
    'ToPort': 22,
    'IpRanges': [{'CidrIp': ANYWHERE_IPV4, 'Description': 'Allow SSH access from anywhere'}]
}

SG_INBOUND_RULES = [WEB_INBOUND_RULE, SSH_INBOUND_RULE]  # This will be used in the code

VPC_LAUNCH_PARAMS = {
    'cidr_block': CIDR_BLOCK,
    'vpc_name': VPC_NAME,
    'igw_name': IGW_NAME,
    'rt_name': RT_NAME,
    'subnets_params': SUBNETS_PARAMS,
    'security_group_params': SG_PARAMS
}

# Clean Resources
RETRIES = 3  # Number of times to retry resource cleanup
