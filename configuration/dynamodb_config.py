from configuration.config import REGION
NAME = "Employees"

# ** see method _create_bucket in AwsDataResources/DynamodbManager.py **
key_schema = [
    {
        'AttributeName': 'id',
        'KeyType': 'HASH'
    }
]
attribute_definitions = [
    {
        'AttributeName': 'id',
        'AttributeType': 'S'
    }
]
provisioned_throughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}
