import os
from AwsDataResources.DataInterfaces.RDSInterface import RDSInterface
from utils.Logger import Logger
from configuration.s3_config import DEFAULT_S3_BUCKETS_REGION
from AwsDataResources.DataInterfaces.IS3Policy import IS3Policy


class S3Manager(RDSInterface):
    def __init__(self, s3, s3_client, bucket_name, region, logger: Logger):
        self.bucket_dns_name = bucket_name
        self._logger = logger
        self._region = region
        self._s3_client = s3_client
        self._s3_resource = s3
        # self._s3_client = boto3.client('_s3_resource')
        # self.s3_s3_resource = boto3.resources('_s3_resource')

    def get_bucket_name(self):
        return self.bucket_dns_name

    def setup(self) -> dict:
        """
        Creates an S3 bucket in the specified region.
        """
        try:
            # Check if the region is the default region for S3 buckets
            if self._region == DEFAULT_S3_BUCKETS_REGION:
                # Create the bucket in the default region
                self._s3_client.create_bucket(
                    Bucket=self.bucket_dns_name,
                )
            else:
                # Create the bucket in the specified region with a location constraint
                self._s3_client.create_bucket(
                    Bucket=self.bucket_dns_name,
                    CreateBucketConfiguration={'LocationConstraint': self._region}
                )

            # Log success message if the bucket is created successfully
            self._logger.info(f"Successfully created bucket {self.bucket_dns_name}")

            return {'Name': self.bucket_dns_name}

        except Exception as e:
            # Catch any exceptions that occur during bucket creation and log an error message
            self._logger.error(f"Failed to create bucket {self.bucket_dns_name}: {str(e)}")
            raise  # Re-raise the exception after logging it

    @property
    def bucket_arn(self):
        return f"arn:aws:s3:::{self.bucket_dns_name}"

    def attach_bucket_policy(self, s3_policy: IS3Policy):
        try:
            self._s3_client.put_bucket_policy(
                Bucket=self.bucket_dns_name,
                Policy=s3_policy.generate_policy()
            )

            self._logger.info(f"Successfully attached bucket policy to {self.bucket_dns_name}")

        except Exception as e:
            self._logger.error(f"Failed to attach bucket policy to {self.bucket_dns_name}: {str(e)}")
            self._logger.error(f"The policy:\n{s3_policy.generate_policy()}")
            raise

    def upload_images(self, photos_directory, file_extension=".png"):
        """
        Uploads all PNG images from the specified directory to the S3 bucket.

        Args:
            photos_directory (str): The directory containing the images to be uploaded.
            :param file_extension:
        """
        try:
            # Iterate over all files in the specified directory
            for file_name in os.listdir(photos_directory):
                # Check if the file has a .png extension
                if file_name.endswith(file_extension):
                    # Upload the file to the S3 bucket
                    self._s3_client.upload_file(
                        Filename=os.path.join(photos_directory, file_name),
                        Bucket=self.bucket_dns_name,
                        Key=file_name
                    )
            # Log success message after all images have been uploaded
            self._logger.info("Successfully uploaded images to the S3 bucket")

        except Exception as e:
            # Catch any exceptions that occur during the upload process and log an error message
            self._logger.error(f"Failed to upload images to the S3 bucket: {str(e)}")
            raise  # Re-raise the exception after logging it

    def delete_all_objects(self, delete_versions=True):
        try:
            bucket = self._s3_resource.Bucket(self.bucket_dns_name)
            bucket.objects.all().delete()
            if delete_versions:
                bucket.object_versions.all().delete()  # Delete all object versions (if versioning is enabled)
            self._logger.info(f"Successfully deleted all objects from {self.bucket_dns_name}")
            return True
        # except boto3.exceptions.S3DeleteError as e:
        #     self._loggers.error(f"Failed to delete objects from {self.bucket_dns_name}: {str(e)}")
        #     return False
        except Exception as e:
            self._logger.error(f"Failed to delete objects from bucket {self.bucket_dns_name}: {str(e)}")
            return False

    def delete_bucket(self):
        try:
            # Delete the S3 bucket
            self._s3_client.delete_bucket(Bucket=self.bucket_dns_name)

            self._logger.info(f"Successfully deleted bucket {self.bucket_dns_name}")
            return True

        except Exception as e:
            # Catch any exceptions that occur during the bucket deletion and log an error message
            self._logger.error(f"Failed to delete bucket {self.bucket_dns_name}: {str(e)}")
            return False

    def clean_resources(self, delete_all_versions=True) -> bool:
        return self.delete_all_objects(delete_all_versions) and self.delete_bucket()
