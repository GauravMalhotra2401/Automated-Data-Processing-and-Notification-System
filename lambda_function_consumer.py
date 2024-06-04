import json
import boto3


def lambda_handler(event, context):

    sqs_client = boto3.client('sqs')
    sqs_queue_url = "https://sqs.us-east-1.amazonaws.com/058264373160/movie-recommendation-queue"

    response = sqs_client.receive_message(
        QueueUrl = sqs_queue_url,
        MaxNumberOfMessages = 1,
        WaitTimeSeconds = 10
    )

    if 'Messages' in response:
        for message in event['Records']:
            body = json.loads(message['body'])

            print(f"Received Movie data : {body}")

            receipt_handle = message['receiptHandle']
            sqs_client.delete_message(
                QueueUrl = sqs_queue_url,
                ReceiptHandle = receipt_handle
            )
    else:
        print("No messages received")

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully')
    }