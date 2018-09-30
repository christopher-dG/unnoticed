from sqlalchemy.orm import load_only

from api.database import DBSession, Beatmap


def put_beatmaps(sess, beatmaps):
    """Inserts the given beatmaps. Returns the number of new beatmaps inserted."""
    # Get a map of beatmap MD5s so we can check for preexisting maps in constant time.
    md5s = {
        b.file_md5: True
        for b in sess.query(Beatmap).options(load_only("file_md5")).all()
    }

    # Add beatmaps that don't already exist, keeping count of the new ones.
    new = 0
    for b in beatmaps:
        if b["file_md5"] in md5s:
            continue
        new += 1
        md5s[b["file_md5"]] = True
        sess.add(Beatmap(beatmap_id=b["beatmap_id"], file_md5=b["file_md5"]))

    return new


def beatmap_from_md5(sess, md5):
    """Gets a beatmap from its MD5. Returns None if not found."""
    return sess.query(Beatmap).filter(Beatmap.file_md5 == md5).first()
