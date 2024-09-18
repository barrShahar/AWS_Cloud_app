from configuration.config import REGION

AUTO_SCALING_GROUP_NAME = "employee-auto-scaling"
AVAILABILITY_ZONES = [REGION + 'a', REGION + 'b']

MIN_SIZE = 2
MAX_SIZE = 4
DESIRED_CAPACITY = 2
HEALTH_CHECK_GRACE_PERIOD = 300
HEALTH_CHECK_TYPE = "ELB"

CREATE_ASG_PARAMS = {
    "MinSize": MIN_SIZE,
    "MaxSize": MAX_SIZE,
    "DesiredCapacity": DESIRED_CAPACITY,
    "AvailabilityZones": AVAILABILITY_ZONES,
    "HealthCheckType": HEALTH_CHECK_TYPE,
    "HealthCheckGracePeriod": HEALTH_CHECK_GRACE_PERIOD
}

POLICY_NAME = "your_policy_name"
POLICY_TYPE = "TargetTrackingScaling"
PREDEFINED_METRIC_TYPE = "ASGAverageCPUUtilization"
TARGET_VALUE = 30.0  # Adjust as needed
WARM_UP = 150  # Adjust as needed
COOLDOWN = 200  # Adjust as needed

ASG_POLICY_PARAMS = {
    'PolicyType': POLICY_TYPE,
    'TargetTrackingConfiguration': {
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': PREDEFINED_METRIC_TYPE
        },
        'TargetValue': TARGET_VALUE,
    },
    'EstimatedInstanceWarmup': WARM_UP,
    'Cooldown': COOLDOWN
}

# Security Group
SG_INBOUND_RULES = 'todo'
SG_NAME = 'alb-http-traffic'


# SNS topic (optional)
ENABLE_NOTIFICATIONS = True
SNS_TOPIC_ARN = None
TOPIC_NAME = 'CPU-UTILIZATION'
EMAIL = 'barr.shahar@gmail.com'
