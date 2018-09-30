from api.database import Player


def put_new_player(sess, user_id, username):
    """Inserts a new player. Also handles name changes."""
    p = sess.query(Player).get(user_id)
    if p and p.username != username:
        p.username = username
    else:
        p = Player(user_id=user_id, username=username)
        sess.add(p)
    return p
