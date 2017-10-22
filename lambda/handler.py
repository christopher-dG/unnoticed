import json


def handler(event, _):
    """TODO"""
    response = {
        "isBase64Encoded": False,
        "statusCode": 500,
        "headers": {},
        "body": "server error",
    }

    try:
        db = json.loads(event["body"])
    except Exception as e:
        print(e)
        return response

    print(db.keys())
    print(db["username"])

    response["statusCode"] = 200
    response["body"] = "success"

    return response
