import boto3
import configuration.config
from NetworkResources.Interfaces.TargetGroupInterface import TargetGroupInterface


class TargetGroupApplicationManager(TargetGroupInterface):

    def __init__(self, client, name, logger):
        super().__init__(client, logger)
        self._name = name
        self._target_group_arn = None

    def create_target_group(self, vpc_id: str,
                            target_group_params: dict,
                            conflict_resolution_replace=True):
        try:
            # Check if a target group with the same name already exists
            existing_tg = self._find_target_group_by_name(self._name)

            if existing_tg:
                if conflict_resolution_replace:
                    self._logger.info(f"Target Group with name '{self._name}' already exists, replacing it.")
                    self.delete_target_group(existing_tg['TargetGroupArn'])
                else:
                    raise Exception(f"Target Group with name '{self._name}' already exists.")

            response = self._client.create_target_group(
                Name=self._name,
                VpcId=vpc_id,
                Tags=[{'Key': 'Name',
                       'Value': self._name}],
                **target_group_params
            )
            self._target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
            self._logger.info(f"Target Group '{self._name}' created with ARN: {self._target_group_arn}")
            self._logger.debug(f"The target group is on vpc-id{response['TargetGroups'][0]['VpcId']}")
        except Exception as e:
            self._logger.error(f"Failed to create target group: {e}")
            raise

    def register_targets(self, instance_ids: list):
        try:
            targets = [{'Id': instance_id} for instance_id in instance_ids]
            self._client.register_targets(TargetGroupArn=self._target_group_arn, Targets=targets)
            self._logger.info(f"Instances {instance_ids} registered to Target Group '{self._target_group_arn}'")
        except Exception as e:
            self._logger.error(f"Failed to register targets: {e}")
            raise

    def delete_target_group(self, target_group_arn: str = None):
        """
        Deletes the specified target group.

        :param target_group_arn: The ARN of the target group to delete.
                                 If not provided, the method will use the class's target group ARN.
        """
        try:
            # Use provided ARN or fallback to the stored ARN
            arn_to_delete = target_group_arn or self._target_group_arn

            if arn_to_delete is None:
                self._logger.info("In order to delete target_group,target group ARN must be provided or set in the "
                                  "class instance.")
                return

            # Delete the target group
            self._client.delete_target_group(TargetGroupArn=arn_to_delete)
            self._logger.info(f"Target Group deleted successfully: '{arn_to_delete}'")

            # Clear the stored ARN if it was used for deletion
            if arn_to_delete == self._target_group_arn:
                self._target_group_arn = None
        except Exception as e:
            self._logger.error(f"Failed to delete target group: {e}")

    @property
    def target_group_arn(self):
        return self._target_group_arn

    def _find_target_group_by_name(self, name: str):
        """
        Helper function to find a target group by name.

        :param name: Name of the target group.
        :return: Target group details if found, otherwise None.
        """
        try:
            response = self._client.describe_target_groups(Names=[name])
            if response['TargetGroups']:
                return response['TargetGroups'][0]
        except self._client.exceptions.TargetGroupNotFoundException:
            return None

        return None
