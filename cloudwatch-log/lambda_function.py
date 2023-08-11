import json
import urllib.parse
import boto3
import gzip
import os
import cloudwatch
import datetime
import random
import string
import json, requests

current_milli_time = lambda: int(round(time.time() * 1000))

s3 = boto3.client('s3')

log_group_name = None
cloudwatch_logs = boto3.client('logs')

bucket_location = os.environ['BUCKET_LIST'].split(",")

# Generate the current date in the format: YYYY/MM/DD
current_date = datetime.datetime.now().strftime('%Y/%m/%d')

# Generate a random string of 10 characters
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
# Combine the elements to create the final string
new_log_stream_name = f"{current_date}/[$LATEST]{random_string}"
old_log_stream_name = None

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    s3event = event['Records'][0]['eventName']
    print(event['Records'][0]['s3']['configurationId'])
    print("Get Object")
    response = s3.get_object(Bucket=bucket, Key=key)
    compressed_content = response['Body'].read()
    decompressed_content = gzip.decompress(compressed_content).decode('utf-8')

    if bucket == bucket_location[0]:
        log_group_name = "TestLambdaCentralLog"
        # Check log stream before creating it 
        filtered_old_logstream_name = cloudwatch.check_logstream_exsited(log_group_name)
        if filtered_old_logstream_name != new_log_stream_name:
            cloudwatch_logs.create_log_stream(
                logGroupName=log_group_name, 
                logStreamName=new_log_stream_name
            )
            print(f"LogStream {new_log_stream_name} created")
            cloudwatch.push_log(log_group_name, new_log_stream_name, decompressed_content)
        else:
            # Create a log event
            print(f"LogStream {filtered_old_logstream_name} existed")
            cloudwatch.push_log(log_group_name, filtered_old_logstream_name, decompressed_content)
    else:
        print("Pushing to other log group")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


