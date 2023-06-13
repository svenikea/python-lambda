from botocore.vendored import requests
import os

def send_notification(git_version_control, long_commit_id, short_commit_id, commit_message,job_status, repo, branch, organization, webhook_url, region, pipeline_name):
    pipeline = f"https://{region}.console.aws.amazon.com/codesuite/codepipeline/pipelines/{pipeline_name}/view?region={region}"
    print("Running slack function")
    # Define the Slack webhook URL and message
    if job_status == "SUCCEEDED":
        color = "#009900"
        status = ":tada:"
        print("OK Slack")
    elif job_status == "STARTED":
        color = "#FFFF00"
        status = ":mega:"
        print("Started Slack")
    elif job_status == "FAILED":
        color = "#E45959"
        status = ":poop:"
        print("Failed Slack")
    elif job_status == "STOPPED":
        color = "#FFA500"
        status = ":no_entry_sign:"
        print("Stopped Slack")
    elif job_status == "RESUMED":
        color = "#00FFFF"
        status = ":mega:"
        print("Resumed Slack")
    else:
        color = "#FFFFFF"
        status = ":rotating_light:"
        print("Else Slack")
    
    if git_version_control == "bitbucket":
        git_url = "https://bitbucket.org/"

    if git_version_control == "github":
        git_url = "https://github.com/"
    attachments = [
        {
            "fallback": "Upgrade your Slack client to use messages like these.",
            "color": color,
            "blocks": [
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Resitory*\n{repo.split('/')[-1]}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Branch*\n{branch}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Commit Message*\n{commit_message}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Commit Id*\n<{git_url}{repo}/commits/{long_commit_id}|{short_commit_id}>"
                        }
                    ]
                }
            ]
        }
    ]
    payload = {
        "channel": "#workflow-status",
        "text": f"<!channel>*<{pipeline}|{status} {repo.split('/')[-1]} Deploy {job_status.title()}>*",
        "attachments": attachments
    }

    try:
        # Send the message to Slack
        response = requests.post(webhook_url, json=payload)

        # Check if the message was sent successfully
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {str(e)}")
    
