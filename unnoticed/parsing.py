from os.path import join
from time import sleep

from .models import Beatmap, Score, DB
from .util import DBROOT, log, notify


BYTE = 1
SHORT = 2
INT = 4
SINGLE = 4
LONG = 8
DOUBLE = 8


def readn(f, n):
    """Read an n-byte number (zero precision) from f."""
    return int.from_bytes(f.read(n), "little")


def readbool(f):
    """Read a boolean from f."""
    return bool(readn(f, BYTE))


def readuleb(f):
    """Read and decode a ULEB128 number from f."""
    # https://en.wikipedia.org/wiki/LEB128#Decode_unsigned_integer
    n, shift = 0, 0
    while True:
        byte = readn(f, BYTE)
        n |= (byte & 0x7f) << shift
        if not byte & 0x80:
            break
        shift += 7
    return n


def readstring(f):
    """Read a variable-length string from f."""
    if not readn(f, BYTE):
        return ""
    return f.read(readuleb(f)).decode("utf-8")


def readscore(f):
    """Read a single Score from f."""
    d = {}
    d["mode"] = readn(f, BYTE)
    d["date"] = readn(f, INT)
    d["md5"] = readstring(f)
    d["player"] = readstring(f)
    d["replay"] = readstring(f)
    d["n300"] = readn(f, SHORT)
    d["n100"] = readn(f, SHORT)
    d["n50"] = readn(f, SHORT)
    d["ngeki"] = readn(f, SHORT)
    d["nkatu"] = readn(f, SHORT)
    d["nmisses"] = readn(f, SHORT)
    d["score"] = readn(f, INT)
    d["combo"] = readn(f, SHORT)
    d["fc"] = readbool(f)
    d["mods"] = readn(f, INT)
    readstring(f)
    d["timestamp"] = readn(f, LONG)
    readn(f, INT)
    d["id"] = readn(f, LONG)
    return Score(d)


def readscores(f):
    """Read all scores for a single beatmap from f."""
    md5 = readstring(f)
    nscores = readn(f, INT)
    log.debug("Parsing %d score(s) for beatmap %s" % (nscores, md5))
    scores = [readscore(f) for _ in range(nscores)]
    if not all(score.md5 == md5 for score in scores):
        log.warn("At least one score for %s has a mismatched MD5" % md5)
    return {"md5": md5, "scores": scores}


def scoresdb():
    """Return all scores in scores.db as a lit of dicts: [{md5, [scores]}]."""
    # ~1.2s on my laptop for 2000 maps, 6000 scores.
    notify("Processing scores...")
    sleep(1)  # Helps to make sure the notifications stay in order.
    with open(join(DBROOT, "scores.db"), "rb") as f:
        v = readn(f, INT)
        log.debug("scores.db version: %d" % v)
        nmaps = readn(f, INT)
        log.debug("scores.db contains %d beatmaps" % nmaps)
        scores = [readscores(f) for _ in range(nmaps)]
        if len(scores) != nmaps:
            log.warn(
                "%d != %d: nmaps does not match number of parsed beatmaps" %
                (nmaps, len(scores))
            )
    return list(filter(lambda s: s["scores"], scores))


def readbeatmap(f, v):
    """Read a single beatmap from f. v is the version datestamp."""
    d = {}
    size = readn(f, INT)
    start = f.tell()
    try:
        d["artist"] = readstring(f)
        readstring(f)
        d["title"] = readstring(f)
        readstring(f)
        d["creator"] = readstring(f)
        d["diff"] = readstring(f)
        readstring(f)
        d["md5"] = readstring(f)
        readstring(f)
        d["status"] = readn(f, BYTE)
        readn(f, SHORT * 3)
        readn(f, LONG)
        if v < 20140609:
            readn(f, BYTE * 4)
        else:
            readn(f, SINGLE * 4)
        readn(f, DOUBLE)
        if v >= 20140609:
            for _ in range(4):
                readn(f, 14 * readn(f, INT))
        readn(f, INT * 3)
        readn(f, 17 * readn(f, INT))
        d["id"] = readn(f, INT)  # This seems to not always be correct.
        readn(f, INT * 2)
        readn(f, BYTE * 4)
        readn(f, SHORT)
        readn(f, SINGLE)
        d["mode"] = readn(f, BYTE)
    except Exception as e:
        log.error("Failed to parse beatmap at position %d: %s", start, e)
        return None
    else:
        return Beatmap(d)
    finally:
        f.seek(start + size)


def osudb():
    """Return a generator of beatmaps in osu!.db."""
    notify("Processing beatmaps...")
    with open(join(DBROOT, "osu!.db"), "rb") as f:
        v = readn(f, INT)
        readn(f, INT)
        readbool(f)
        readn(f, LONG)
        readstring(f)
        nmaps = readn(f, INT)
        log.debug("osu!.db contains %d beatmaps" % nmaps)
        return list(filter(
            lambda b: b, [readbeatmap(f, v) for _ in range(nmaps)]
        ))


def username():
    """Get the player's username."""
    with open(join(DBROOT, "osu!.db"), "rb") as f:
        readn(f, INT)
        readn(f, INT)
        readbool(f)
        readn(f, LONG)
        return readstring(f)


def builddb():
    """Build the beatmap and score container."""
    return DB(username(), osudb(), scoresdb())
