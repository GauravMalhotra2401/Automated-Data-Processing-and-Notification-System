import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs_client = boto3.client('sqs')
sqs_queue_url = "https://sqs.us-east-1.amazonaws.com/058264373160/movie-recommendation-queue"


def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        logger.info(f"Received Movie data: {body}")
        print(f"Message Body : {body}")

        try:
            receipt_handle = record['receiptHandle']  # Correct case here
            sqs_client.delete_message(
                QueueUrl=sqs_queue_url,
                ReceiptHandle=receipt_handle  # Correct case here
            )
            logger.info(f"Message deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting message: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully')
    }