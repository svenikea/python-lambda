import boto3
import json

def get_push_info(function_name):
    codepipeline = boto3.client('codepipeline')
    response = codepipeline.list_pipeline_executions(
        pipelineName=function_name,
        maxResults=1  # Adjust this value if you want to fetch more executions
    )
    if 'pipelineExecutionSummaries' in response and len(response['pipelineExecutionSummaries']) > 0:
        #print(response)
        long_commit_id = response['pipelineExecutionSummaries'][0]['sourceRevisions'][0]['revisionId']
        short_commit_id = long_commit_id[0:6]
        revision_sumary = json.loads(response['pipelineExecutionSummaries'][0]['sourceRevisions'][0]['revisionSummary'])
        commit_message = revision_sumary['CommitMessage']
    return long_commit_id, short_commit_id, commit_message