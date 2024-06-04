import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Log all messages for debugging

sqs_client = boto3.client('sqs')
sqs_queue_url = "https://sqs.us-east-1.amazonaws.com/058264373160/movie-recommendation-queue"

def lambda_handler(event, context):
    logger.debug(f"Event: {event}")  # Log the entire event object
    logger.debug(f"Context: {context}")  # Log the context object

    response = sqs_client.receive_message(
        QueueUrl=sqs_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    if 'Messages' in response:
        for message in response['Messages']:
            body = json.loads(message['Body'])
            logger.debug(f"Received Message Body: {body}") 

            try:
                receipt_handle = message['ReceiptHandle']
                logger.debug(f"Receipt Handle: {receipt_handle}")

                sqs_client.delete_message(
                    QueueUrl=sqs_queue_url,
                    ReceiptHandle=receipt_handle
                )
                logger.debug(f"Message deleted successfully")

            except Exception as e:
                logger.error(f"Error deleting message: {e}")
    else:
        logger.info("No messages received")

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully')
    }
