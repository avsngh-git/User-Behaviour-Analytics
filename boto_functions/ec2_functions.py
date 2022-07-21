import string
from botocore.exceptions import ClientError
import json
from logger_project import logger
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

def my_ip():
    ip = subprocess.run(['curl', '-s', 'http://whatismyip.akamai.com/'],stderr=subprocess.PIPE, text=True)
    return ip.stderr
