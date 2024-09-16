import json
from AwsDataResources.DataInterfaces.IS3Policy import IS3Policy


class DefaultBucketPolicy(IS3Policy):
    def __init__(self, account_id: str, role_name: str, bucket_name: str):
        self._bucket_name = bucket_name
        self._role_name = role_name
        self._account_id = account_id

    def generate_policy(self) -> json:
        s3_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowS3ReadAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{self._account_id}:role/{self._role_name}"
                    },
                    "Action": "s3:*",
                    "Resource": [
                        f"arn:aws:s3:::{self._bucket_name}",
                        f"arn:aws:s3:::{self._bucket_name}/*"
                    ]
                }
            ]
        }
        return json.dumps(s3_policy)
