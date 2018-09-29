from .database import DBSession, Score


def get_score_hashes(user):
    pass


def put_scores(user, scores):
    pass


def get_scores(beatmap_id, u=None, m=0, mods=None, type=None, limit=50):
    pass


def get_user_best(user, m=0, limit=10, type=None):
    pass


def get_user_recent(user, m=0, limit=10, type=None):
    pass
