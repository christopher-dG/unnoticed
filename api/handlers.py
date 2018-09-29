import json

application_json = {"Content-Type": "application/json"}
text_plain = {"Content-Type": "text/plain"}


def get_score_hashes(event, context):
    """
    Handler for /client/get_score_hashes.
    Returns a list of replay hashes for each score by the user already stored.
    """
    body = []
    return {
        "headers": application_json,
        "statusCode": 500,
        "body": json.dumps(body),
    }


def put_scores(event, context):
    """
    Handler for /client/put_scores.
    Inserts scores sent by the user.
    """
    return {
        "headers": text_plain,
        "statusCode": 500,
        "body": "TODO",
    }


def get_scores(event, context):
    """
    Handler for /client/get_scores.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_scores
    """
    body = []
    return {
        "headers": application_json,
        "statusCode": 200,
        "body": json.dumps(body),
    }


def get_user_best(event, context):
    """
    Handler for /client/get_user_best.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_user_best
    """
    body = []
    return {
        "headers": application_json,
        "statusCode": 200,
        "body": json.dumps(body),
    }


def get_user_recent(event, context):
    """
    Handler for /client/get_user_recent.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_user_recent
    """
    body = []
    return {
        "headers": application_json,
        "statusCode": 200,
        "body": json.dumps(body),
    }


def beatmap_maintenance(event, context):
    """
    Cleans up the beatmap error queue.
    """
    return {
        "message": "TODO",
        "event": event,
    }
