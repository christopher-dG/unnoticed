from api.database import Player


def put_new_player(session, user_id, username):
    """Inserts a new player."""
    if not session.query(Player).get(user_id):
        p = Player(user_id=user_id, username=username)
        sesson.add(p)
        return p
    return None
