import boto3
import os
from os.path import splitext


from .util import notify

# Local development keys until I get Cognito or similar set up,
k = os.environ["KEYID"]
sec = os.environ["SECRETKEY"]
b = "unnoticed"
q = "https://sqs.us-east-1.amazonaws.com/876595393910/unnoticed"


def upload(fn):
    """Upload a file to S3."""
    client = boto3.client(
        "s3",
        aws_access_key_id=k,
        aws_secret_access_key=sec,
    )
    f = open(fn, "rb")
    try:
        return client.put_object(
            Body=f,
            Bucket=b,
            Key=parsefn(fn),
        )
    except Exception as e:
        notify("Uploading scores failed: %s" % e)
        return None
    finally:
        f.close()


def writeq(fn):
    """Write a message to SQS."""
    client = boto3.client(
        "sqs",
        aws_access_key_id=k,
        aws_secret_access_key=sec,
        region_name="us-east-1",
    )
    try:
        return client.send_message(
            QueueUrl=q,
            MessageBody=parsefn(fn),
        )
    except Exception as e:
        notify("Publishing message failed: %s" % e)
        return None


def parsefn(fn):
    """Get the username and timestamp from fn."""
    dt, username = fn.split(":", 1)
    return "%s/%s" % (splitext(username)[0], dt)
