import json
import os

import psycopg2
import psycopg2.extras

import requests


def handler(event, _):
    body = {"error": "internal server error"}
    response = {
        "isBase64Encoded": False,
        "statusCode": 500,
        "headers": {},
        "body": json.dumps(body),
    }

    try:
        db = json.loads(event["body"])
    except Exception as e:
        print(e)
        body["error"] = "body is not valid JSON"
        response["statusCode"] = 400
        response["body"] = json.dumps(body)
        return response

    if "username" not in db or "scores" not in db:
        print("Body is missing a key")
        body["error"] = "body is missing required key: 'username' or 'scores'"
        response["statusCode"] = 400
        response["body"] = json.dumps(body)
        return response

    try:
        conn = psycopg2.connect("")
    except Exception as e:
        print("Couldn't connect to DB: %s" % e)
        body["error"] = "couldn't connect to database"
        response["body"] = json.dumps(body)
        return response

    cur = conn.cursor()

    print("Processing '%s'" % db["username"])
    result = name_to_id(cur, db["username"])
    if result is None:
        body["error"] = "couldn't get a user from %s" % db["username"]
        response["body"] = json.dumps(body)
        return cleanup(conn, cur, response, conn.rollback)
    user_id, username = result

    cur.execute("select shash from scores where player_id = %d" % user_id)
    exists = {s[0]: True for s in cur.fetchall()}
    tuples = []
    for s in db["scores"]:
        if s["shash"] in exists:  # The replay file hash is unique.
            continue
        # Some scores appear to be missing the username. Ignore these so that
        # we don't accidentally credit someone with a score they didn't make.
        if not s["player"]:
            continue
        # Other player's scores appear here too if the user has downloaded
        # replays, so ignore scores whose names don't match.
        if s["player"] != username:
            continue

        exists[s["shash"]] = True
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
        body["error"] = "error inserting values into database"
        response["body"] = json.dumps(body)
        return cleanup(conn, cur, response, conn.rollback)
    else:
        print("Added %d scores" % len(tuples))

    body["nscores"] = len(tuples)
    body["error"] = ""
    response["statusCode"] = 200
    response["body"] = json.dumps(body)
    return cleanup(conn, cur, response, conn.commit)


def name_to_id(cur, name):
    """
    Get a player's user ID from their name. Returns the ID and username.
    Additionally, this handles inserting new users and updating names
    when necessary.
    """
    cur.execute("select id from players where username = '%s'" % name)
    result = cur.fetchone()
    if result:
        return result[0], name

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
    flag = body[0]["country"]

    cur.execute("select username from players where id = %d" % user_id)
    result = cur.fetchone()
    if result:  # Name change.
        cur.execute(
            "update players set username = '%s' where id = %d" %
            (username, user_id),
        )
    else:
        sql = """\
        insert into players (id, username, flag) values (%d, '%s', '%s')
        """ % (user_id, username, flag)
        cur.execute(sql)

    return user_id, username


def cleanup(conn, cur, resp, func):
    """Undo or commit changes to the DB."""
    func()
    cur.close()
    conn.close()
    return resp
