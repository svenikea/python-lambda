import json, boto3, math, os
from botocore.vendored import requests

codecommit = boto3.client('codecommit')
domain = os.environ['domain']
region = os.environ['region']
webhook =  os.environ['webhook']
color = "#ffff00"
status = "Deploying"
pipeline_name = os.environ['pipeline_name']
image = os.environ['image_url']

def lambda_handler(event, context):
    # TODO implement

    references_raw = { reference['ref'] for reference in event['Records'][0]['codecommit']['references'] }
    reference = str(references_raw).replace("'","").replace("{","").replace("}","").split("/")
    commit_raw = { reference['commit'] for reference in event['Records'][0]['codecommit']['references'] }
    long_commit_id = str(commit_raw).replace("'","").replace("{","").replace("}","")
    short_commit_id = long_commit_id[0:6]

    
    #Get the repository from the event and show its git clone URL
    repository_raw = event['Records'][0]['eventSourceARN'].split(':')[5]
    repository = codecommit.get_repository(repositoryName=repository_raw)['repositoryMetadata']['repositoryName']
    commit_message = codecommit.get_commit(commitId=long_commit_id,repositoryName=repository)['commit']['message']
    #payload = {"text" : f"<users/all> Deploying {domain} commit: *<https://{region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repository}/commit/{long_commit_id}?region={region}|{short_commit_id}>* message: {commit_message}"}
    
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
                                        "text": f"<b>Domain: </b>{domain}<br><b>Commit-id:</b> <a href=https://{region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repository}/commit/{long_commit_id}?region={region}>{short_commit_id}</a><br><b>Branch: </b>{reference[2]}<br><b>Build Status: </b> <font color=\"{color}\">{status}</font><br>"
                                    },
                                    "buttons": [
                                        {
                                            "textButton": {
                                                "text": "Pipeline Details",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://{region}.console.aws.amazon.com/codesuite/codepipeline/pipelines/{pipeline_name}/view?region={region}"
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
        #response = codecommit.get_repository(repositoryName=repository)
        print(f"Repo Name: {repository}")
        print(f"Branch: {reference[2]}")
        print(f"Long Commit: {long_commit_id}")
        print(f"Short Commit: {short_commit_id}")
        print(f"Message: {commit_message}")
        print(f"Payload: {payload}")
        requests.post(webhook, json=payload)
        #print("Clone URL: " +response['repositoryMetadata']['cloneUrlHttp'])
        # return response['repositoryMetadata']['cloneUrlHttp']
        requests.post(webhook, json=payload)
        # print(f"Short Commit: {short_commit_id}")
        # print(f"Long commit: {long_commit_id}")
        # print(f"Message: {commit_message}")

    except Exception as e:
        print(e)
        print('Error getting repository {}. Make sure it exists and that your repository is in the same region as this function.'.format(repository))
        raise e
#    return {
#        'statusCode': 200,
#        'body': json.dumps('Hello from Lambda!')
#    }
