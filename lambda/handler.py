import json
import os
import psycopg2
import psycopg2.extras
import requests
import time


def handler(event, _):
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

    try:
        conn = psycopg2.connect(
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
        )
    except Exception as e:
        print("Couldn't connect to DB: %s" % e)
        return response

    cur = conn.cursor()

    result = name_to_id(cur, db["username"])
    if result is None:
        return cleanup(conn, cur, response, conn.rollback)
    user_id, username, exists = result

    if exists:
        cur.execute("select updated from players where id = %d" % user_id)
        result = cur.fetchone()
        if result:
            last_update = result[0]
        else:  # This should never happen.
            last_update = 0  # Upload all scores, we can clean up later.
            print("Couldn't get last update time for player %d" % user_id)
    else:  # User is not in the database yet.
        last_update = 0  # We want to upload all scores.

    tuples = []
    for s in db["scores"]:
        # Any plays older then the last update should be already uploaded.
        if s["date"] < last_update:
            continue
        # Some scores appear to be missing the username. Ignore these so that
        # we don't accidentally credit someone with a score they didn't make.
        if not s["player"]:
            continue
        # Other player's scores appear here too if the user has downloaded
        # replays, so ignore scores whose names don't match.
        if s["player"] != username:
            continue

        tuples.append((
            user_id, s["mode"], s["ver"], s["mhash"], s["player"], s["shash"],
            s["n300"], s["n100"], s["n50"], s["ngeki"], s["nkatu"], s["nmiss"],
            s["score"], s["combo"], s["fc"], s["mods"], s["date"], s["map"],
        ))

    sql = """\
    insert into scores (player_id, mode, ver, mhash, player, shash, n300, n100,
    n50, ngeki, nkatu, nmiss, score, combo, fc, mods, date, map) values %s\
    """

    try:
        psycopg2.extras.execute_values(cur, sql, tuples)
    except Exception as e:
        print("Error inserting values: %s" % e)
        return cleanup(conn, cur, response, conn.rollback)
    else:
        print("Added %d scores" % len(tuples))
        cur.execute(
            "update players set updated = %d where id = %d;" %
            (int(time.time()), user_id),
        )

    response["statusCode"] = 200
    response["body"] = "success"
    return cleanup(conn, cur, response, conn.commit)


def name_to_id(cur, name):
    """
    Get a player's user ID from their name. Returns the ID and username, as
    well as True if the user is already in the database and False otherwise.
    If the usre cannot be found at all, None is returned.
    Additionally, this handles inserting new users and updating names
    when necessary.
    """
    cur.execute("select id from players where username = '%s';" % name)
    result = cur.fetchone()
    if result:
        return result[0], name, True

    url = "https://osu.ppy.sh/api/get_user?k=%s&u=%s&type=string" % (
        os.environ["OSU_API_KEY"], name)
    r = requests.get(url)
    if r.status_code != 200:
        print("API request for %s returned %d" % (name, r.status_code))
        return None
    body = json.loads(r.content)
    if not body:
        print("API request for %s returned empty" % name)
        return None

    user_id = int(body[0]["user_id"])
    username = body[0]["username"]

    cur.execute("select username from players where id = %d;" % user_id)
    result = cur.fetchone()
    if result:  # Name change.
        cur.execute(
            "update players set username = '%s' where id = %d;" %
            (username, user_id),
        )
        return user_id, username, True
    cur.execute(
        "insert into players values (%d, '%s', 0);" %
        (user_id, username),
    )
    return user_id, username, False


def cleanup(conn, cur, resp, func):
    """Undo or commit changes to the DB."""
    func()
    cur.close()
    conn.close()
    return resp
