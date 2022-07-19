from logger_project import logger
from botocore.exceptions import ClientError
import json
from boto3 import s3


def create_bucket(bucket_name, s3_resource):
    """
    bucket_name: a string 
    s3_resource: a S3 resource created
    logger: logger instance
    """
    try:
        bucket = s3_resource.Bucket(bucket_name)
        response = bucket.create(
            ACL = 'private',
            CreateBucketConfiguration ={
                'LocationConstraint' : 'ap-south-1'
            }
        )
        logger.info(f"Created bucket {bucket_name}")
    except ClientError:
        logger.exception(f"Couldn't create the {bucket_name} bucket")
        raise
    else: 
        return response


def delete_bucket(bucket_name, s3_resource):
    """
    bucket_name: a string 
    s3_resource: a S3 resource created
    logger: logger instance
    """
    try:
        bucket = s3_resource.Bucket(bucket_name)
        response = bucket.delete()
        logger.info(f"Deleted bucket {bucket_name}")

    except ClientError:
        logger.exception(f"Couldn't delete the {bucket_name} bucket")
        raise
    else:
        return response

