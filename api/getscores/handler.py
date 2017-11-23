import json
import os
import psycopg2
import pyttanko
import requests


def handler(event, _):
    """Retrieve scores for given beatmaps."""
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
        map_hash = get_hash(map_id)
        sql = """\
        select player_id, mode, player, n300, n100, n50, ngeki, nkatu, nmiss, \
        score, combo, fc, mods, date, flag, mhash from scores join players on \
        scores.player_id = players.id where map = %d\
        """ % map_id
        cur.execute(sql)

        for score in cur.fetchall():
            d = {}
            (
                d["player_id"], d["mode"], d["player"], d["n300"], d["n100"],
                d["n50"], d["ngeki"], d["nkatu"], d["nmiss"], d["score"],
                d["combo"], d["fc"], d["mods"], d["date"], d["flag"],
            ) = score[:-1]
            d["outdated"] = map_hash != score[-1]
            d["pp"] = get_pp(
                map_id, d["mode"], d["mods"], d["combo"], d["n300"],
                d["n100"], d["n50"], d["ngeki"], d["nkatu"], d["nmiss"],
            )

            body["scores"][map_id].append(d)
            body["nscores"] += 1

    response["statusCode"] = 200
    body["error"] = ""
    response["body"] = json.dumps(body)

    print("Returning %d total scores for %s" % (body["nscores"], map_ids))
    return response


def get_hash(map_id):
    """Get the MD5 hash of a beatmap's most recent version."""
    print("Requesting beatmap %d" % map_id)
    url = "https://osu.ppy.sh/api/get_beatmaps?k=%s&b=%d&l=1" % (
        os.environ["OSU_API_KEY"], map_id)
    r = requests.get(url)
    if r.status_code != 200:
        print("API request failed (%d)" % r.statusCode)
        return None
    body = json.loads(r.content)
    if not body:
        print("API request returned empty")
        return None
    try:
        return body[0]["file_md5"]
    except KeyError:
        print("API response is missing file_md5 key")
        return None


def get_pp(map_id, mode, mods, combo, n300, n100, n50, ngeki, nkatu, nmiss):
    """Get pp for a play."""
    if mode == 0:
        return std(map_id, mods, combo, n300, n100, n50, nmiss)
    if mode == 1:
        return taiko(map_id, mods, combo, n300, n100, nmiss)
    elif mode == 2:
        return ctb(map_id, mods, combo, n300, n100, n50, nkatu, nmiss)
    elif mode == 3:
        return mania(map_id, mods, combo, n300, n100, n50, ngeki, nkatu, nmiss)
    else:
        return None


def std(map_id, mods, combo, n300, n100, n50, nmiss):
    """Get pp for a Standard play."""
    osu = "%d.osu" % map_id
    url = "https://osu.ppy.sh/osu/%s" % map_id
    response = requests.get(url)
    if response.status_code != 200:
        print("Download failed")
        return None
    with open(osu, "w") as f:
        f.write(response.text)
    parser = pyttanko.parser()
    with open(osu) as f:
        bmap = parser.map(f)
    stars = pyttanko.diff_calc().calc(bmap, mods)
    return pyttanko.ppv2(
        aim_stars=stars.aim, speed_stars=stars.speed, mods=mods, combo=combo,
        n300=n300, n100=n100, n50=n50, nmiss=nmiss, bmap=bmap,
    )[0]


def taiko(map_id, mods, combo, n300, n100, nmiss):
    """Get pp for a Taiko play."""
    return None  # https://github.com/Francesco149/pyttanko/issues/1


def ctb(map_id, mods, combo, n300, n100, n50, nkatu, nmiss):
    """Get pp for a CTB play."""
    return None


def mania(map_id, mods, combo, n300, n100, n50, ngeki, nkatu, nmiss):
    """Get pp for a Mania play."""
    return None
