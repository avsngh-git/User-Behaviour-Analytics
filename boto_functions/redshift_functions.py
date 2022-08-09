from botocore.exceptions import ClientError
import json
from logger_project import logger

def create_redshift_cluster(client, cluster_identifier, cluster_type, node_type, master_username, master_password, iam_role_arn):
    """Creates an AWS Redshift Cluster"""
    try:
        cluster = client.create_cluster(
            ClusterIdentifier=cluster_identifier,
            ClusterType=cluster_type,
            NodeType=node_type,
            MasterUsername=master_username,
            MasterUserPassword=master_password,  
            AutomatedSnapshotRetentionPeriod=0,
            ManualSnapshotRetentionPeriod=1,
            IamRoles=[
                iam_role_arn
            ],
            Port=5739,          
            PubliclyAccessible=True,
        )
        logger.info(f'redshift cluster {cluster_identifier} was created')
    
    except ClientError:
        logger.info(f'failed to create redshift cluster {cluster_identifier}')
        raise
    else:
        return cluster
    