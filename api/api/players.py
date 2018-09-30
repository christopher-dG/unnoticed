from api.database import Player


def put_new_player(sess, user_id, username):
    """Inserts a new player. Also handles name changes."""
    p = sess.query(Player).get(user_id)
    if not p:
        # If the player doesn't exist, insert a new one.
        p = Player(user_id=user_id, username=username)
        sess.add(p)
    elif p.username != username:
        # If the player exists but the username doesn't match, change the name.
        p.username = username
    return p
