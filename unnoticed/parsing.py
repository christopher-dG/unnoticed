from time import sleep

from .models import Score
from .util import log, notify


BYTE = 1
SHORT = 2
INT = 4
LONG = 8


def readn(f, n):
    """Read an n-byte number from f."""
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
        n |= byte & 0x3f << shift
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


def readbeatmap(f):
    """Read all scores for a single beatmap from f."""
    md5 = readstring(f)
    nscores = readn(f, INT)
    log.debug("Parsing %d score(s) for beatmap %s" % (nscores, md5))
    scores = [readscore(f) for _ in range(nscores)]
    if not all(score.md5 == md5 for score in scores):
        log.warn("At least one score for %s has a mismatched MD5" % md5)
    return {"md5": md5, "scores": scores}


def processdb(filename):
    """Return all scores as a list of dicts."""
    # ~1.2s on my laptop for 2000 maps, 6000 scores.
    notify("Processing new scores...")
    sleep(1)  # Helps to make sure the notifications stay in order.
    with open(filename, "rb") as f:
        v = readn(f, INT)
        log.debug("scores.db version: %d" % v)
        nmaps = readn(f, INT)
        log.debug("scores.db contains %d beatmaps" % nmaps)
        scores = [readbeatmap(f) for _ in range(nmaps)]
        if len(scores) != nmaps:
            log.warn(
                "%d != %d: nmaps does not match number of parsed beatmaps" %
                (nmaps, len(scores))
            )
    return scores
