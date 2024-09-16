
class ApplicationLoadBalancerManager:
    def __init__(self, name: str, elbv2_client, logger):
        self._name = name
        self._load_balancer_arn = None
        self._elbv2_client = elbv2_client
        self._logger = logger

    @property
    def name(self):
        return self._name

    @property
    def load_balancer_arn(self):
        return self._load_balancer_arn

    def create_load_balancer(self,
                             subnets_ids: list,
                             security_group_id: str,
                             create_alb_params: dict,
                             conflict_resolution_replace=True):
        try:

            # Check if a load balancer with the same name already exists
            existing_lb = self._find_load_balancer_by_name(self._name)

            if existing_lb:
                # if conflict_resolution == 'load':
                #     self._load_balancer_arn = existing_lb['LoadBalancerArn']
                #     self._logger.info(
                #         f"Loaded existing Load Balancer '{self._name}' with ARN: {self._load_balancer_arn}")
                #     return self._load_balancer_arn
                if conflict_resolution_replace:
                    self._logger.info(f"Load Balancer with name '{self._name}' already exists, replacing it.")
                    self.delete_load_balancer(existing_lb['LoadBalancerArn'])
                else:
                    raise Exception(f"Load Balancer with name '{self._name}' already exists.")


            response = self._elbv2_client.create_load_balancer(
                **create_alb_params,
                Name=self._name,
                Subnets=subnets_ids,
                SecurityGroups=[security_group_id],
            )
            self._load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']
            self._logger.info(f"Load Balancer '{self.name}' created with ARN: {self._load_balancer_arn}")
            self._logger.info(self.get_alb_dns_name(self.name))
            return self._load_balancer_arn
        except Exception as e:
            self._logger.error(f"Failed to create load balancer: {e}")
            raise

    def get_alb_dns_name(self, load_balancer_name: str):
        response = self._elbv2_client.describe_load_balancers(
            Names=[load_balancer_name]
        )
        return response['LoadBalancers'][0]['DNSName']

    def delete_load_balancer(self, load_balancer_arn: str = None):
        try:
            arn_to_delete = load_balancer_arn or self._load_balancer_arn
            self._elbv2_client.delete_load_balancer(LoadBalancerArn=arn_to_delete)
            self._logger.info(f"Load Balancer '{arn_to_delete}' deleted successfully.")
            if arn_to_delete == self._load_balancer_arn:
                self._load_balancer_arn = None
        except Exception as e:
            self._logger.error(f"Failed to delete load balancer: {e}")

    def _find_load_balancer_by_name(self, name: str):
        """
        Helper function to find a load balancer by name.

        :param name: Name of the load balancer.
        :return: Load Balancer details if found, otherwise None.
        """
        try:
            response = self._elbv2_client.describe_load_balancers(Names=[name])
            if response['LoadBalancers']:
                return response['LoadBalancers'][0]
        except self._elbv2_client.exceptions.LoadBalancerNotFoundException:
            return None

        return None
