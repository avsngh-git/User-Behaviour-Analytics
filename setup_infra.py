from venv import create
from boto_functions.ec2_functions import create_key_ec2
from boto_functions.s3functions import create_bucket
from boto_functions.ec2_functions import create_key_ec2, create_security_group, get_my_ip, attach_egress, attach_ingress, create_instance
from boto_functions.iam_functions import create_role, attach_policy, create_instance_profile, add_role_instance
from boto_functions.emr import create_cluster
import boto3
from boto_functions.logger_project import logger


if __name__ == '__main__':
    
    region = 'ap-south-1'

    # First create an S3 Resource object to call various actions on
    s3_resource = boto3.resource('s3')

    # Call S3 functions module to create a bucket for me 
    bucket_name = 'batch-project-sr1-19-7-2022'
    create_bucket(bucket_name=bucket_name, s3_resource=s3_resource, acl='public-read-write')


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

    #Now we are going to create an SSH key-value pair to connect to the EC2 instance
    #first we have to create an EC2 resource.
    ec2 = boto3.resource('ec2')

    #now we create the key value pair
    key_name = 'first_project'
    key_pair = create_key_ec2(key_name=key_name, ec2=ec2)

    #Create a security group to only allow access from my ip
    ec2_security_group = create_security_group('ec2-project 1', 'for access to ec2 instance for project 1', ec2)
    ec2_security_group_id = ec2_security_group.group_id

    #get my ip 
    my_ip = get_my_ip()

    #Create Ingress and Egress rules for outbound and inbound access from my ip in the security group created above
    attach_ingress(my_ip=my_ip, security_group=ec2_security_group, group_id=ec2_security_group_id)
    attach_egress(my_ip=my_ip, security_group=ec2_security_group)

    #Create an EC2 instance for processing our data
    ec2_instance = create_instance(ec2=ec2, security_group_id=ec2_security_group_id, instance_profile_name=instance_profile_name, instance_type='t2.large')

    #Lets Get Instance id of the EC2 instance. 
    #create instance function returns a list object and thus we have to do ec2_instance[0] to actually get the instance object and use descrive_attribute action on it
    instance_attr = ec2_instance[0].describe_attribute( 
        Attribute = 'instanceType'
    )
    instance_id = instance_attr['InstanceId']

    #Creating an EMR cluster to run hadoop and spark for processing
    emr = boto3.client('emr')
    cluster_name = 'project_cluster'
    key_name = 'emr_ec2_project1'
    emr_ec2_key = create_key_ec2(ec2=ec2, key_name=key_name)
    emr_cluster = create_cluster(client=emr, name=cluster_name, key_name=key_name, instance_role='EMR_EC2_DefaultRole', emr_role='EMR_Service_Role' )