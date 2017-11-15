import json
import os
import psycopg2


def handler(event, _):
    body = {"error": "unknown server error", "nscores": 0, "scores": []}
    response = {
        "isBase64Encoded": False,
        "statusCode": 500,
        "headers": {},
        "body": json.dumps(body),
    }

    try:
        map_id = event["queryStringParameters"]["b"]
    except KeyError:
        print("Missing parameter b")
        body["error"] = "missing parameter b"
        response["body"] = json.dumps(body)
        return response

    try:
        map_id = int(map_id)
    except ValueError:
        print("Invalid parameter b=%s" % map_id)
        body["error"] = "invalid value for b (need an integer)"
        response["body"] = json.dumps(body)
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
        body["error"] = "couldn't connect to database"
        response["body"] = json.dumps(body)
        return response

    cur = conn.cursor()

    sql = """\
    select player_id, mode, player, n300, n100, n50, ngeki, nkatu, nmiss, \
    score, combo, fc, mods, date) from scores where map = %d
    """ % map_id

    cur.execute(sql)

    for score in cur.fetchall():
        d = {}
        (
            d["player_id"], d["mode"], d["player"], d["n300"], d["n100"],
            d["n50"], d["ngeki"], d["nkatu"], d["nmiss"], d["score"],
            d["combo"], d["fc"], d["mods"], d["date"],
        ) = score
        body["scores"].append(d)
        body["nscores"] += 1

    response["statusCode"] = 200
    body["error"] = ""
    response["body"] = json.dumps(body)

    return response
