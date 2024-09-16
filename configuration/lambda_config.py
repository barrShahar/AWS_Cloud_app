
FUNCTION_NAME = 'S3UnzipperFunction'
ZIP_FILE_URL = 'https://ap-southeast-1-tcprod.s3.ap-southeast-1.amazonaws.com/courses/ILT-TF-100-TECESS/v5.5.8.prod-3b017a1e/lab-3/scripts/sample-photos.zip'
ROLE_NAME = 'LambdaS3AccessRole'

RUNTIME = 'python3.9'
HANDLER = 'lambda_function.lambda_handler'
TIMEOUT = 60
MEMORY_SIZE = 128

LAMBDA_CLIENT_CREATE_FUNCTION = {
    'Runtime': RUNTIME,
    'Handler': HANDLER,
    'Timeout': TIMEOUT,
    'MemorySize': MEMORY_SIZE
}


lambda_code = """
import urllib
import boto3
import zipfile
import io
import os

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    dest_bucket = os.environ['DEST_BUCKET']
    zip_file_url = os.environ['ZIP_FILE_URL']

    # Download the zip file
    try:
        response = urllib.request.urlopen(zip_file_url)
        zip_data = response.read()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error downloading zip file: {str(e)}"
        }

    # Unzip the content and upload to S3
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as z:
            for file_info in z.infolist():
                file_name = file_info.filename
                file_data = z.read(file_name)
                # Upload each file to S3
                s3.put_object(Bucket=dest_bucket, Key=file_name, Body=file_data)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error processing zip file: {str(e)}"
        }

    return {
        'statusCode': 200,
        'body': f"Files from {zip_file_url} successfully extracted and uploaded to {dest_bucket}"
    }
            """