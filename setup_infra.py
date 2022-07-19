from boto_functions.s3functions import create_bucket
import boto3
from boto_functions.logger_project import logger

region = 'ap-south-1'

# First create an S3 Resource object to call various actions on
s3_resource = boto3.resource('s3')

# Call S3 functions module to create a bucket for me 
bucket_name = 'batch-project-sr1-19-7-2022'
create_bucket(bucket_name=bucket_name, s3_resource=s3_resource, logger=logger)