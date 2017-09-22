class Score:
    """An osu! score."""
    def __init__(self, d):
        """
        d is a dict with values corresponding to some of the fields here,
        under "Individual score format":
        https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
        """
        self.mode = d["mode"]  # 0 = Standard, 1 = Taiko, 2 = CRB, 3 = Mania.
        self.version = d["version"]  # "Version of this score", yyyymmdd.
        self.name = d["name"]  # Player's username.
        self.md5 = d["md5"]  # Hash of the replay file.
        self.n300 = d["n300"]  # Number of 300s.
        self.n100 = d["n100"]  # Number of 100s, 150s, 100s, or 200s.
        self.n50 = d["n50"]  # Number of 50s, NA, small fruits, 50s.
        self.ngeki = d["ngeki"]  # Number of Gekis, NA, NA, Max 300s.
        self.nkatu = d["nkatu"]  # Number of Katus, NA, NA, 100s.
        self.nmisses = d["nmisses"]  # Number of misses.
        self.score = d["score"]  # Total score.
        self.combo = d["combo"]  # Maximum combo.
        self.fc = d["fc"]  # Perfect combo (bool).
        self.mods = d["mods"]  # https://github.com/ppy/osu-api/wiki#mods
        self.time = d["time"]  # Timestamp of the play.
        self.scoreid = d["scoreid"]  # Online score id.
