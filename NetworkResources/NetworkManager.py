from configuration import alb_config, asg_config, ec2_config
from NetworkResources.AutoScalingManager import AutoScalingManager
from NetworkResources.ApplicationLoadBalancerManager import ApplicationLoadBalancerManager
from NetworkResources.SecurityGroupManager import SecurityGroupInterface
from NetworkResources.LaunchTemplateManager import LaunchTemplateManager
from NetworkResources.SecurityGroupManager import SecurityGroupManager


class NetworkManager:
    def __init__(self, vpc_id: str,
                 launch_template_manager: LaunchTemplateManager,
                 alb_manager: ApplicationLoadBalancerManager,
                 asg_manager: AutoScalingManager,
                 logger):
        self.vpc_id = vpc_id
        self.sg_manager = None
        self.logger = logger
        self.asg_manager = asg_manager
        self.alb_manager = alb_manager
        self.launch_template_manager = launch_template_manager

    def setup(self):
        # Create security group
        self.sg_manager: SecurityGroupInterface = SecurityGroupManager(
            region=asg_config.REGION,
            group_name=asg_config.SG_NAME,
            sg_inbound_rules=asg_config.SG_INBOUND_RULES,
            logger=self.logger)

        self.sg_manager.create_security_group(self.vpc_id)
        tg_manager: T

        alb_manager: ApplicationLoadBalancerManager = ApplicationLoadBalancerManager(name=alb_config.NAME,
                                                                                     logger=self.logger)

        tg_manager = NetworkManager

        # Create launch template
        (self.launch_template_manager.create_launch_template
         (asg_config.REGION,
          name=ec2_config.LAUNCH_TEMPLATE_NAME,
          iam_role='todo',
          user_data_script="todo",
          image_id=ec2_config.LAUNCH_TEMPLATE_AMI,
          instance_type=ec2_config.LAUNCH_TEMPLATE_TYPE,
          key_name='todo',
          security_group_id=['todo'],
          logger=self.logger
          ))

        #
