import datetime
import json
import os
import osuapi
import re
import requests_cache

# Headers for API responses.
_application_json = {"Content-Type": "application/json"}
_text_plain = {"Content-Type": "text/plain"}
# Format to render datetimes with.
_datefmt = "%Y-%m-%d %H:%M:%S"
# Windows ticks since the Unix epoch, and Windows ticks per second.
_epoch_ticks = 621_355_968_000_000_000
_ticks_per_s = 10_000_000
# Regex to capture the user JSON from the osu! site.
_user_json_re = re.compile(
    re.escape('<script id="json-user" type="application/json">')
    + "(.*?)"
    + re.escape("</script>")
)
# Cached session so that we don't repeat API calls.
_sess = requests_cache.CachedSession(backend="memory")
# osu! API client.
_osu = osuapi.OsuApi(
    os.getenv("OSU_API_KEY"), connector=osuapi.connectors.ReqConnector(sess=_sess)
)
# Mapping of mods to their bit.
_mods = {
    "": 0,
    "NF": 1,
    "EZ": 2,
    "TD": 4,
    "HD": 8,
    "HR": 16,
    "SD": 32,
    "DT": 64,
    "RX": 128,
    "HT": 256,
    "NC": 512,
    "FL": 1024,
    "AT": 2048,
    "SO": 4096,
    "AP": 8192,
    "PF": 16384,
    "4K": 32768,
    "5K": 65536,
    "6K": 131_072,
    "7K": 262_144,
    "8K": 524_288,
    "FI": 1_048_576,
    "RD": 2_097_152,
    "LM": 4_194_304,
    "9K": 16_777_216,
    "10K": 33_554_432,
    "1K": 67_108_864,
    "3K": 134_217_728,
    "2K": 268_435_456,
    "V2": 536_870_912,
}


def parse(body: str):
    """Parses the request body."""
    try:
        return json.loads(body)
    except Exception as e:
        print(f"parsing error: {e}")
        return None


def from_winticks(n: int):
    """Converts a number of Windows ticks to a datetime."""
    # Algorithm found here: http://www.tickstodatetime.com/
    return datetime.datetime.fromtimestamp(round((n - _epoch_ticks) / _ticks_per_s))


def has_mod(score: dict, mod: str):
    """Checks if a given mod was used for a score."""
    if not isinstance(score.get("enabled_mods"), int):
        return None
    m = _mods.get(mod)
    if m is None:
        return False
    return score.enabled_mods & m == m


def osu_id(username: str):
    """Gets a user's user ID."""
    u = _osu.get_user(username)
    return u[0].user_id if u else None


def osu_beatmap_md5(beatmap_id: int):
    """Gets a beatmap's MD5 (from the osu! API)."""
    if beatmap_id is None:
        return None
    b = _osu.get_beatmaps(beatmap_id=beatmap_id)
    return b[0].file_md5 if b else None


def osu_previous_usernames(user_id: int):
    """Get a user's previous usernames."""
    resp = _sess.get(f"https://osu.ppy.sh/users/{user_id}")
    # Get the user's web page.
    if resp.status_code != 200:
        return []
    # Search it for the JSON data.
    match = _user_json_re.search(resp.text.replace("\n", ""))
    if not match:
        return []
    # Load that data.
    try:
        d = json.loads(match.group(1))
    except:
        return []
    # Return the previous usernames.
    return d.get("previous_usernames", [])


def get_int(val: str, default):
    """Parses val to an int, and returns default if it's not an int."""
    try:
        return int(val)
    except ValueError:
        return default


def stringify(x):
    """Stringifies all values in a dict, or list of dicts."""
    if isinstance(x, list):
        return [stringify(y) for y in x]

    d = d.copy()
    for k, v in d.items():
        print(k)
        if isinstance(v, float) or isinstance(v, int):
            d[k] = str(v)
        elif isinstance(v, bool):
            d[k] = str(int(v))
        elif isinstance(v, datetime.datetime):
            d[k] = v.strftime(_datefmt)
    return d


def response(status: int, body):
    """Returns an HTTP response."""
    if body is None:
        return {"statusCode": status, "body": ""}
    elif isinstance(body, list) or isinstance(body, dict):
        return {
            "statusCode": status,
            "headers": _application_json,
            "body": json.dumps(stringify(body)),
        }
    else:
        return {"statusCode": status, "headers": _text_plain, "body": body}


def accuracy(score: dict):
    """Computes the accuracy of a score."""
    mode = score.get("mode")
    n300 = score.get("count300")
    n100 = score.get("count100")
    n50 = score.get("count50")
    geki = score.get("countgeki")
    katu = score.get("counkatu")
    miss = score.get("countmiss")
    if any(not isinstance(x, int) for x in [mode, n300, n100, n50, geki, katu, miss]):
        return None
    if mode < 0 or mode > 3:
        return None

    if mode == 0:
        a = (n300 + n100 / 3 + n50 / 6) / (n300 + n100 + n50 + geki + katu + miss)
    elif mode == 1:
        a = (n300 + n100 / 2) / (c300 + c100 + miss)
    elif mode == 2:
        a = (c300 + c100 + c50) / (c300 + c100 + c50 + katu + miss)
    elif mode == 3:
        a = (geki + n300 + 2 * katu / 3 + n100 / 3 + count50 / 6) / (
            geki + n300 + katu + n100 + n50 + nmiss
        )
    return 100 * a


def grade(score: dict):
    """Computes the letter grade of a score."""
    mods = score["mode"]
    mode = score.get("mode")
    n300 = score.get("count300")
    n100 = score.get("count100")
    n50 = score.get("count50")
    miss = score.get("countmiss")
    acc = _accuracy(score)
    if any(not isinstance(x, int) for x in [mods, mode, n300, n100, n50, miss]):
        return None
    if not isinstance(acc, float):
        return None

    rank = "D"
    if mode == 0:
        total = n300 + n100 + n50 + miss
        p300 = n300 / total
        if acc == 100:
            rank = "X"
        elif p300 > 0.9 and n50 / total < 0.01 and miss == 0:
            rank = "S"
        elif p300 > 0.8 and miss == 0 or p300 > 0.9:
            rank = "A"
        elif p300 > 0.7 and miss == 0 or p300 > 0.8:
            rank = "B"
        elif p300 > 0.6:
            rank = "C"
    elif mode == 1:
        if acc == 100:
            rank = "X"
        elif acc > 95 and miss == 0:
            rank = "S"
        elif acc > 90:
            rank = "A"
        elif acc > 80:
            rank = "B"
        elif acc > 70:
            rank = "C"
    elif mode == 2:
        if acc == 100:
            rank = "X"
        elif acc > 98:
            rank = "S"
        elif acc > 94:
            rank = "A"
        elif acc > 90:
            rank = "B"
        elif acc > 85:
            rank = "C"
    elif mode == 3:
        if acc == 100:
            rank = "X"
        elif acc > 95:
            rank = "S"
        elif acc > 90:
            rank = "A"
        elif acc > 80:
            rank = "B"
        elif acc > 70:
            rank = "C"

    if (rank == "X" or rank == "S") and (has_mod(score, "HD") or has_mod(score, "FL")):
        rank += "H"

    return rank
