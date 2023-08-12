import boto3
import time

current_milli_time = lambda: int(round(time.time() * 1000))
cloudwatch_logs = boto3.client('logs')

def push_log (log_group,log_stream,content):
    log_event = {
        'timestamp': current_milli_time(),
        'message': content
    }
    # Put the log event to the log stream
    #print(f"Push Log to {log_group}")
    response = cloudwatch_logs.put_log_events(
        logGroupName=log_group,
        logStreamName=log_stream,
        logEvents=[log_event]
    )

def check_logstream_exsited (log_group):
    logstream_name = cloudwatch_logs.describe_log_streams(
        logGroupName=log_group,
        descending = True,
        orderBy='LastEventTime'
    )
    #print(logstream_name['logStreams'][0]['logStreamName'])
    filtered_logstream_name = logstream_name['logStreams'][0]['logStreamName']
    #print (f"Latest logstream from console: {filtered_logstream_name}")
    return filtered_logstream_name

def create_new_logstream (log_group,logstream):
    cloudwatch_logs.create_log_stream(
        logGroupName=log_group, 
        logStreamName=logstream
    )