import boto3
from configuration.config import REGION
from configuration import s3_config, dynamodb_config
import AwsDataResources
from utils.NameGeneratorDNS import generate_unique_dns_name
from AwsDataResources.DataInterfaces.RDSInterface import RDSInterface


class RDSManager(RDSInterface):

    def __init__(self, resources: dict[str, RDSInterface], logger):
        self._logger = logger
        self._resource = resources

    def setup(self) -> dict:
        rds_runtime_params = {}
        for name, res in self._resource.items():
            try:
                res_runtime_params = {name: res.setup()}
                rds_runtime_params = {**res_runtime_params, **rds_runtime_params}
            except Exception as e:
                self._logger.error(f"Couldn't setup {name}: {e}")
                raise

        return rds_runtime_params

    def clean_resources(self) -> bool:
        """
        clean_up all AWS Data resources
        :return: boolean (if the operation was successful)
        """
        is_resources_cleaned = True
        for name, res in self._resource.items():
            try:
                res.clean_resources()
            except Exception as e:
                self._logger.error(f"Couldn't clean resource {name}: {e}")
                is_resources_cleaned = False

        return is_resources_cleaned

