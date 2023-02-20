import json, boto3, os
from botocore.vendored import requests

codecommit = boto3.client('codecommit')
codepipeline = boto3.client('codepipeline')
domain = os.environ['domain']
region = os.environ['region']
webhook =  os.environ['webhook']
color = None
pipeline_name = os.environ['pipeline_name']
image = os.environ['image_url']

def lambda_handler(event, context):
    # Repository detail
    references_raw = { reference['ref'] for reference in event['Records'][0]['codecommit']['references'] }
    reference = str(references_raw).replace("'","").replace("{","").replace("}","").split("/")
    commit_raw = { reference['commit'] for reference in event['Records'][0]['codecommit']['references'] }
    long_commit_id = str(commit_raw).replace("'","").replace("{","").replace("}","")
    short_commit_id = long_commit_id[0:6]
    repository_raw = event['Records'][0]['eventSourceARN'].split(':')[5]
    repository = codecommit.get_repository(repositoryName=repository_raw)['repositoryMetadata']['repositoryName']
    commit_message = codecommit.get_commit(commitId=long_commit_id,repositoryName=repository)['commit']['message']

    # Get Deploy Stage status on CodePipeline
    deploy_status = codepipeline.get_pipeline_state(name=pipeline_name)['stageStates'][1]['actionStates'][0]['latestExecution']['status']
    if deploy_status == "Succeeded":
        color = "#ffff00"
    elif deploy_status == "Failed":
        color = "#FF0000"
    elif deploy_status == "Cancelled" or deploy_status == "Stopped":
        color = "#FFA500"

    payload = {
            "cards": [
                {
                    "header": {
                        "title": "CodePipeline",
                        "subtitle": "Deploy Job",
                        "imageUrl": f"{image}",
                        "imageStyle": "IMAGE"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": f"<b>Domain: </b>{domain}<br><b>Commit-id:</b> <a href=https://{region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repository}/commit/{long_commit_id}?region={region}>{short_commit_id}</a><br><b>Message: </b>{commit_message}<br><b>Status: </b> <font color=\"{color}\">{deploy_status}</font><br>"
                                    },
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "Pipeline Details",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": f"https://{region}.console.aws.amazon.com/codesuite/codepipeline/pipelines/local-minc-connect-pipeline-ec2/view?region={region}"
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    try:
        #print(f"Repo Name: {repository}")
        #print(f"Branch: {reference[2]}")
        #print(f"Long Commit: {long_commit_id}")
        #print(f"Short Commit: {short_commit_id}")
        #print(f"Message: {commit_message}")
        #print(f"Payload: {payload}")
        #print(response)
        #print(deploy_status)
        response = requests.post(webhook, json=payload)

    except Exception as e:
        print(e)
        print('Error getting repository {}. Make sure it exists and that your repository is in the same region as this function.'.format(repository))
        raise e