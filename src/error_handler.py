import aioboto3
import json


async def handle_error(error: Exception, bucket: str, key: str):
    async with aioboto3.Session().client('s3') as s3:
        # Move to quarantine
        await s3.copy_object(
            CopySource={'Bucket': bucket, 'Key': key},
            Bucket=f"{bucket}-quarantine",
            Key=key
        )
        await s3.delete_object(Bucket=bucket, Key=key)

    # Log metrics
    async with aioboto3.Session().client('cloudwatch') as cw:
        await cw.put_metric_data(
            Namespace='ETL/Errors',
            MetricData=[{
                'MetricName': 'ProcessingErrors',
                'Value': 1,
                'Dimensions': [{'Name': 'ErrorType', 'Value': error.__class__.__name__}]
            }]
        )
