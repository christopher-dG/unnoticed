from time import sleep

from .util import notify


def processdb(filename):
    """Return all new unranked scores."""
    notify("Processing new scores...")
    scores = []
    f = open(filename, "rb")
    f.seek(4 + 4)  # Ignore the first two int fields.
    f.close()
    sleep(1)  # Helps to make sure the notifications stay in order.
    return scores


def readnum(f, n):
    """Read an n-byte integer from f."""
    return int.from_bytes(f.read(n), "little")


def readbool(f):
    """Read a boolean from f."""
    return bool(int.from_bytes(f.read(1)))


def readuleb(f):
    """Read and decode a ULEB128 number from f."""
    # https://en.wikipedia.org/wiki/LEB128#Decode_unsigned_integer
    n, shift = 0, 0
    while True:
        byte = readnum(f, 1)
        n |= byte & 0x3f << shift
        if not byte & 0x80:
            break
        shift += 7
    return n


def readstring(f):
    """Read a variable-length string from f."""
    if not readnum(f, 1):
        return ""
    return f.read(readuleb(f)).decode("utf-8")
