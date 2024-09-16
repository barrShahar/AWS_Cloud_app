from configuration.config import REGION

# Common Constants
ANYWHERE_IPV4 = "0.0.0.0/0"  # CIDR block representing "anywhere" for inbound/outbound rules

# VPC Configuration
CIDR_BLOCK = "10.0.0.0/16"  # CIDR block for the VPC
VPC_NAME = "MyVPC"  # Name tag for the VPC

# Internet Gateway Configuration
IGW_NAME = "MyInternetGateway"  # Name tag for the Internet Gateway

# Route Table Configuration
RT_NAME = "MyRouteTable"  # Name tag for the Route Table

# Subnets Configuration
AVAILABILITY_ZONES = [REGION + 'a', REGION + 'b']
SUBNETS_PARAMS = [
    {"subnet_name": "PublicSubnetA", "cidr_block": "10.0.0.0/24", "availability_zone": AVAILABILITY_ZONES[0]},
    {"subnet_name": "PublicSubnetB", "cidr_block": "10.0.1.0/24", "availability_zone": AVAILABILITY_ZONES[1]},
]

# Security Group Configuration
SG_NAME = "MySecurityGroup"  # Name tag for the Security Group
SG_DESCRIPTION = "No Description"

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
RETIRES = 3  # how many times to retry cleaning resources
#
# subnetA_name = 'public-subnet-A'
# subnetB_name = 'public-subnet-B'
# subnets_cidr_dict = {
#     subnetA_name: '10.0.0.0/24',
#     subnetB_name: '10.0.1.0/24'
# }
# # vpc sg
# sg_name = '-1'
# # vpc sg inbound ip-permission
# cdir_ip_toBeNameBetter = '0.0.0.0/0'  # Anywhere_IPv4
# ip_inbound_rule = {
#     'IpProtocol': 'tcp',
#     'FromPort': 80,
#     'ToPort': 80,
#     'IpRanges': [{'CidrIp': cdir_ip_toBeNameBetter, 'Description': 'Allow web requests from anywhere'}]
# }
# ssh_inbound_rule = {
#     'IpProtocol': 'tcp',
#     'FromPort': 22,
#     'ToPort': 22,
#     'IpRanges': [{'CidrIp': cdir_ip_toBeNameBetter, 'Description': 'Allow SSH access'}]
# }
# sg_inbound_rules = [ip_inbound_rule, ssh_inbound_rule]
#
# # rout table
# rt_name = '-1'
# destination_cidr_block = '-1'
#
# # internet gate-way
# igw_name = '-1'
