import boto3

from NetworkResources import SecurityGroupManager, ListenerManager, TargetGroupApplicationManager
from NetworkResources import AutoScalingManager, ApplicationLoadBalancerManager, LaunchTemplateManager
from AwsDataResources import S3Manager, DynamodbManager
from VPCManager import VPCManager
from RDSManager import RDSManager
from utils.NameGeneratorDNS import generate_unique_dns_name
from LambdaManagerEmployee import LambdaManagerEmployee
import configuration as cfg


class AWSResourceFactory:
    def __init__(self, ec2, ec2_client,
                 elbv2_client,
                 s3_resource,
                 s3_client,
                 dynamodb_client,
                 dynamodb_resource,
                 auto_scaling_client,
                 lambda_client,
                 iam_client,
                 logger):
        self._iam_client = iam_client
        self._lambda_client = lambda_client
        self._auto_scaling_client = auto_scaling_client
        self._dynamodb_client = dynamodb_client
        self._dynamodb_resource = dynamodb_resource
        self._s3_client = s3_client
        self._s3_resource = s3_resource
        self._elbv2_client = elbv2_client
        self._ec2_client = ec2_client
        self._ec2 = ec2
        self._logger = logger

    @staticmethod
    def factory(logger):
        ec2_resource = boto3.resource('ec2', region_name=cfg.config.REGION)
        client = boto3.client('ec2', region_name=cfg.config.REGION)
        elbv2_client = boto3.client('elbv2', region_name=cfg.config.REGION)
        s3_resource = boto3.resource('s3')
        s3_client = boto3.client('s3')
        dynamodb_client = boto3.client('dynamodb', region_name=cfg.config.REGION)
        dynamodb_resource = boto3.resource('dynamodb', region_name=cfg.config.REGION)
        asg_client = boto3.client('autoscaling', region_name=cfg.config.REGION)

        return AWSResourceFactory(ec2=ec2_resource,
                                  ec2_client=client,
                                  elbv2_client=elbv2_client,
                                  s3_resource=s3_resource,
                                  s3_client=s3_client,
                                  dynamodb_resource=dynamodb_resource,
                                  dynamodb_client=dynamodb_client,
                                  auto_scaling_client=asg_client,
                                  logger=logger)

    def lambda_manager(self):
        return LambdaManagerEmployee(function_name=cfg.lambda_config.FUNCTION_NAME,
                                     role_name=cfg.lambda_config.ROLE_NAME,
                                     lambda_client=self._lambda_client,
                                     iam_client=self._iam_client,
                                     s3_client=self._s3_client,
                                     logger=self._logger)

    def vpc_manager(self) -> VPCManager:
        sg = SecurityGroupManager(ec2=self._ec2,
                                  group_name=cfg.vpc_config.SG_NAME,
                                  sg_inbound_rules=cfg.vpc_config.SG_INBOUND_RULES,
                                  logger=self._logger)

        return VPCManager(ec2=self._ec2,
                          client=self._ec2_client,
                          security_group_manager=sg,
                          logger=self._logger)

    def target_group_application_manager(self):
        return TargetGroupApplicationManager(client=self._elbv2_client, logger=self._logger)

    def application_load_balancer_manager(self):
        return ApplicationLoadBalancerManager(name=cfg.alb_config.NAME,
                                              elbv2_client=self._elbv2_client,
                                              logger=self._logger)

    def target_group(self):
        return TargetGroupApplicationManager(client=self._elbv2_client,
                                             name=cfg.alb_config.TARGET_GROUP_NAME,
                                             logger=self._logger)

    def listener_manager(self):
        return ListenerManager(elbv2_client=self._elbv2_client,
                               logger=self._logger)

    def auto_scaling_manager(self):
        return AutoScalingManager(name=cfg.asg_config.AUTO_SCALING_GROUP_NAME,
                                  asg_client=self._auto_scaling_client,
                                  logger=self._logger)

    def launch_template_manager(self):
        return LaunchTemplateManager(ec2_client=self._ec2_client,
                                     name=cfg.ec2_config.LAUNCH_TEMPLATE_NAME,
                                     region=cfg.config.REGION,
                                     logger=self._logger)

    def s3_manager(self):
        bucket_name = generate_unique_dns_name(cfg.s3_config.S3_BUCKET_BASE_NAME)
        return S3Manager(s3=self._s3_resource,
                         s3_client=self._s3_client,
                         bucket_name=bucket_name,
                         region=cfg.config.REGION,
                         logger=self._logger)

    def dynamodb_manager(self):
        return DynamodbManager(dynamodb=self._dynamodb_resource,
                               dynamodb_client=self._dynamodb_client,
                               table_name=cfg.dynamodb_config.NAME,
                               region=cfg.config.REGION,
                               logger=self._logger)

    def rds_manager(self):
        resources = dict()
        resources['S3Manager'] = (self.s3_manager())
        resources['DynamodbManager'] = (self.dynamodb_manager())

        return RDSManager(resources=resources, logger=self._logger)
