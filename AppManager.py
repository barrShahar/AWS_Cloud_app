import boto3
import time
from AWSResourceFactory import AWSResourceFactory
from NetworkResources.Interfaces.TargetGroupInterface import TargetGroupInterface
import Interfaces
from configuration import *


class AppManager:
    def __init__(self, logger):
        self.listener_manager = None
        self._lt_manager = None
        self.logger = logger
        self._ec2_resource = boto3.resource('ec2', region_name=config.REGION)
        self._client = boto3.client('ec2', region_name=config.REGION)
        self._elbv2_client = boto3.client('elbv2', region_name=config.REGION)
        self._s3_resource = boto3.resource('s3')
        self._s3_client = boto3.client('s3')
        self._dynamodb_client = boto3.client('dynamodb', region_name=config.REGION)
        self._dynamodb_resource = boto3.resource('dynamodb', region_name=config.REGION)
        self._asg_client = boto3.client('autoscaling', region_name=config.REGION)
        self._lambda_client = boto3.client('lambda')
        self._iam_client = boto3.client('iam')

        aws_resources_factory = AWSResourceFactory(ec2=self._ec2_resource,
                                                   ec2_client=self._client,
                                                   elbv2_client=self._elbv2_client,
                                                   s3_resource=self._s3_resource,
                                                   s3_client=self._s3_client,
                                                   dynamodb_resource=self._dynamodb_resource,
                                                   dynamodb_client=self._dynamodb_client,
                                                   auto_scaling_client=self._asg_client,
                                                   lambda_client=self._lambda_client,
                                                   iam_client=self._iam_client,
                                                   logger=logger)

        self._vpc_manager: Interfaces.VpcInterface = aws_resources_factory.vpc_manager()

        self._tg: TargetGroupInterface = aws_resources_factory.target_group()

        self._alb = aws_resources_factory.application_load_balancer_manager()

        self.listener_manager = aws_resources_factory.listener_manager()

        self._asg = aws_resources_factory.auto_scaling_manager()

        self._lt_manager = aws_resources_factory.launch_template_manager()

        self._rds_manager = aws_resources_factory.rds_manager()

        self._app_lambda = aws_resources_factory.lambda_manager()

    def initialize_vpc_and_aws_resources(self):
        self._vpc_manager.launch_vpc_environment(**vpc_config.VPC_LAUNCH_PARAMS)

        self.launch_alb_server()

        rds_response = self._rds_manager.setup()

        user_data = ec2_config.lunch_template_script_stress(rds_response['S3Manager']['Name'])
        self._lt_manager.create_launch_template(user_data_script=user_data,
                                                security_group_id=[self._vpc_manager.security_group_id],
                                                **ec2_config.LAUNCH_TEMPLATE_CREATE_PARAMS)

        self.launch_auto_scaling_group()

        self.load_bucket_photos_lambda(bucket_name=rds_response['S3Manager']['Name'])

    def clean_resources(self):
        functions = [self._asg.delete_group,
                     self.listener_manager.delete_listener,
                     self._tg.delete_target_group,
                     self._alb.delete_load_balancer,
                     self._rds_manager.clean_resources,
                     self._lt_manager.clean_resources,
                     self._vpc_manager.teardown_vpc_resources,
                     self._app_lambda.clean_up]

        for func in functions:
            try:
                func()
            except Exception as e:
                self.logger.error(f"Some unexpected error execute {func.__name__}: {e}")

    def launch_alb_server(self):
        self._alb.create_load_balancer(
            create_alb_params=alb_config.CREATE_ALB_PARAMS,
            subnets_ids=self._get_subnet_ids(),
            security_group_id=self._vpc_manager.security_group_id
        )

        self._tg.create_target_group(vpc_id=self._vpc_manager.id,
                                     target_group_params=alb_config.TG_PARAMS)

        self.listener_manager.create_listener(self._alb.load_balancer_arn,
                                              target_group_arn=self._tg.target_group_arn,
                                              static_listener_config=alb_config.LISTENER_PARAMS)

    def launch_auto_scaling_group(self):
        self._asg.create_auto_scaling_group(launch_template_id=self._lt_manager.id,
                                            get_subnets_id_list=self._get_subnet_ids(),
                                            target_groups_arns=[self._tg.target_group_arn],
                                            asg_config=asg_config.CREATE_ASG_PARAMS)

        self._asg.attach_policy(policy_name=asg_config.POLICY_NAME,
                                policy_params=asg_config.ASG_POLICY_PARAMS)

    def _get_subnet_ids(self):
        return [subnet.id for subnet in self._vpc_manager.subnets]

    @property
    def server_link(self):
        return self._alb.get_alb_dns_name(self._alb.name)

    def _create_lambda_helper(self, bucket_name):
        self._app_lambda.deploy_lambda(lambda_code=lambda_config.lambda_code,
                                       role_name=lambda_config.ROLE_NAME,
                                       bucket_name=bucket_name,
                                       zip_file_url=lambda_config.ZIP_FILE_URL,
                                       lambda_client_create_function_params=lambda_config.LAMBDA_CLIENT_CREATE_FUNCTION)

    def load_bucket_photos_lambda(self, bucket_name, number_of_retries=3):
        """
            Deploys a Lambda function for one-time use to upload employee photos to an S3 bucket.
            The function may need to be retried due to transitional states, such as invoking
            the Lambda function while it's still in a pending state.

            :param bucket_name: The name of the S3 bucket to which the photos will be uploaded.
            :param number_of_retries: The number of retry attempts in case of failure. Default is 3.
            :return: None
        """
        for i in range(number_of_retries):
            try:  # temporary block for development
                self.logger.debug(f"Attempt {i + 1} to launch the Lambda function for uploading photos")
                self._create_lambda_helper(bucket_name=bucket_name)
                return
            except Exception as e:
                self.logger.debug(e)
                # wait 20 seconds
                self.logger.debug("Waiting 20 seconds before retrying Lambda execution")
                time.sleep(20)


# if __name__ == '__main__':
#     # lt = LaunchTemplateManager('dsd', 4)
#     logger = utils.Logger.Logger()
#     app_manager = AppManager()
#     try:
#         app_manager.initialize_vpc_and_aws_resources()
#         logger.info(f"App Link: {app_manager.server_link}")
#     except Exception as e:
#         logger.error(e)
#         # logger.error(traceback.print_exc())
#     finally:
#         input("Press any key to cleanup resources..")
#         app_manager.clean_resources()
