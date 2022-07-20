# User-Behaviour-Analytics
An End to End Data flow Project to analyze user behavior using the spending behavior of a customer and his movie reviews Using Apache Spark, AWS S3, AWS Redshift, AWS EMR and Apache Airflow.

## boto_functions package
Contains a bunch of modules having functions to interact with various AWS services by performing actions. The modules are separated by the service.
* iam_functions module contains functions to interact with AWS's Identity and Authentication Management system(IAM) without which any service or identity doesn't have any permissions
* s3_fucntions has fucntions to interact with S3 datalake
* logger has a logger for use in our script
