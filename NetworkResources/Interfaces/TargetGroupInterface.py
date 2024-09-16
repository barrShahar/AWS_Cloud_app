from abc import ABC, abstractmethod


class TargetGroupInterface(ABC):
    def __init__(self, client, logger):
        self._client = client
        self._logger = logger

    @abstractmethod
    def create_target_group(self, *args, **kwargs):
        """
        Creates a target group for the specific load balancer type.
        # :param name: Name of the target group.
        # :param vpc_id: ID of the VPC where the target group is located.
        # :param health_check_protocol: Protocol to be used for health checks.
        """
        pass

    @abstractmethod
    def delete_target_group(self, target_group_arn: str = None):
        """
        Deletes the target group.
        :param target_group_arn: ARN of the target group to delete.
        """
        pass

    @property
    @abstractmethod
    def target_group_arn(self):
        """
        Returns the ARN of the target group.
        """
        pass
