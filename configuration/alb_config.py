from configuration.config import REGION

AVAILABILITY_ZONES = [REGION + 'a', REGION + 'b']

NAME = "Web-Application-ALB"
TARGET_GROUP_NAME = 'app-target-group'
SCHEME = 'internet-facing'
ALB_TYPE = 'application'
IP_ADDRESS_TYPE = 'ipv4'

# Creating ALB
# If there is an ALB with the same name, Replace with a new one (throw Error otherwise)
conflict_resolution_REPLACE = True

# Target group
TARGET_TYPE = 'instance'
HEALTH_CHECK_PROTOCOL = 'HTTP'
HEALTHY_THRESHOLD = 2
UNHEALTHY_THRESHOLD = 5
HEALTH_CHECK_TIMEOUT = 20
HEALTH_CHECK_INTERVAL = 30
HEALTH_CHECK_PATH = '/'

TG_PARAMS = {
    'Protocol': 'HTTP',
    'Port': 80,
    'TargetType': TARGET_TYPE,
    'HealthCheckProtocol': HEALTH_CHECK_PROTOCOL,
    'HealthyThresholdCount': HEALTHY_THRESHOLD,
    'UnhealthyThresholdCount': UNHEALTHY_THRESHOLD,
    'HealthCheckTimeoutSeconds': HEALTH_CHECK_TIMEOUT,
    'HealthCheckIntervalSeconds': HEALTH_CHECK_INTERVAL,
    'HealthCheckPath': HEALTH_CHECK_PATH
}


CREATE_ALB_PARAMS = {'Scheme': SCHEME,
                     'Type': ALB_TYPE,
                     'IpAddressType': IP_ADDRESS_TYPE}

# Listener configuration

LISTENER_PROTOCOL = 'HTTP'
LISTENER_PORT = 80

LISTENER_PARAMS = {
    "Protocol": LISTENER_PROTOCOL,
    "Port": LISTENER_PORT,
}

