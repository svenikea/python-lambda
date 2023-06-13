import boto3
import json

def update_pipeline_job_status(job_id, job_status, message):
    client = boto3.client('codepipeline')
    if job_status == "FAILED":
        print("Failed Debug Function")
        client.put_job_failure_result(jobId=job_id, failureDetails={'message': message, 'type': 'JobFailed'})
    else:
        print("Success Debug Function")
        client.put_job_success_result(jobId=job_id)

def get_userparameters(event):
    raw_json = json.loads(event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters'])
    pipelinename = None
    repositoryname = None 
    branchname = None
    decoded_user = json.loads(raw_json)
    print(f"converted: {decoded_user}")
    pipelinename = decoded_user['pipeline_name']
    repositoryname = decoded_user['repository_name']
    branchname = decoded_user['branch_name']
    organization = decoded_user['organization']
    return pipelinename, repositoryname, branchname, organization