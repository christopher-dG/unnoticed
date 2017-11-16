import json
import os
import psycopg2


def handler(event, _):
    body = {
        "info": "",
        "error": "internal server error",
        "nscores": 0,
        "scores": {},
    }
    response = {
        "isBase64Encoded": False,
        "statusCode": 500,
        "headers": {},
        "body": json.dumps(body),
    }

    try:
        param_b = str(event["queryStringParameters"]["b"])
    except KeyError:
        print("Missing parameter b")
        response["statusCode"] = 400
        body["info"] = "b must be an integer or comma-separated integers"
        body["error"] = "missing parameter b"
        response["body"] = json.dumps(body)
        return response

    id_strings = param_b.split(",")
    map_ids = []
    for map_id in id_strings:
        try:
            map_ids.append(int(map_id))
        except ValueError:
            body["info"] = "one or more values for b is not an integer"

    if not map_ids:
        print("No valid integer values in parameter b=%s" % param_b)
        response["statusCode"] = 400
        body["info"] = "b must be an integer or comma-separated integers"
        body["error"] = "invalid value for parameter b"
        response["body"] = json.dumps(body)
        return response

    print("Processing %s" % map_ids)

    try:
        conn = psycopg2.connect(
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
        )
    except Exception as e:
        print("Couldn't connect to DB: %s" % e)
        body["info"] = str(e)
        body["error"] = "couldn't connect to database"
        response["body"] = json.dumps(body)
        return response

    cur = conn.cursor()

    for map_id in set(map_ids):
        # The map_id key here will be converted to a string, unfortunately.
        body["scores"][map_id] = []
        sql = """\
        select player_id, mode, player, n300, n100, n50, ngeki, nkatu, nmiss, \
        score, combo, fc, mods, date from scores where map = %d\
        """ % map_id
        cur.execute(sql)

        for score in cur.fetchall():
            d = {}
            (
                d["player_id"], d["mode"], d["player"], d["n300"], d["n100"],
                d["n50"], d["ngeki"], d["nkatu"], d["nmiss"], d["score"],
                d["combo"], d["fc"], d["mods"], d["date"],
            ) = score
            body["scores"][map_id].append(d)
            body["nscores"] += 1

    response["statusCode"] = 200
    body["error"] = ""
    response["body"] = json.dumps(body)

    print("Returning %d total scores for %s" % (body["nscores"], map_ids))
    return response
