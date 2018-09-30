import datetime
import json
import os
import osuapi

from api import database, players, scores


application_json = {"Content-Type": "application/json"}
text_plain = {"Content-Type": "text/plain"}
datefmt = "%Y-%m-%d %H:%M:%S"
osu = osuapi.OsuApi(
    os.getenv("OSU_API_KEY"), connector=osuapi.connectors.ReqConnector()
)


def _user_id(name):
    """Gets a user's user ID."""
    u = osu.get_user(name)
    return u[0].user_id if u else None


def _int(val, default):
    """Parses val to an int, and returns default if it's not an int."""
    try:
        return int(val)
    except ValueError:
        return default


def _stringify(x):
    """Stringifies all values in a dict, or list of dicts."""
    if isinstance(x, list):
        return [_stringify(y) for y in x]

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


def _response(status, body):
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


empty = _response(200, [])


def get_score_hashes(event, context):
    """
    Handler for /client/get_score_hashes/{user}.
    Returns a list of replay hashes for each score by the user already stored.
    """
    if not event["pathParameters"] or not event["pathParameters"].get("user"):
        return _response(400, "missing required path parameter 'username'")
    username = event["pathParameters"]["user"].strip()
    user_id = _user_id(username)
    if user_id is None:
        return _response(400, "user does not exist")

    sess = database.session()
    put_new_player(sess, user_id, username)
    hashes = scores.get_score_hashes(sess, user_id)
    sess.commit()

    return _response(200, hashes)


def put_scores(event, context):
    """
    Handler for /client/put_scores/{user}.
    Inserts scores sent by the user.
    """
    if not event["pathParameters"] or not event["pathParameters"].get("user"):
        return _response(400, "missing required path parameter 'username'")
    username = event["pathParameters"]["user"]
    user_id = _user_id(username)
    if user_id is None:
        return _response(400, "user does not exist")

    return _response(500, "TODO")


def get_scores(event, context):
    """
    Handler for /client/get_scores.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_scores
    """
    if not event["queryStringParameters"]:
        return empty
    b = _int(event["queryStringParameters"].get("b"), None)
    if not b:
        return empty

    u = event["queryStringParameters"].get("u")
    m = _int(event["queryStringParameters"].get("m", 0), 0)
    mods = _int(event["queryStringParameters"].get("mods"), None)
    type = event["queryStringParameters"].get("type")
    if type != "id" and type != "string":
        type = None
    limit = min(max(_int(event["queryStringParameters"].get("limit", 50), 50), 1), 100)

    sess = database.session()
    scores = scores.get_scores(sess, b, u=u, m=m, mods=mods, type=type, limit=limit)
    sess.close()

    return _response(200, scores)


def get_user_x(event, context, lookup_function):
    if not event["queryStringParameters"]:
        return empty
    u = event["queryStringParameters"].get("u")
    if not u:
        return empty

    m = _int(event["queryStringParameters"].get("m", 0), 0)
    limit = min(max(int(event["queryStringParameters"].get("limit", 10), 10), 1), 100)
    type = event["queryStringParameters"].get("type")
    if type != "id" and type != "string":
        type = None

    sess = database.session()
    scores = lookup_function(sess, u, m=m, limit=limit, type=type)
    sess.close()

    return _response(200, user_best)


def get_user_best(event, context):
    """
    Handler for /client/get_user_best.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_user_best
    """
    return get_user_x(event, context, scores.get_user_best)


def get_user_recent(event, context):
    """
    Handler for /client/get_user_recent.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_user_recent
    """
    return get_user_x(event, context, scores.get_user_recent)


def mapset_maintenance(event, context):
    """
    Cleans up the mapset error queue.
    """
    return {"message": "TODO", "event": event}
