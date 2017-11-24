import io
import json
import math
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
                map_id, d["mode"], d["score"], d["mods"], d["combo"],
                d["n300"], d["n100"], d["n50"], d["ngeki"], d["nkatu"],
                d["nmiss"],
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
        print("API response is missing a required key")
        return None


def get_pp(
        map_id, mode, score, mods, combo, n300, n100, n50, ngeki, nkatu, nmiss,
):
    """Get pp for a play."""
    if mode == 0:
        return std(map_id, mods, combo, n300, n100, n50, nmiss)
    elif mode == 1:
        return taiko(map_id, mods, combo, n300, n100, nmiss)
    elif mode == 2:
        return ctb(map_id, mods, combo, n300, n100, n50, nkatu, nmiss)
    elif mode == 3:
        return mania(
            map_id, score, mods, combo, n300, n100, n50, ngeki, nkatu, nmiss,
        )
    else:
        return None


def std(map_id, mods, combo, n300, n100, n50, nmiss):
    """Get pp for a Standard play."""
    osu = "%d.osu" % map_id
    url = "https://osu.ppy.sh/osu/%s" % map_id
    r = requests.get(url)
    if r.status_code != 200:
        print("Download failed (%d)" % r.status_code)
        return None
    parser = pyttanko.parser()
    with io.StringIO(r.text) as f:
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
    if mods & 2 or mods & 16 or mods & 64 or mods & 256:  # EZ/HR/DT/HT.
        return None  # TODO: Mods.

    url = "https://osu.ppy.sh/api/get_beatmaps?k=%s&b=%d&m=2&a=1&limit=1" % (
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
        sr = float(body[0]["difficultyrating"])
        ar = float(body[0]["diff_approach"])
        max_combo = int(body[0]["max_combo"])
    except KeyError:
        print("API response is missing a required key")
        return None

    acc = (n300 + n100 + n50) / (n300 + n100 + n50 + nkatu + nmiss)

    # The following is translated almost directly from the code in #12.
    pp = pow(((5 * sr / 0.0049) - 4), 2) / 100000
    length_bonus = 0.95 + 0.4 * min(1.0, max_combo / 3000.0)
    if max_combo > 3000:
        length_bonus += math.log10(max_combo / 3000) * 0.5
    pp *= length_bonus
    pp *= pow(0.97, nmiss)
    pp *= pow(combo / max_combo, 0.8)
    if ar > 9:
        pp *= 1 + 0.1 * (ar - 9)
    pp *= pow(acc, 5.5)
    return pp


def mania(map_id, score, mods, combo, n300, n100, n50, ngeki, nkatu, nmiss):
    """Get pp for a Mania play."""
    if mods & 72 or mods & 256:  # DT/HT.
        return None  # TODO: Calculate modded SR.

    url = "https://osu.ppy.sh/api/get_beatmaps?k=%s&b=%d&m=3&a=1&limit=1" % (
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
        sr = float(body[0]["difficultyrating"])
        od = float(body[0]["diff_overall"])
    except KeyError:
        print("API response is missing a required key")
        return None

    # Get the number of hit objects.
    url = "https://osu.ppy.sh/osu/%s" % map_id
    r = requests.get(url)
    if r.status_code != 200:
        print("Download failed (%d)", r.status_code)
        return None
    for i, line in enumerate(r.text.split("\n")):
        if "[HitObjects]" in line:
            break
    else:
        print("HitObjects section was not found")
        return None
    for j, line in enumerate(r.text.split("\n")[i + 1:]):
        if not line:
            break
    nobjs = j

    acc = (ngeki + n300 + 2 * nkatu / 3 + n100/3 + n50/6) / \
          (ngeki + n300 + nkatu + n100 + n50 + nmiss)

    # The following is translated almost directly from the code in #12.
    f = 64 - 3 * od
    k = 2.5 * pow((150 / f) * pow(acc, 16), 1.8) * \
        min(1.15, pow(nobjs / 1500, 0.3))
    l = (pow(5 * max(1, sr / 0.0825) - 4, 3) / 110000) * \
        (1 + 0.1 * min(1, nobjs / 1500))
    if score < 500000:
        m = score / 500000 * 0.1
    elif score < 600000:
        m = (score - 500000) / 100000 * 0.2 + 0.1
    elif score < 700000:
        m = (score - 600000) / 100000 * 0.35 + 0.3
    elif score < 800000:
        m = (score - 700000) / 100000 * 0.2 + 0.65
    elif score < 900000:
        m = (score - 800000) / 100000 * 0.1 + 0.85
    else:
        m = (score - 900000) / 100000 * 0.05 + 0.95
    return pow(pow(k, 1.1) + pow(l * m, 1.1), 1 / 1.1) * 1.1
