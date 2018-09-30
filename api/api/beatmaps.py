from sqlalchemy.orm import load_only

from api.database import DBSession, Beatmap


def put_beatmaps(sess, beatmaps):
    """Inserts the given beatmaps."""
    # TODO: Will this take too much memory? Maybe not, 1,000,000 * 32 is just 32MB.
    md5s = {
        b.file_md5: True
        for b in sess.query(Beatmap).options(load_only("beatmap_md5")).all()
    }

    new = 0
    for b in beatmaps:
        if b.file_md5 in md5s:
            continue

        new += 1
        sess.add(Beatmap(beatmap_id=b["beatmap_id"], file_md5=b["file_md5"]))

    return new


def beatmap_from_md5(sess, md5):
    """Gets a beatmap from its MD5. Returns None if not found."""
    return sess.query(Beatmap).filter(Beatmap.file_md5 == md5).first()
