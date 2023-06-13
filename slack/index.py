import json
import repository
import slack
import pipeline
import os
import re
import boto3

print('Loading function')


def lambda_handler(event, context):
    try:
    ####################### Put your Lambda Code Here ###########################
        # Get the CodePipeline job ID and job status from the Lambda event
        pipeline_name = event['detail']['pipeline']
        pipeline_state = event['detail']['state']
        region = event['region']
        pipeline_arn = event['resources'][0]

        codepipeline_client = boto3.client('codepipeline')
        response = codepipeline_client.get_pipeline(name=pipeline_name)
        
        repository_branch = response['pipeline']['stages'][0]['actions'][0]['configuration']['BranchName']
        repository_name = response['pipeline']['stages'][0]['actions'][0]['configuration']['FullRepositoryId']
        
        
        long_commit_id, short_commit_id, commit_message = repository.get_push_info(pipeline_name)
        slack.send_notification(os.environ.get('git_location'),long_commit_id, short_commit_id, commit_message, pipeline_state, repository_name, repository_branch, "zwitch", os.environ.get('webhook_url'), region, pipeline_name)
    ####################### Lambda Code End ###########################
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as e:
        print("Failed Except")
        raise e