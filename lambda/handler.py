import json
import os
import psycopg2
import psycopg2.extras
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
        # TODO: Store these somewhere to be retrieved later.
        print("Couldn't get a user ID for %s" % db["username"])
        return cleanup(conn, cur, response, conn.rollback)
    else:
        user_id, exists = result
        if exists:
            cur.execute("select updated from players where id = %d" % user_id)
            result = cur.fetchone()
            if not result:  # This should never happen.
                print(
                    "Couldn't get last update time for %d (%s)" %
                    (user_id, db["username"]),
                )
                return cleanup(conn, cur, response, conn.rollback)
            else:
                last_update = result[0]
        else:  # User is not in the database yet.
            last_update = 0  # We want to upload all scores.
            cur.execute(
                "insert into players values (%d, %s, %d);" %
                (user_id, db["username"], int(time.time())),
            )

    tuples = []
    for s in db["scores"]:
        # Check the date so we can skip any already-uploaded plays.
        # Some scores appear to be missing the username. Ignore these so that
        # we don't accidentally credit someone with a score they didn't make.
        if s["date"] < last_update or not s["name"]:
            continue

        # Other player's scores appear here too, so if the name doesn't match,
        # set the ID to an impossible value. We can periodically clean up
        # scores with missing IDs seperately.
        id_field = user_id if s["name"] == db["username"] else -1

        tuples.append((
            id_field, s["mode"], s["mhash"], s["name"], s["shash"], s["n300"],
            s["n100"], s["n50"], s["ngeki"], s["nkatu"], s["nmiss"],
            s["score"], s["combo"], s["fc"], s["mods"], s["date"], s["map"],
        ))

    sql = """\
    insert into scores (player_id, mode, mhash, name, shash, n300, n100, n50, \
    ngeki, nkatu, nmiss, score, combo, fc, mods, date, map) values %s\
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
    Get a player's user ID from their name. Returns the ID and True
    if the user is already in the database, the ID and False if the user
    is not yet in the database, and None if the user cannot be found at all.
    """
    cur.execute("select id from players where username = '%s';" % name)
    result = cur.fetchone()
    # TODO: Look for user with osu! API. Remember to check the retrieved ID
    # in the DB again in case of a name change.
    return result[0], True if result else None


def cleanup(conn, cur, resp, func):
    """Undo changes to the DB."""
    func()
    cur.close()
    conn.close()
    return resp
