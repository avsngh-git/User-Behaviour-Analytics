from boto_functions.s3functions import create_bucket
from boto_functions.iam_functions import create_role, attach_policy, create_instance_profile, add_role_instance
import boto3
from boto_functions.logger_project import logger

if __name__ == '__main__':
    
    region = 'ap-south-1'

    # First create an S3 Resource object to call various actions on
    s3_resource = boto3.resource('s3')

    # Call S3 functions module to create a bucket for me 
    bucket_name = 'batch-project-sr1-19-7-2022'
    create_bucket(bucket_name=bucket_name, s3_resource=s3_resource)


    #Creating role for EC2 to access a bunch of stuff
    # First creating an IAM resource to call actions on
    iam_resource = boto3.resource('iam')

    #Creating a Role for EC2
    service = ['ec2.amazonaws.com']
    role_name = 'ec2-role-project-sr1-19-7-2022'
    ec2_role = create_role(role_name=role_name, allowed_services=service, iam=iam_resource)

    #Attaching Policies to the role

    #Attaching S3 full access policy to EC2 role so it can completely access S3
    s3_policy_arn = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
    attach_policy(role_name=role_name, policy_arn=s3_policy_arn, iam=iam_resource)

    #attach EMR full access policy 
    emr_policy_arn = 'arn:aws:iam::aws:policy/AmazonEMRFullAccessPolicy_v2'
    attach_policy(role_name=role_name, policy_arn=emr_policy_arn, iam=iam_resource)

    #Attaching AmazonRedshiftAllCommandsFullAccess Policy 
    redshift_policy_arn = 'arn:aws:iam::aws:policy/AmazonRedshiftAllCommandsFullAccess'
    attach_policy(role_name=role_name, policy_arn=redshift_policy_arn, iam=iam_resource)
 
    #Creating an intance profile for EC2 instance and the attaching the role we created above to it
    instance_profile_name = 'ec2-role-project-sr1-19-7-2022-instance-profile'
    instance_profile = create_instance_profile(instance_profile_name, iam_resource)

    # Attach the role to the instance profile
    add_role_instance(instance_profile=instance_profile, role_name=role_name)