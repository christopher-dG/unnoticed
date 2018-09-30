import datetime
import json
import os
import osuapi

from api.database import DBSession

application_json = {"Content-Type": "application/json"}
text_plain = {"Content-Type": "text/plain"}
datefmt = "%Y-%m-%d %H:%M:%S"
osu = osuapi.OsuApi(
    os.getenv("OSU_API_KEY"), connector=osuapi.connectors.ReqConnector()
)


def _stringify(d):
    """Stringifies all values in a dict."""
    d = d.copy()
    for k, v in d.items():
        print(k)
        if isinstance(v, float) or isinstance(v, int):
            d[k] = str(v)
        elif isinstance(v, bool):
            d[k] = str(int(v))
        elif isinstance(v, datetime.datetime):
            d[k] = v.strftime(datefmt)
    return d


def _user_id(name):
    """Gets a user's user ID."""
    u = osu.get_user(name)
    return u[0].user_id if u else None


def _response(status, body=None):
    """Returns an HTTP response."""
    if body is None:
        return {"statusCode": status, "body": ""}
    elif isinstance(body, list) or isinstance(body, dict):
        return {
            "statusCode": status,
            "headers": application_json,
            "body": json.dumps(_stringify(body)),
        }
    else:
        return {"statusCode": status, "headers": text_plain, "body": body}


def get_score_hashes(event, context):
    """
    Handler for /client/get_score_hashes/{user}.
    Returns a list of replay hashes for each score by the user already stored.
    """
    user = event["pathParameters"]["user"]
    if user is None:
        return _response(400, "missing required path parameter 'username'")

    user_id = _user_id(user)
    if user_id is None:
        return _response(400, "user does not exist")

    return _response(500, [])


def put_scores(event, context):
    """
    Handler for /client/put_scores/{user}.
    Inserts scores sent by the user.
    """
    user = event["pathParameters"]["user"]
    if user is None:
        return _response(400, "missing required path parameter 'username'")

    user_id = _user_id(user)
    if user_id is None:
        return _response(400, "user does not exist")

    return _response(500, "TODO")


def get_scores(event, context):
    """
    Handler for /client/get_scores.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_scores
    """
    return _response(500, [])


def get_user_best(event, context):
    """
    Handler for /client/get_user_best.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_user_best
    """
    return _response(500, [])


def get_user_recent(event, context):
    """
    Handler for /client/get_user_recent.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_user_recent
    """
    return _response(500, [])


def mapset_maintenance(event, context):
    """
    Cleans up the mapset error queue.
    """
    return {"message": "TODO", "event": event}
