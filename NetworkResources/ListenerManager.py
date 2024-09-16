import boto3


class ListenerManager:
    def __init__(self, elbv2_client: boto3.client, logger):
        self._listener_arn = None
        self._elbv2_client = elbv2_client
        self._logger = logger

    def create_listener(self, load_balancer_arn: str, target_group_arn: str, static_listener_config: dict):
        try:
            response = self._elbv2_client.create_listener(
                LoadBalancerArn=load_balancer_arn,
                DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn}],
                **static_listener_config
            )
            self._listener_arn = response['Listeners'][0]['ListenerArn']
            self._logger.info(f"Listener created with ARN: {self._listener_arn}")
            return self._listener_arn
        except Exception as e:
            self._logger.error(f"Failed to create listener: {e}")
            raise

    def delete_listener(self, listener_arn: str = None):
        try:
            arn_to_delete = listener_arn or self._listener_arn
            self._elbv2_client.delete_listener(ListenerArn=arn_to_delete)
            self._logger.info(f"Listener deleted successfully. '{arn_to_delete}'")
        except Exception as e:
            self._logger.error(f"Failed to delete listener: {e}")

    @property
    def listener_arn(self):
        return self._listener_arn
