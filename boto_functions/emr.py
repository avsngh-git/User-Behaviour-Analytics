from botocore.exceptions import ClientError
import json
from logger_project import logger


def create_cluster(client, name, key_name, instance_role, emr_role):
    """Creates an emr cluster
    Hardcoded ReleaseLabel: Version of EMR release, change if needed
    Hardcoded Instances: InstanceGroups: Name, Market, InstanceRole, InstanceType, InstanceCount, EBSconfiguration """

    try:
        response = client.run_job_flow(
            Name=name,
            LogUri='string',
            ReleaseLabel='emr-6.7.0',
            Instances={
                'InstanceGroups': [
                    {
                        'Name': 'master',
                        'Market': 'SPOT',
                        'InstanceRole': 'MASTER',
                        'InstanceType': 'm5.xlarge',
                        'InstanceCount': 1,
                        'EbsConfiguration': {
                            'EbsBlockDeviceConfigs': [
                                {
                                    'VolumeSpecification': {
                                        'VolumeType': 'gp2',
                                        'SizeInGB': 32,
                                        
                                    },
                                    'VolumesPerInstance': 2
                                },
                            ]
                        },
                    },
                    {
                        'Name': 'core',
                        'Market': 'SPOT',
                        'InstanceRole': 'CORE',
                        'InstanceType': 'm5.xlarge',
                        'InstanceCount': 2,
                        'EbsConfiguration': {
                            'EbsBlockDeviceConfigs': [
                                {
                                    'VolumeSpecification': {
                                        'VolumeType': 'gp2',
                                        'SizeInGB': 32,
                                        
                                    },
                                    'VolumesPerInstance': 2
                                },
                            ]
                        },
                    }
                ],
                'Ec2KeyName': key_name,
                'KeepJobFlowAliveWhenNoSteps': False,
                'TerminationProtected': False
            },
            Applications=[
                {
                    'Name': 'spark',
                    
                    
                },
            ],
            
            JobFlowRole=instance_role,
            ServiceRole=emr_role,
            
            
            ScaleDownBehavior='TERMINATE_AT_TASK_COMPLETION'
        )
        logger.info(f'created an emr cluster {name}')
    except ClientError:
        logger.info(f'failed to create an emr cluster {name}')
        raise
    else:
        return response
