import json
import requests
import boto3
import random
import pandas as pd  
import io

API_URL = "https://www.omdbapi.com/"
API_KEY = "ae8ed93"

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')
sns_arn = "arn:aws:sns:us-east-1:058264373160:movie-recommendation"
sqs_queue_url = "https://sqs.us-east-1.amazonaws.com/058264373160/movie-recommendation-queue"

while True:  # Loop until a valid IMDb ID is found
    random_id = "tt" + str(random.randint(1000000, 9999999))

    # Check if the ID exists (using only i and apikey)
    response = requests.get(f"{API_URL}?i={random_id}&apikey={API_KEY}")

    if response.status_code == 200:
        raw_data = response.json()

        if 'Title' in raw_data:  # Check if title is present
            print(raw_data)

            print(raw_data['Title'])
            print(raw_data['Year'])
            print(raw_data['Runtime'])
            print(raw_data['Director'])
            print(raw_data['Actors'])
            print(raw_data['Type'])

            movie_data = {
                "Title":raw_data['Title'],
                "Year":raw_data['Year'],
                "Runtime":raw_data['Runtime'],
                "Director":raw_data['Director'],
                "Actors":raw_data['Actors'],
                "Type":raw_data['Type']
            }

            movies_df = pd.DataFrame([movie_data]) # creating a dataframe

            csv_buffer = io.StringIO()
            movies_df.to_csv(csv_buffer, index = False)   # Convert DataFrame to CSV format

            # Upload CSV to S3
            s3_upload_bucket = "movie-data-s3-bucket"
            s3_upload_object_key = "file.txt"
            s3_client.put_object(Bucket = s3_upload_bucket, Key = s3_upload_object_key, Body = csv_buffer.getvalue())

            # Construct and send SNS message
            message = f"Recommending you a fantabulous {raw_data['Type']} named {raw_data['Title']}, released in the Year {raw_data['Year']}, directed by {raw_data['Director']} starring {raw_data['Actors']}"
            sns_client.publish(
                Subject = f"{raw_data['Type']} : {raw_data['Title']} ✔",
                TargetArn = sns_arn,
                Message = message,
                MessageStructure = 'text'
            )

            # Send JSON data to SQS
            sqs_client.send_message(
                QueueUrl = sqs_queue_url,
                MessageBody = json.dumps(movie_data)
            )

            break  # Exit the loop
        else:
            print("Invalid ID, trying again...")  # Try a new ID
    else:
        print(f"Error: {response.status_code}")
        message = "Can't recommend any Movie/Series at this time. Hold back for some time"
        sns_client.publish(
                Subject = "FAILED - Unable to recommend",
                TargetArn = sns_arn,
                Message = message,
                MessageStructure = 'text'
            )
        break  # Exit the loop