import boto3

from NetworkResources.Interfaces.SecurityGroupInterface import SecurityGroupInterface


class SecurityGroupManager(SecurityGroupInterface):
    def __init__(self,
                 ec2,
                 group_name: str,
                 sg_inbound_rules: list[dict[str, any]],
                 logger):
        self._sg_inbound_rules = sg_inbound_rules
        self.vpc_id: str | None = None
        self._group_name = group_name
        self._ec2 = ec2
        self._logger = logger
        self._security_group = None

    def create_security_group(self, vpc_id: str,
                              sg_params: dict = None) -> None:
        self._security_group = self._ec2.create_security_group(
            GroupName=self._group_name,
            VpcId=vpc_id,
            **sg_params
        )

        # Add inbound rules using IpPermissions parameter
        self._security_group.authorize_ingress(
            IpPermissions=self._sg_inbound_rules
        )

        # Add a name tag to the security group
        self._security_group.create_tags(Tags=[{'Key': 'Name', 'Value': self._group_name}])
        self._logger.info(f"Security Group created with ID: {self._security_group.id} and name: {self._group_name}")

    def delete_security_group(self) -> bool:
        if self._security_group:
            try:
                self._security_group.delete()
                self._logger.info(f"Security Group {self._security_group.id} has been deleted.")
                self._security_group = None
            except Exception as e:
                self._logger.error(e)
                return False
        return True

    def load_security_group(self, security_group_id: str) -> None:
        self._security_group = self._ec2.SecurityGroup(security_group_id)

    @property
    def id(self):
        return self._security_group.id
