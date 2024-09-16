from configuration.config import REGION, ACCOUNT_ID

S3_NAME_INITIALS = "sb"
S3_BUCKET_BASE_NAME = "employee-photo-bucket-" + S3_NAME_INITIALS
S3_ROLE_NAME = 'EmployeeWebApp'
DEFAULT_S3_BUCKETS_REGION = 'us-east-1'  # This is always true, don't change!


# def s3_policy(account_id: str, role_name: str, bucket_name: str) -> json:
#     S3_POLICY = {
#         "Version": "2012-10-17",
#         "Statement": [
#             {
#                 "Sid": "AllowS3ReadAccess",
#                 "Effect": "Allow",
#                 "Principal": {
#                     "AWS": f"arn:aws:iam::{account_id}:role/{role_name}"
#                 },
#                 "Action": "_s3_resource:*",
#                 "Resource": [
#                     f"arn:aws:s3:::{bucket_name}",
#                     f"arn:aws:s3:::{bucket_name}/*"
#                 ]
#             }
#         ]
#     }
#     return json.dumps(S3_POLICY)
