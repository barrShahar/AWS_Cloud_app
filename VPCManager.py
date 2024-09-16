from botocore.exceptions import WaiterError

from Interfaces.VPCInterface import VpcInterface
from botocore.client import BaseClient
from configuration import vpc_config
from NetworkResources.SecurityGroupManager import SecurityGroupManager, SecurityGroupInterface
import time


class VPCManager(VpcInterface):
    def __init__(self, ec2,
                 client: BaseClient,
                 security_group_manager: SecurityGroupInterface,
                 logger=None):
        """
        Initializes the VPCManager with necessary AWS resources and managers.

        :param ec2: Boto3 EC2 resources object
        :param client: Boto3 client object for EC2
        :param security_group_manager: Instance of SecurityGroupInterface for managing security groups
        :param logger: Logger instance for logging operations
        """
        self._security_group_manager = security_group_manager
        self._ec2 = ec2
        self._client = client
        self._vpc = None
        self._route_table = None
        self._internet_gateway = None
        self._subnets = []
        self._logger = logger

    @property
    def id(self):
        if self._vpc:
            return self._vpc.id
        else:
            self._logger.error("Logic error, can't get vpc.if because VPC not initialized.")
            raise Exception("VPC not initialized.")

    @property
    def security_group_id(self) -> str:
        return self._security_group_manager.id

    @property
    def subnets(self) -> list:
        return self._subnets

    def launch_vpc_environment(self, cidr_block,
                               vpc_name,
                               igw_name,
                               rt_name: str,
                               subnets_params: list[dict],
                               security_group_params: dict):
        """
        Launches the entire VPC environment including VPC, Internet Gateway, Route Table, and Subnets.

        :param security_group_params:
        :param cidr_block: The CIDR block for the VPC
        :param vpc_name: The name tag for the VPC
        :param igw_name: The name tag for the Internet Gateway
        :param rt_name: The name tag for the Route Table
        :param subnets_params: A list of dictionaries containing subnet parameters like CIDR block and AZ
        """
        self.create_vpc(cidr_block, vpc_name)
        self.create_internet_gateway(igw_name=igw_name)
        self.create_route_table(rt_name=rt_name)

        self.create_subnets(subnets_params)
        self.associate_subnets_list_with_route_table()

        # Create the security group in the newly created VPC
        self._security_group_manager.create_security_group(self._vpc.id, security_group_params)

    def teardown_vpc_resources(self, tries=0, max_retrying=vpc_config.RETIRES):
        """
        Tears down the VPC environment by deleting all resources: security groups, subnets_ids, route tables, IGW, and the VPC itself.

        :return: Boolean indicating if all resources are successfully deleted
        """
        self._logger.debug(f"Attempt to clean VPC Resources {tries + 1}/{max_retrying}")
        try:
            # security group
            try:
                self._debug_resources_status()
            except Exception as e:
                self._logger.debug(e)

            deletion_vector = [self.delete_subnets_and_dependencies,
                               self.delete_internet_gateway,
                               self.delete_subnets_and_dependencies,  # debug
                               self.delete_route_table,
                               self._security_group_manager.delete_security_group,
                               self.delete_vpc]

            is_all_deleted = True
            for func in deletion_vector:
                is_all_deleted = is_all_deleted and func()

        except Exception as e:
            self._logger.error(f"Error during teardown: {e}")
            if tries < max_retrying:
                self.teardown_vpc_resources(tries + 1, max_retrying)
            raise

    def create_vpc(self, cidr_block, vpc_name):
        """
        Creates a VPC with the given CIDR block and name.

        :param cidr_block: The CIDR block for the VPC
        :param vpc_name: The name tag for the VPC
        """
        self._vpc = self._ec2.create_vpc(CidrBlock=cidr_block)
        self._vpc.wait_until_available()

        # Enable DNS support and hostnames in the VPC
        self._vpc.modify_attribute(EnableDnsSupport={'Value': True})
        self._vpc.modify_attribute(EnableDnsHostnames={'Value': True})

        # Tag the VPC with a name
        self._vpc.create_tags(Tags=[{'Key': 'Name', 'Value': vpc_name}])
        self._logger.info(f"VPC created with ID: {self._vpc.id} and name: {vpc_name}")

    def create_internet_gateway(self, igw_name):
        """
        Creates and attaches an Internet Gateway to the VPC.

        :param igw_name: The name tag for the Internet Gateway
        """
        self._internet_gateway = self._ec2.create_internet_gateway()
        self._vpc.attach_internet_gateway(InternetGatewayId=self._internet_gateway.id)
        self._internet_gateway.create_tags(Tags=[{'Key': 'Name', 'Value': igw_name}])
        self._logger.info(
            f"Internet Gateway created and attached with ID: {self._internet_gateway.id} and name: {igw_name}")

    def create_route_table(self, rt_name: str) -> None:
        """
        Creates a Route Table and adds a route to the Internet Gateway.

        :param rt_name: The name tag for the Route Table
        """
        self._route_table = self._vpc.create_route_table()
        self._route_table.create_route(
            DestinationCidrBlock=vpc_config.ANYWHERE_IPV4,
            GatewayId=self._internet_gateway.id
        )
        self._route_table.create_tags(Tags=[{'Key': 'Name', 'Value': rt_name}])
        self._logger.info(f"Route Table created with ID: {self._route_table.id} and name: {rt_name}")

    def create_subnet(self, cidr_block, availability_zone, subnet_name):
        """
        Creates a subnet in the specified CIDR block and availability zone.

        :param cidr_block: The CIDR block for the subnet
        :param availability_zone: The availability zone for the subnet
        :param subnet_name: The name tag for the subnet
        :return: The created subnet object
        """
        subnet = self._ec2.create_subnet(CidrBlock=cidr_block, VpcId=self._vpc.id, AvailabilityZone=availability_zone)
        subnet.create_tags(Tags=[{'Key': 'Name', 'Value': subnet_name}])
        self._subnets.append(subnet)
        self._logger.info(f"Subnet created with ID: {subnet.id} in AZ: {availability_zone}")
        return subnet

    def associate_subnet_with_route_table(self, subnet):
        """
        Associates a subnet with the created route table.

        :param subnet: The subnet object to be associated with the route table
        """
        self._route_table.associate_with_subnet(SubnetId=subnet.id)
        self._logger.info(f"Subnet ID: {subnet.id} associated with Route Table ID: {self._route_table.id}")

    def delete_subnets_and_dependencies(self, delay=20, max_attempts=10) -> bool:
        """
        Terminates instances in the subnets, waits for termination, and deletes all subnets_ids associated with the VPC.
        :param delay: Time in seconds to wait between checks for instance termination.
        :param max_attempts: Maximum number of attempts to check for instance termination before timing out.
        """
        try:
            if not self._subnets:
                self._logger.info("No subnets to delete.")
                return True

            instance_waiter = self._ec2.meta.client.get_waiter('instance_terminated')

            for subnet in self._subnets:
                self._logger.info(f"Checking for instances in Subnet ID: {subnet.id}")

                # Get all instances in the subnet
                instances = list(self._ec2.instances.filter(Filters=[{'Name': 'subnet-id', 'Values': [subnet.id]}]))

                if instances:
                    instance_ids = [instance.id for instance in instances]
                    self._logger.info(f"Found instances {instance_ids} in Subnet ID: {subnet.id}, terminating...")

                    # Terminate instances
                    self._ec2.instances.filter(InstanceIds=instance_ids).terminate()

                    # Wait for instances to terminate using the waiter
                    try:
                        self._logger.info(f"Waiting for instances {instance_ids} to terminate...")
                        instance_waiter.wait(InstanceIds=instance_ids,
                                             WaiterConfig={'Delay': delay, 'MaxAttempts': max_attempts})
                        self._logger.info(f"All instances in Subnet ID: {subnet.id} terminated.")
                    except WaiterError as e:
                        self._logger.error(f"Error waiting for instances to terminate in Subnet ID: {subnet.id}: {e}")
                        continue

                # After ensuring instances are terminated, delete the subnet
                subnet.delete()
                self._logger.info(f"Subnet ID: {subnet.id} deleted.")

            # Clear subnets list
            self._subnets = []
            return True

        except Exception as e:
            self._logger.error(f"Error deleting subnets: {e}")
            return False

    def delete_subnets(self):
        """
        Deletes all subnets_ids associated with the VPC.
        """
        try:
            if self._subnets:
                for subnet in self._subnets:
                    subnet.delete()
                    self._logger.info(f"Subnet ID: {subnet.id} deleted")
                self._subnets = []
        except Exception as e:
            self._logger.error(f"Error deleting Subnets: {e}")

    def delete_internet_gateway(self) -> bool:
        """
        Detaches and deletes the Internet Gateway.
        """
        try:
            if self._internet_gateway:
                try:
                    self._vpc.detach_internet_gateway(InternetGatewayId=self._internet_gateway.id)
                except Exception as e:
                    self._logger.error(f"Error detaching Internet Gateway: {e}")
                    raise

                self._internet_gateway.delete()
                self._logger.info(f"Internet Gateway ID: {self._internet_gateway.id} detached and deleted")
                self._internet_gateway = None
        except Exception as e:
            self._logger.error(f"Error deleting Internet Gateway: {e}")
            return False

        return True

    def delete_route_table(self) -> bool:
        """
        Deletes the route table and its associations.
        """
        try:
            if self._route_table:
                try:
                    for association in self._route_table.associations:
                        association.delete()
                except Exception as e:
                    self._logger.error(f"Error deleting route table associations: {e}")

                self._route_table.delete()
                self._logger.info(f"Route Table ID: {self._route_table.id} deleted")
                self._route_table = None
                return True
        except Exception as e:
            self._logger.error(f"Error deleting Route Table: {e}")
            return False

    def delete_vpc(self) -> bool:
        """
        Deletes the VPC.
        """
        try:
            if self._vpc:
                self._vpc.delete()
                self._logger.info(f"VPC ID: {self._vpc.id} deleted")
                self._vpc = None
        except Exception as e:
            self._logger.error(f"Error deleting VPC: {e}")
            return False
        return True

    def delete_vpc_with_retry(self, max_attempts=3, delay=5) -> bool:
        """
        Attempts to delete the VPC multiple times with a delay between attempts.

        :param max_attempts: Maximum number of attempts
        :param delay: Delay in seconds between attempts
        :return: Boolean indicating whether the VPC was successfully deleted
        """
        for attempt in range(max_attempts):
            try:
                self.teardown_vpc_resources()
                return True
            except Exception as e:
                self._logger.error(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(delay)
        return False

    def are_resources_fully_deleted(self) -> bool:
        """
        Checks if all resources have been successfully deleted.

        :return: Boolean indicating if all resources are deleted.
        """
        return not any([self._vpc, self._route_table, self._internet_gateway, self._subnets])

    def create_subnets(self, subnets_params):
        for subnet_p in subnets_params:
            self.create_subnet(cidr_block=subnet_p['cidr_block'], availability_zone=subnet_p['availability_zone'],
                               subnet_name=subnet_p['subnet_name'])

    def associate_subnets_list_with_route_table(self):
        for subnet in self._subnets:
            self.associate_subnet_with_route_table(subnet)

    def _debug_resources_status(self):
        # security group

        report = self._client.describe_network_interfaces(
            Filters=[{'Name': 'group-id', 'Values': [self._security_group_manager.id]}])

        short_report = report['NetworkInterfaces'][0]['Association']
        self._logger.debug(short_report)

        # subnets
        for subnet in self.subnets:
            self._logger.debug(
                self._client.describe_network_interfaces(Filters=[{'Name': 'subnet-id', 'Values': [subnet.id]}]))

        # ineternet-gateway
        self._logger.debug(self._client.describe_internet_gateways(
            Filters=[{'Name': 'internet-gateway-id', 'Values': [self._internet_gateway.id]}]))

        # route table
        self._logger.debug(self._client.describe_route_tables(
            Filters=[{'Name': 'route-table-id', 'Values': [self._route_table.id]}]))

        self._logger.debug(self._client.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [self._vpc.id]}]))
        self._logger.debug(
            self._client.describe_network_interfaces(Filters=[{'Name': 'vpc-id', 'Values': [self._vpc.id]}]))
