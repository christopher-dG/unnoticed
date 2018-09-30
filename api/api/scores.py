from sqlalchemy import desc
from sqlalchemy.orm import load_only

from api import utils
from api.beatmaps import beatmap_from_md5
from api.database import Beatmap, Score


def _field(u, type):
    """Determines which field to compare on based on type."""
    type = type.lower()
    if type == "id":
        return Score.user_id
    elif type == "string":
        return Score.username
    else:
        return Score.user_id if isinstance(u, type) else Score.username


def _outdated(sess, score):
    """
    Checks if a score is outdated and adds the result to the dict.
    If the current MD5 can't be determined, the value is None.
    """
    md5 = utils.osu_beatmap_md5(score.beatmap_id)
    outdated = None if md5 is None else md5 == score.beatmap_md5
    b = sess.query(Beatmap).get(score["beatmap_id"]).first()
    if b:
        b.file_md5 = md5
    return {**score, "outdated": outdated}


def get_score_hashes(sess, user):
    """Returns the replay hash of every score by user."""
    scores = (
        sess.query(Score)
        .filter(Score.user_id == user)
        .options(load_only("replay_md5"))
        .all()
    )
    return [s.replay_md5 for s in scores]


def put_scores(sess, user, scores):
    """Inserts the given scores. Returns the number of new scores."""
    md5s = {
        s.replay_md5: True
        for s in sess.query(Score)
        .filter(
            Score.user_id == user, Score.replay_md5 in [s["replay_md5"] for s in scores]
        )
        .options(load_only("replay_md5"))
        .all()
    }

    u = sess.query(Player).get(user)
    username = u.username
    prev_usernames = utils.osu_previous_usernames(user)
    new = 0
    for s in scores:
        if s["replay_md5"] in md5s:
            continue
        if s["username"] != username and s["username"] not in prev_usernames:
            continue
        elif s["username"] != username:
            s["username"] = username

        new += 1
        sc = Score.from_dict(s)
        sc.user_id = user
        sc.beatmap_id = beatmap_from_md5(sc.beatmap_md5)
        # Stil leave pp null here, we'll fill it in in the background.
        sess.add(sc)

    return new


def get_scores(sess, beatmap_id, u=None, m=0, mods=None, type=None, limit=50):
    """Returns scores for a given beatmap."""
    filters = [Score.beatmap_id == beatmap_id, Score.mode == m]
    if u is not None:
        filters.append(_field(u, type) == u)
    if mods is not None:
        filters.append(Score.enabled_mods == mods)

    scores = (
        sess.query(Score)
        .filter(*filters)
        .distinct(Score.user_id)
        .order_by(desc(Score.score))
        .limit(limit)
        .all()
    )

    return [_outdated(s.dict()) for s in scores]


def get_user_best(sess, user, m=0, limit=10, type=None):
    """Gets a single user's best scores (by pp)."""
    filters = [_field(user, type) == user]
    if mods is not None:
        filters.append(Score.enabled_mods == mods)

    scores = (
        sess.query(Score).filter(*filters).order_by(desc(Score.pp)).limit(limit).all()
    )

    return [_outdated(s.dict()) for s in scores]


def get_user_recent(sess, user, m=0, limit=10, type=None):
    # TODO: Should we limit to the last 24 hours like the official API does?
    scores = (
        sess.query(Score)
        .filter(_field(user, type) == user, Score.mode == m)
        .order_by(desc(Score.date))
    )

    return [_outdated(s.dict()) for s in scores]
