from api import database, players, scores, utils


# Empty OK response.
# The osu! API returns this instead of a 400 when you give bad input,
# so we'll replicate that behaviour.
empty = utils.response(200, [])


def get_score_hashes(event, context):
    """
    Handler for /client/get_score_hashes/{username}.
    Returns a list of replay hashes for each score by the user already stored.
    """
    # Get the username parameter.
    if not event["pathParameters"] or not event["pathParameters"].get("username"):
        return utils.response(400, "missing required path parameter 'username'")
    username = event["pathParameters"]["username"].strip()
    print(f"username: {username}")
    # Get the osu! user ID from that username.
    user_id = utils.osu_id(username)
    print(f"user ID: {user_id}")
    if user_id is None:
        return utils.response(400, "user does not exist")

    database.connect()
    sess = database.session()
    # If the player does not already exist in the database, insert it.
    # This also deals with name changes.
    players.put_new_player(sess, user_id, username)
    # Get the MD5 of all scores by the user.
    hashes = scores.get_score_hashes(sess, user_id)
    sess.commit()

    return utils.response(200, {"user_id": user_id, "scores": hashes})


def put_scores(event, context):
    """
    Handler for /client/put_scores/{user}.
    Inserts scores sent by the user.
    """
    # Get the user ID parameter.
    if not event["pathParameters"] or not event["pathParameters"].get("user_id"):
        return utils.response(400, "missing required path parameter 'user_id'")
    # Parse the request body.
    body = utils.parse(event["body"])
    if body is None:
        return utils.response(400, "invalid request body")
    # Check the client version.
    version = body.get("version")
    if version is None:
        print("missing body parameter 'version'")
    else:
        print(f"version: {version}")
    # Get the scores from the body.
    scores = body.get("scores")
    if scores is None:
        return utils.response(400, "missing required body parameter 'scores'")
    # Get the beatmaps from the body.
    beatmaps = body.get("beatmaps")
    if beatmaps is None:
        return utils.response(400, "missing required body parameter 'beatmaps'")
    user_id = event["pathParameters"]["user_id"]
    print(f"user ID: {user_id}")

    database.connect()
    sess = session()
    # No need to put_new_player here, because calling this endpoint always comes
    # after get_score_hashes which inserts the player if necessary.
    # Insert the beatamps.
    n = beatmaps.put_beatmaps(sess, beatmaps)
    print(f"inserted {n} new beatmap{'' if n == 0 else 's'}")
    # Insert the scores.
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
    # Get the beatmap parameter (required).
    if not event["queryStringParameters"]:
        return empty
    b = utils.get_int(event["queryStringParameters"].get("b"), None)
    if not b:
        return empty

    # Get the mode parameter (optional, default 0 for standard).
    m = utiils.get_int(event["queryStringParameters"].get("m", 0), 0)
    # Get the user parameter (optional, default none for any user).
    u = event["queryStringParameters"].get("u")
    # Get the mods parameter (optional, default none for any mod).
    mods = utils.get_int(event["queryStringParameters"].get("mods"), None)
    # Get the type parameter (optional, default none for autodetection).
    type = event["queryStringParameters"].get("type")
    if type != "id" and type != "string":
        type = None
    # Get and bound the limit parameter (optional, default 50, minimum 1, maximum 100).
    limit = min(
        max(utils.get_int(event["queryStringParameters"].get("limit", 50), 50), 1), 100
    )

    database.connect()
    sess = database.session()
    # Get scores by the given parameters.
    scores = scores.get_scores(sess, b, u=u, m=m, mods=mods, type=type, limit=limit)
    sess.close()

    return utils.response(200, scores)


def _get_user_x(event, context, lookup_function):
    """
    Gets scores for a given user by some function
    (likely either scores.get_user_best or scores.get_user_recent).
    """
    # Get the user parameter (required).
    if not event["queryStringParameters"]:
        return empty
    u = event["queryStringParameters"].get("u")
    if not u:
        return empty

    # Get the mode parameter (optional, default 0 for standard).
    m = utils.get_int(event["queryStringParameters"].get("m", 0), 0)
    # Get and bound the limit parameter (optional, default 50, minimum 1, maximum 100).
    limit = min(
        max(utils.get_int(event["queryStringParameters"].get("limit", 10), 10), 1), 100
    )
    # Get the type parameter (optional, default none for autodetection).
    type = event["queryStringParameters"].get("type")
    if type != "id" and type != "string":
        type = None

    database.connect()
    sess = database.session()
    # Get scores by the given parameters with the given lookup function.
    scores = lookup_function(sess, u, m=m, limit=limit, type=type)
    sess.close()

    return utils.response(200, user_best)


def get_user_best(event, context):
    """
    Handler for /client/get_user_best.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_user_best
    """
    return _get_user_x(event, context, scores.get_user_best)


def get_user_recent(event, context):
    """
    Handler for /client/get_user_recent.
    Follows the osu! API spec:
    https://github.com/ppy/osu-api/wiki#apiget_user_recent
    """
    return _get_user_x(event, context, scores.get_user_recent)
