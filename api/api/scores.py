from sqlalchemy import desc
from sqlalchemy.orm import load_only

from .database import Score


def _field(u, type):
    """Determines which field to compare on based on type."""
    type = type.lower()
    if type == "id":
        return Score.user_id
    elif type == "string":
        return Score.username
    else:
        return Score.user_id if isinstance(u, type) else Score.username


def get_score_hashes(session, user):
    """Returns the replay hash of every score by user."""
    # TODO: Is this username or ID?
    scores = (
        session.query(Score)
        .filter(Score.user_id == user)
        .options(load_only("replay_md5"))
        .all()
    )
    return [s.replay_md5 for s in scores]


def put_scores(session, user, scores):
    pass


def get_scores(session, beatmap_id, u=None, m=0, mods=None, type=None, limit=50):
    """Returns scores for a given beatmap."""
    filters = [Score.beatmap_id == beatmap_id, Score.mode == m]
    if u is not None:
        filters.append(_field(u, type) == u)
    if mods is not None:
        filters.append(Score.mods == mods)

    scores = (
        session.query(Score)
        .filter(*filters)
        .distinct(Score.user_id)
        .order_by(desc(Score.score))
        .limit(limit)
        .all()
    )

    return [s.dict() for s in scores]


def get_user_best(session, user, m=0, limit=10, type=None):
    """Gets a single user's best scores (by pp)."""
    filters = [_field(user, type) == user]
    if mods is not None:
        filters.append(Score.mods == mods)

    scores = (
        session.query(Score)
        .filter(*filters)
        .order_by(desc(Score.pp))
        .limit(limit)
        .all()
    )

    return [s.dict() for s in scores]


def get_user_recent(session, user, m=0, limit=10, type=None):
    scores = (
        session.query(Score)
        .filter(_field(user, type) == user, Score.mode == m)
        .order_by(desc(Score.date))
    )

    return [s.dict() for s in scores]
