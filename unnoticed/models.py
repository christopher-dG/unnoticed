from .util import log


class Beatmap:
    """An osu! beatmap."""
    def __init__(self, d):
        self.artist = d["artist"]  # String: Song artist.
        self.title = d["title"]  # String: Song title.
        self.creator = d["creator"]  # String: Mapper name.
        self.diff = d["diff"]  # String: Diff name.
        self.md5 = d["md5"]  # String: File hash.
        self.status = d["status"]  # Int: 4: ranked, 5: approved, 2: unranked.
        self.id = d["id"]  # Int: Beatmap ID.
        self.mode = d["mode"]  # Int: 0: Standard, 1: Taiko, 2: CTB, 3: Mania.


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


class DB:
    """A collection of all of a user's beatmaps and their scores on them."""
    def __init__(self, username, beatmaps, scores):
        """beatmaps is a list of Beatmaps, scores is a list of Scores."""
        self.username = username
        self.beatmaps = beatmaps
        self.scores = scores

    def md5map(self):
        """Return a dict mapping MD5 hashes to their beatmaps."""
        return {beatmap.md5: beatmap for beatmap in self.beatmaps}

    def scoremap(self):
        """Return a dict mapping beatmaps to their scores."""
        scoremap = {beatmap: [] for beatmap in self.beatmaps}
        table = self.md5map()
        for score in self.scores:
            try:
                scoremap[table[score["md5"]]].append(score)
            except KeyError:
                log().warn(
                    "A score had md5 %s but no beatmap matched" % score["md5"]
                )
        return scoremap
