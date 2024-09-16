import time

import boto3
from botocore.exceptions import ClientError

from utils.Logger import Logger


class AutoScalingManager:
    def __init__(self, name, asg_client, logger):
        self._group_name = name
        self._client = asg_client
        self._logger = logger

    def create_auto_scaling_group(self, launch_template_id,
                                  get_subnets_id_list: list,
                                  target_groups_arns: list,
                                  asg_config: dict):

        try:
            self._logger.info(f"Creating Auto Scaling Group: {self._group_name}")
            vpc_zone_identifier_str = ','.join(get_subnets_id_list)
            response = self._client.create_auto_scaling_group(
                AutoScalingGroupName=self._group_name,
                LaunchTemplate={'LaunchTemplateId': launch_template_id},
                VPCZoneIdentifier=vpc_zone_identifier_str,
                TargetGroupARNs=target_groups_arns,
                **asg_config
            )
            self._logger.info(f"Auto Scaling Group created: {self._group_name}")
            return response
        except ClientError as e:
            self._logger.error(f"Failed to create Auto Scaling Group {self._group_name}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Failed to create Auto Scaling Group {self._group_name}: {e}")
            raise

    def attach_policy(self, policy_name: str, policy_params: dict):
        """
        Create a Scaling Policy for the Auto Scaling Group.
        """
        try:
            self._logger.info(f"Creating Scaling Policy: {policy_name}")
            response = self._client.put_scaling_policy(
                AutoScalingGroupName=self._group_name,
                PolicyName=policy_name,
                **policy_params
            )

            self._logger.info(f"Scaling Policy created: {policy_name}")
            return response
        except ClientError as e:
            self._logger.error(f"Failed to create Scaling Policy {policy_name}: {e}")
            return None
        except Exception as e:
            self._logger.error(f"Failed to create Scaling Policy {policy_name}: {e}")
            return None

    def configure_asg_notifications(self, sns_topic_arn, notification_types):
        """
        Add SNS topic for notifications to an Auto Scaling Group.

        :param sns_topic_arn: The ARN of the SNS topic to which notifications will be sent.
        :param notification_types: A list of event types for which notifications will be sent.
        """
        try:
            self._logger.info(f"Configuring notifications for ASG: {self._group_name}")
            response = self._client.put_notification_configuration(
                AutoScalingGroupName=self._group_name,
                TopicARN=sns_topic_arn,
                NotificationTypes=notification_types
            )
            self._logger.info(f"Notifications configured for ASG: {self._group_name}")
            return response
        except ClientError as e:
            self._logger.error(f"Failed to configure notifications for ASG {self._group_name}: {e}")
            return None
        except Exception as e:
            self._logger.error(f"Unexpected error configuring notifications for ASG {self._group_name}: {e}")
            return None

    @staticmethod
    def get_sns_topic_arn(topic_name: str) -> str | None:
        """
        Retrieves the ARN of an SNS topic given its name.

        :param topic_name: The name of the SNS topic.
        :return: The ARN of the SNS topic, or None if the topic is not found.
        """
        sns_client = boto3.client('sns', region_name='us-east-1')

        try:
            # List all SNS topics
            response = sns_client.list_topics()
            topics = response.get('Topics', [])

            # Iterate over the topics to find the one with the specified name
            for topic in topics:
                topic_arn = topic['TopicArn']
                if topic_name in topic_arn:
                    print(f"Found Topic ARN: {topic_arn}")
                    return topic_arn

            print(f"No topic found with the name: {topic_name}")
            return None

        except ClientError as e:
            print(f"Error retrieving SNS topic ARN: {e}")
            return None

    @staticmethod
    def open_sns_topic(topic_name: str, email_address: str = None) -> str | None:
        """
        Creates an SNS topic with the specified name and optionally subscribes an email address to the topic.

        :param topic_name: The name of the SNS topic to create.
        :param email_address: Optional email address to subscribe to the SNS topic.
        :return: The Amazon Resource Name (ARN) of the created SNS topic.
        """
        sns_client = boto3.client('sns', region_name='us-east-1')

        try:
            # Create an SNS topic with the specified name
            response = sns_client.create_topic(Name=topic_name)
            topic_arn = response['TopicArn']
            print(f"Topic ARN: {topic_arn}")

            # If an email address is provided, create a subscription
            if email_address:
                sns_client.subscribe(
                    TopicArn=topic_arn,
                    Protocol='email',
                    Endpoint=email_address
                )
                print(
                    f"Subscription request sent to {email_address}. Please check your email to confirm the subscription.")

            return topic_arn
        except ClientError as e:
            print(f"Error creating SNS topic or subscription: {e}")
            return None

    def delete_policy(self):
        try:
            # Step 1: Delete Scaling Policies
            self._logger.info(f"Deleting Scaling Policies for Auto Scaling Group: {self._group_name}")
            policies = self._client.describe_policies(AutoScalingGroupName=self._group_name)['ScalingPolicies']
            for policy in policies:
                self._client.delete_policy(AutoScalingGroupName=self._group_name, PolicyName=policy['PolicyName'])
                self._logger.info(f"Deleted Scaling Policy: {policy['PolicyName']}")
        except ClientError as e:
            self._logger.error(f"Failed to delete auto-scaling policies: {e}")

    def delete_group(self):
        try:
            self._logger.info(f"Deleting Auto Scaling Group: {self._group_name}")
            self._client.delete_auto_scaling_group(AutoScalingGroupName=self._group_name, ForceDelete=True)
            self._logger.info(f"Auto Scaling Group deleted: {self._group_name}")
        except ClientError as e:
            self._logger.error(f"Failed to delete auto-scaling-group: {e}")

    def wait_for_asg_termination(self, wait_interval=30, tries=4):
        self._logger.info(f"Waiting for all instances in Auto Scaling Group '{self._group_name}' to terminate.")

        for i in range(tries):
            try:
                # Describe instances in the Auto Scaling group
                response = self._client.describe_auto_scaling_instances()
                instances = response['AutoScalingInstances']

                # Filter instances that belong to the current Auto Scaling group and are not terminated
                asg_instances = [i for i in instances if i['AutoScalingGroupName'] == self._group_name]
                non_terminated_instances = [i for i in asg_instances if i['LifecycleState'] != 'Terminated']

                if not non_terminated_instances:
                    self._logger.info(f"All instances in Auto Scaling Group '{self._group_name}' have terminated.")
                    break
                else:
                    self._logger.info(f"{len(non_terminated_instances)} instance(s) still terminating...")

                time.sleep(wait_interval)

            except ClientError as e:
                self._logger.error(f"Failed to check instance status: {e}")
                break
            except Exception as e:
                self._logger.error(f"Unexpected error while waiting for instance termination: {e}")
                break

    def cleanup(self):
        self.delete_policy()
        self.delete_group()
