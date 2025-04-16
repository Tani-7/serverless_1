import asyncio
import os
import aioboto3
from .data_validation import transform_row, sanitize_csv
from .error_handler import handle_error
from .models import InputSchema

PROCESSED_BUCKET = os.getenv('PROCESSED_BUCKET')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 10))


async def process_single_file(s3_client, record):
    try:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        response = await s3_client.get_object(Bucket=bucket, Key=key)
        content = await response['Body'].read()
        cleaned = sanitize_csv(content)

        transformed = [transform_row(row)
                       for row in csv.DictReader(cleaned.splitlines())]

        await s3_client.put_object(
            Bucket=PROCESSED_BUCKET,
            Key=f"processed/{key.split('/')[-1]}",
            Body='\n'.join([json.dumps(row) for row in transformed])
        )
        return True
    except Exception as e:
        await handle_error(e, bucket, key)
        return False


async def handler(event, context):
    async with aioboto3.Session().client('s3') as s3_client:
        semaphore = asyncio.Semaphore(MAX_WORKERS)
        tasks = [process_with_limit(s3_client, record)
                 for record in event['Records']]
        results = await asyncio.gather(*tasks)
    return {'processed': sum(results), 'failed': len(results) - sum(results)}
