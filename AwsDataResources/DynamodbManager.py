import boto3
from configuration import dynamodb_config
from AwsDataResources.DataInterfaces.RDSInterface import RDSInterface


class DynamodbManager(RDSInterface):
    def __init__(self, dynamodb, dynamodb_client, table_name: str, region: str, logger):
        self._dynamodb_client = dynamodb_client
        self._dynamodb = dynamodb
        self._logger = logger
        self._region = region
        self._table_name = table_name
        self._table = None

    def setup(self) -> dict:
        self.create_table(self._dynamodb)
        return {}

    def _get_dynamodb_table_list(self):
        """Retrieves a list of DynamoDB table names in the specified region.

        Args:
            region (str): The AWS region.

        Returns:
            list: A list of DynamoDB table names.
        """

        response = self._dynamodb_client.list_tables()
        return response['TableNames']

    def _create_table(self, dynamodb):
        return dynamodb.create_table(
            TableName=self._table_name,
            KeySchema=dynamodb_config.key_schema,
            AttributeDefinitions=dynamodb_config.attribute_definitions,
            ProvisionedThroughput=dynamodb_config.provisioned_throughput
        )

    def create_table(self, delete_data_if_table_exist=False):
        try:
            self._dynamodb = boto3.resource('dynamodb', region_name=self._region)
            self._logger.info(f"Checking if table {self._table_name} already exists in region {self._region}")

            try:
                # Attempt to list tables
                table_names = self._get_dynamodb_table_list()
                if self._table_name not in table_names:
                    self._table = self._create_table(self._dynamodb)  # Assuming this method creates the table
                    self._logger.info(f"Table '{self._table_name}' created successfully")
                else:
                    self._logger.info(f"Table {self._table_name} already exists in region {self._region}")
                    self._logger.info(f"Loading {self._table_name}")
                    self._table = self._dynamodb.Table(self._table_name)
                    try:
                        self._table.load()
                    except Exception as e:
                        self._logger.error(f"Failed to load an existing table:{e}")
                        raise
                    if delete_data_if_table_exist:
                        self.delete_data_if_loaded_table_exist()

            except Exception as e:
                self._logger.error(f"Error listing or loading table: {e}")
                raise  # Re-raise the exception for further handling

        except Exception as e:
            self._logger.error(f"Unexpected error creating table: {e}")
            raise  # Re-raise the exception for further handling

    def clean_resources(self) -> bool:
        """
        Deletes DynamoDB table
        :return: None
        """
        if not self._table:
            self._logger.error(f"self.table {self._table_name} is None")
            return

        try:
            self._logger.info(f"Deleting table {self._table_name}")
            self._table.delete()
            self._logger.info(f"Table {self._table_name} deleted successfully")
        except Exception as e:
            self._logger.error(f"Error deleting table: {e}")
            raise

    def delete_data_if_loaded_table_exist(self):
        self.clean_resources()
        self.create_table(delete_data_if_table_exist=True)
