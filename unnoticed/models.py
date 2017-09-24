import json
import time

from .util import log


class Beatmap:
    """An osu! beatmap."""
    def __init__(self, d):
        self.artist = d["artist"]  # String: Song artist.
        self.title = d["title"]  # String: Song title.
        self.creator = d["creator"]  # String: Mapper name.
        self.diff = d["diff"]  # String: Diff name.
        self.md5 = d["md5"]  # String: File hash.
        self.status = d["status"]  # Int: 0-2 = unranked, 4-6 ranked, 7 loved.
        self.id = d["id"]  # Int: Beatmap ID.
        self.mode = d["mode"]  # Int: 0: Standard, 1: Taiko, 2: CTB, 3: Mania.

    def serialize(self):
        return {
            "artist": self.artist,
            "title": self.title,
            "creator": self.creator,
            "diff": self.diff,
            "md5": self.md5,
            "status": self.status,
            "id": self.id,
            "mode": self.mode,
        }


class Score:
    """An osu! score."""
    def __init__(self, d):
        """
        d is a dict with values corresponding to some of the fields here,
        under "Individual score format":
        https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
        """
        self.mode = d["mode"]  # Int: 0: Standard, 1: Taiko, 2: CTB, 3: Mania.
        self.date = d["date"]  # Int: "Version of this score", yyyymmdd.
        self.md5 = d["md5"]  # String: Hash of the beatmap file.
        self.player = d["player"]  # String: Player's username.
        self.replay = d["replay"]  # String: Hash of the replay file.
        self.n300 = d["n300"]  # Int: Number of 300s.
        self.n100 = d["n100"]  # Int: Number of 100s/150s/100s/200s.
        self.n50 = d["n50"]  # Int: Number of 50s/NA/small fruits/50s.
        self.ngeki = d["ngeki"]  # Int: Number of Gekis/NA/NA/Max 300s.
        self.nkatu = d["nkatu"]  # Int: Number of Katus/NA/NA/100s.
        self.nmisses = d["nmisses"]  # Int: Number of misses.
        self.score = d["score"]  # Int: Total score.
        self.combo = d["combo"]  # Int: Maximum combo.
        self.fc = d["fc"]  # Bool: Perfect combo.
        self.mods = d["mods"]  # Int: https://github.com/ppy/osu-api/wiki#mods
        self.timestamp = d["timestamp"]  # Int: Timestamp of the play(?).
        self.id = d["id"]  # Int: Online score id.

    def serialize(self):
        return {
            "mode": self.mode,
            "date": self.date,
            "md5": self.md5,
            "player": self.player,
            "replay": self.replay,
            "n300": self.n300,
            "n100": self.n100,
            "n50": self.n50,
            "ngeki": self.ngeki,
            "nkatu": self.nkatu,
            "nmisses": self.nmisses,
            "score": self.score,
            "combo": self.combo,
            "fc": self.fc,
            "mods": self.mods,
            "timestamp": self.timestamp,
            "id": self.id,
        }


class DB:
    """
    A collection of all of a user's beatmaps and their scores on them.
    Each beatmap is guaranteed to have at least one associated score, and
    each score's beatmap is guaranteed to exist.
    """
    def __init__(self, username, beatmaps, scores):
        """beatmaps is a list of Beatmaps, scores is a list of Scores."""
        self.username = username
        self.dt = time.time()
        # Get rid of ranked/loved maps.
        unranked = [b for b in beatmaps if b.status in [0, 1, 2]]
        diff = len(beatmaps) - len(unranked)
        log.debug("Filtered out %d non-unranked beatmaps" % diff)
        # Get rid of scores on filtered maps.
        md5map = {b.md5: b for b in unranked}
        self.scores = [s for s in scores if s.md5 in md5map]
        diff = len(scores) - len(self.scores)
        log.debug("Filtered out %d scores on non-unranked beatmaps" % diff)
        # Get rid of beatmaps without any scores.
        md5s = [s.md5 for s in self.scores]
        self.beatmaps = [b for b in unranked if b.md5 in md5s]
        diff = len(unranked) - len(self.beatmaps)
        log.debug("Filtered out %d beatmaps without scores" % diff)

    def scoremap(self):
        """Return a dict mapping beatmaps to their scores."""
        smap = {b: [] for b in self.beatmaps}
        md5map = {b.md5: b for b in self.beatmaps}
        for s in self.scores:
            smap[md5map[s.md5]].append(s)
        return smap

    def serialize(self):
        """Dump the DB to a JSON string."""
        return json.dumps({
            "username": self.username,
            "dt": self.dt,
            "beatmaps": [b.serialize() for b in self.beatmaps],
            "scores": [s.serialize() for s in self.scores],
        })
