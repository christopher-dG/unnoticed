import boto3
import os

from .util import notify

# Local development credentials until I get Cognito or similar set up.
k = os.environ["KEYID"]
sec = os.environ["SECRETKEY"]
b = "unnoticed"


def upload(bs, key):
    """Upload a file containing the bytestring bs to S3."""
    client = boto3.client(
        "s3",
        aws_access_key_id=k,
        aws_secret_access_key=sec,
    )
    try:
        return client.put_object(
            Body=bs,
            Bucket=b,
            Key=key,
        )
    except Exception as e:
        notify("Uploading scores failed: %s" % e)
        return None
