from api import database, players, scores, utils


empty = utils.response(200, [])


def get_score_hashes(event, context):
    """
    Handler for /client/get_score_hashes/{username}.
    Returns a list of replay hashes for each score by the user already stored.
    """
    if not event["pathParameters"] or not event["pathParameters"].get("username"):
        return utils.response(400, "missing required path parameter 'username'")
    username = event["pathParameters"]["username"].strip()
    print(f"username: {username}")
    user_id = utils.osu_id(username)
    print(f"user ID: {user_id}")
    if user_id is None:
        return utils.response(400, "user does not exist")

    database.connect()
    sess = database.session()
    players.put_new_player(sess, user_id, username)
    hashes = scores.get_score_hashes(sess, user_id)
    sess.commit()

    return utils.response(200, {"user_id": user_id, "scores": hashes})


def put_scores(event, context):
    """
    Handler for /client/put_scores/{user}.
    Inserts scores sent by the user.
    """
    if not event["pathParameters"] or not event["pathParameters"].get("user_id"):
        return utils.response(400, "missing required path parameter 'user_id'")
    body = utils.parse(event["body"])
    if body is None:
        return utils.response(400, "invalid request body")
    version = body.get("version")
    if version is None:
        print("missing body parameter 'version'")
    else:
        print(f"version: {version}")
    scores = body.get("scores")
    if scores is None:
        return utils.response(400, "missing required body parameter 'scores'")
    beatmaps = body.get("beatmaps")
    if beatmaps is None:
        return utils.response(400, "missing required body parameter 'beatmaps'")
    user_id = event["pathParameters"]["user_id"]
    print(f"user ID: {user_id}")

    database.connect()
    sess = session()
    # No need to put_new_player here, because calling this endpoint always comes
    # after get_score_hashes which inserts the player if necessary.
    n = beatmaps.put_beatmaps(sess, beatmaps)
    print(f"inserted {n} new beatmap{'' if n == 0 else 's'}")
    n = scores.put_scores(sess, user_id, scores)
    print(f"inserted {n} new score{'' if n == 0 else 's'}")
    sess.commit()

    return utils.response(200, f"inserted {n} new score{'' if n == 0 else 's'}")


def get_scores(event, context):
    """
    Handler for /client/get_scores.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_scores
    """
    if not event["queryStringParameters"]:
        return empty
    b = utils.get_int(event["queryStringParameters"].get("b"), None)
    if not b:
        return empty

    u = event["queryStringParameters"].get("u")
    m = utiils.get_int(event["queryStringParameters"].get("m", 0), 0)
    mods = utils.get_int(event["queryStringParameters"].get("mods"), None)
    type = event["queryStringParameters"].get("type")
    if type != "id" and type != "string":
        type = None
    limit = min(
        max(utils.get_int(event["queryStringParameters"].get("limit", 50), 50), 1), 100
    )

    database.connect()
    sess = database.session()
    scores = scores.get_scores(sess, b, u=u, m=m, mods=mods, type=type, limit=limit)
    sess.close()

    return utils.response(200, scores)


def get_user_x(event, context, lookup_function):
    if not event["queryStringParameters"]:
        return empty
    u = event["queryStringParameters"].get("u")
    if not u:
        return empty

    m = utils.get_int(event["queryStringParameters"].get("m", 0), 0)
    limit = min(
        max(utils.get_int(event["queryStringParameters"].get("limit", 10), 10), 1), 100
    )
    type = event["queryStringParameters"].get("type")
    if type != "id" and type != "string":
        type = None

    database.connect()
    sess = database.session()
    scores = lookup_function(sess, u, m=m, limit=limit, type=type)
    sess.close()

    return utils.response(200, user_best)


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
