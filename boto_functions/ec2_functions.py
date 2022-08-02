import string
from botocore.exceptions import ClientError
import json
from boto_functions.ec2_functions import logger
import subprocess



def create_key_ec2(key_name, ec2):
    """
    Creates a key pair to connect to ec2 instance
    
    key_name: string
    ec2: ec2 resource instance
    """
    try:
        key_pair = ec2.create_key_pair(
            KeyName=key_name,
            DryRun=True|False,
        
        )
        logger.info(f'created a key pair {key_name} successfully')
    except ClientError:
        logger.exception(f"Couldn't create a key pair {key_pair} ")
        raise
    else:
        return key_pair

def create_security_group(group_name, description, ec2):
    try:
        security_group = ec2.create_security_group(
        Description=description,
        GroupName=group_name,  
        )
        logger.info(f'created a security group {group_name} successfully')
    except ClientError:
        logger.exception(f"Couldn't create a security group {group_name} ")
        raise
    else:
        return security_group

def get_my_ip():
    """Gets my ip by running a bash script using python itself
    return: returns my ip as a string
    """
    process = subprocess.Popen(['curl', '-s', 'http://whatismyip.akamai.com/'],stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ip = process.communicate()
    return ip[0]


def attach_ingress(my_ip, security_group, group_id):
    """ attaches ingress rule, Port is hardcoded, free to edit"""
    cidr = my_ip+'/32'
    response = security_group.authorize_ingress(
        CidrIp=cidr,
        FromPort=23,
        GroupId= group_id,
        IpProtocol='tcp',
        ToPort=23 
    )
    return response

def attach_egress(my_ip, security_group):
    """ attaches egress rule, Port is hardcoded, free to edit"""
    cidr = my_ip+'/32'
    response = security_group.authorize_egress(
        IpPermissions=[
        {
            'FromPort': 8080,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': cidr,
                    'Description': 'my_ip'
                },
            ],
            'ToPort': 8080
        },
    ],
    )


def create_instance(ec2, security_group_id, instance_profile_name, instance_type):
    """ creates an EC2 instance for our computing needs
    Hardcoded: instance number max and min values, OS image_id, volumetype, availability zone, 
    """
    try:
        instance = ec2.create_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sdh',
                    'Ebs': {
                        'DeleteOnTermination': False,
                        'VolumeSize': 8,
                        'VolumeType': 'gp2'
                    }
                }
            ],
            ImageId='ami-08df646e18b182346',
            InstanceType=instance_type,
            MaxCount=1,
            MinCount=1,
            Monitoring={
                'Enabled': False
            },
            SecurityGroupIds=[
                security_group_id
            ],
            IamInstanceProfile={
                'Name': instance_profile_name
            }
        )
    except ClientError:
        raise
    else:
        return instance
