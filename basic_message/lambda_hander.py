import json, boto3, math, os
from botocore.vendored import requests
codecommit = boto3.client('codecommit')
domain = os.environ['domain']
region = os.environ['region']
webhook =  os.environ['webhook']
def lambda_handler(event, context):
    # TODO implement

    references_raw = { reference['ref'] for reference in event['Records'][0]['codecommit']['references'] }
    reference = str(references_raw).replace("'","").replace("{","").replace("}","").split("/")
    commit_raw = { reference['commit'] for reference in event['Records'][0]['codecommit']['references'] }
    long_commit_id = str(commit_raw).replace("'","").replace("{","").replace("}","")
    short_commit_id = long_commit_id[0:6]

    
    # print(f"Branch: {references[2]}")
    # print(f"Commit-ID: {short_commit_id}")
    
    #Get the repository from the event and show its git clone URL
    repository_raw = event['Records'][0]['eventSourceARN'].split(':')[5]
    repository = codecommit.get_repository(repositoryName=repository_raw)['repositoryMetadata']['repositoryName']
    commit_message = codecommit.get_commit(commitId=long_commit_id,repositoryName=repository)['commit']['message']
    #message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    payload = {"text" : f"<users/all> {domain} commit: *<https://{region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repository}/commit/{long_commit_id}?region={region}|{short_commit_id}>* message: {commit_message}"}
    try:
        #response = codecommit.get_repository(repositoryName=repository)
        print(f"Repo Name: {repository}")
        print(f"Reference: {reference[2]}")
        print(f"Long Commit: {long_commit_id}")
        print(f"Short Commit: {short_commit_id}")
        print(f"Message: {commit_message}")
        print(f"Payload: {payload}")
        requests.post(webhook, json=payload)
        #print("Clone URL: " +response['repositoryMetadata']['cloneUrlHttp'])
        # return response['repositoryMetadata']['cloneUrlHttp']
        #requests.post(webhook, json=payload)
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
