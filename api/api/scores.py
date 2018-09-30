from sqlalchemy import desc
from sqlalchemy.orm import load_only

from api.database import Score


def _field(u, type):
    """Determines which field to compare on based on type."""
    type = type.lower()
    if type == "id":
        return Score.user_id
    elif type == "string":
        return Score.username
    else:
        return Score.user_id if isinstance(u, type) else Score.username


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
    pass


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

    return [s.dict() for s in scores]


def get_user_best(sess, user, m=0, limit=10, type=None):
    """Gets a single user's best scores (by pp)."""
    filters = [_field(user, type) == user]
    if mods is not None:
        filters.append(Score.enabled_mods == mods)

    scores = (
        sess.query(Score).filter(*filters).order_by(desc(Score.pp)).limit(limit).all()
    )

    return [s.dict() for s in scores]


def get_user_recent(sess, user, m=0, limit=10, type=None):
    # TODO: Should we limit to the last 24 hours like the official API does?
    scores = (
        sess.query(Score)
        .filter(_field(user, type) == user, Score.mode == m)
        .order_by(desc(Score.date))
    )

    return [s.dict() for s in scores]
