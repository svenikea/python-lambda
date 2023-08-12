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

evenlist = os.environ['EVENT_LIST'].split(",")
log_group_list = os.environ['LOG_GROUP_LIST'].split(",")

# Generate the current date in the format: YYYY/MM/DD
current_date = datetime.datetime.now().strftime('%Y/%m/%d')

# Generate a random string of 10 characters
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
# Combine the elements to create the final string
new_log_stream_name = f"{current_date}/[$LATEST]{random_string}"
old_log_stream_name = None
target_logstream_name = None
target_log_group = None
log_stream_status = None

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    s3event = event['Records'][0]['s3']['configurationId']
    #print(f"Retrived S3 Event: {s3event}")
    response = s3.get_object(Bucket=bucket, Key=key)
    #print(f"Retrived S3 Object: {key}")
    compressed_content = response['Body'].read()
    #print(f"Unzip the content of {key}")
    decompressed_content = gzip.decompress(compressed_content).decode('utf-8')

    for i, event_type in enumerate(evenlist):
        if s3event == event_type:
            target_log_group = log_group_list[i]
            filtered_old_logstream_name = cloudwatch.check_logstream_exsited(target_log_group)
            if filtered_old_logstream_name != new_log_stream_name:
                cloudwatch.create_new_logstream(target_log_group, new_log_stream_name)
                log_stream_status = True
                #print(f"LogStream {new_log_stream_name} created")
                target_logstream_name = new_log_stream_name
                cloudwatch.push_log(target_log_group, new_log_stream_name, decompressed_content)
            else:
                target_logstream_name = filtered_old_logstream_name
                log_stream_status = False
                #print(f"LogStream {filtered_old_logstream_name} existed")
                cloudwatch.push_log(target_log_group, filtered_old_logstream_name, decompressed_content)

    json_data = {
        "s3-event": s3event,
        "bucket": bucket,
        "object": key,
        "log-group": target_log_group,
        "log-stream": target_logstream_name,
        "new-log-stream": log_stream_status
    }
    return {
        'statusCode': 200,
        'body': json_data
    }
