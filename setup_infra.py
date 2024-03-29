from platform import node
from sqlite3 import connect
from venv import create
from botocore.exceptions import ClientError
from boto_functions.ec2_functions import create_key_ec2
from boto_functions.s3functions import create_bucket
from boto_functions.ec2_functions import create_key_ec2, create_security_group, get_my_ip, attach_egress, attach_ingress, create_instance
from boto_functions.iam_functions import create_role, attach_policy, create_instance_profile, add_role_instance
from boto_functions.emr import create_cluster
from boto_functions.redshift_functions import create_redshift_cluster, run_sql_commands
import boto3
from boto_functions.logger_project import logger
from fabric.connection import Connection
import subprocess

def ssh_ec2_connection(host_ip:str):
    connect = Connection(host=host_ip, user='ubuntu', port=22, connect_kwargs={'key_filename':'/home/avinash/data/test.pem'})
    return connect

def copy_to_ec2(host_ip):
    """Zips all the code in the project to be copied to EC2 instance via SSH
    After it is copied it is unzipped to be ready for use"""
    try:
        subprocess.run(['zip', '-r', 'user_analytics', './../User-Behaviour-Analytics']) # Zips all the code
        ssh_connection = ssh_ec2_connection(host_ip=host_ip) #calls the ssh_ec2_connection function to create a connection object
        ssh_connection.open() #opens the connection using the connection object attributes
        ssh_connection.run(command='mkdir user_behaviour_analytics')
        ssh_connection.put('user_analytics.zip', 'user_behaviour_analytics/') #puts the zip file into the folder we created on the remote server

        ssh_connection.run(command='sudo apt-get install unzip') #need to install unzip for unzipping
        ssh_connection.run(command='unzip user_analytics.zip -d user_behaviour_analytics/')
        logger.info('copied to ec2 and unzipped successfully')
    except ClientError:
        logger.info('failed to copy and unzip to ec2 instance')
        raise







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

    #lets use the instance as an service resource
    instance = ec2_instance.Instance(instance_id)
    host_ip = instance.public_ip_address #ip address of the lanched instance

    #Zipping and then copying the code to the EC2 Instance and then unzipping it there for use
    copy_to_ec2(host_ip=host_ip)
   
    

    #Creating an EMR cluster to run hadoop and spark for processing
    emr = boto3.client('emr')
    cluster_name = 'project_cluster'
    key_name = 'emr_ec2_project1'
    emr_ec2_key = create_key_ec2(ec2=ec2, key_name=key_name)
    emr_cluster = create_cluster(client=emr, name=cluster_name, key_name=key_name, instance_role='EMR_EC2_DefaultRole', emr_role='EMR_Service_Role' )
    emr_id = emr_cluster['JobFlowId']
    # Waiter will wait till cluster is operational
    emr_waiter = emr.get_waiter('cluster_running')
    emr_waiter.wait(ClusterId=emr_id)

    # Creating Redshift Cluster
    redshift_client = boto3.client('redshift')
    redshift_role_name = 'redshift-role-project1'
    redshift_service = ['redshift.amazonaws.com']
    redshift_role = create_role(role_name=redshift_role_name, allowed_services=redshift_service, iam=iam_resource)
    attach_policy(role_name=redshift_role_name, policy_arn='arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess', iam=iam_resource)
    attach_policy(role_name=redshift_role_name, policy_arn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess', iam=iam_resource)
    redshift_role_arn = redshift_role.arn
    cluster_identifier = 'redshift-project-1'
    cluster_type = 'single-node'
    node_type = 'dc2.large'
    redshift_cluster = create_redshift_cluster(client=redshift_client, cluster_identifier=cluster_identifier, cluster_type=cluster_type, 
        node_type=node_type, master_username='redshift-user-project-1', master_password='redshift-project-1', iam_role_arn=redshift_role_arn )
    # Adding a waiter to wait till the cluster is created
    redshift_cluster_waiter = redshift_client.get_waiter('cluster_available')
    redshift_cluster_waiter.wait(ClusterIdentifier=cluster_identifier)

    #creating databases and required tables in redshift
    sql_statements = (open("./redshiftsetup/setup.sql", 'r')).read().split(';')
    run_sql_commands(redshift_client, cluster_identifier, sql_statements)
