import sys
from os.path import dirname
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


##### Data models #####

class Score:
    """An osu! score."""
    def __init__(self, d):
        """
        d is a dict with values corresponding to some of the fields here,
        under "Individual score format":
        https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
        """
        self.mode    = d["mode"]     # 0 = Standard, 1 = Taiko, 2 = CRB, 3 = Mania.
        self.version = d["version"]  # "Version of this score/replay", yyyymmdd.
        self.name    = d["name"]     # Player's username.
        self.md5     = d["md5"]      # Hash of the replay file.
        self.n300    = d["n300"]     # Number of 300s.
        self.n100    = d["n100"]     # Number of 100s, 150s, 100s, or 200s.
        self.n50     = d["n50"]      # Number of 50s, NA, small fruits, 50s.
        self.ngeki   = d["ngeki"]    # Number of Gekis, NA, NA, Max 300s.
        self.nkatu   = d["nkatu"]    # Number of Katus, NA, NA, 100s.
        self.nmisses = d["nmisses"]  # Number of misses.
        self.score   = d["score"]    # Total score.
        self.combo   = d["combo"]    # Maximum combo.
        self.fc      = d["fc"]       # Perfect combo (bool).
        self.mods    = d["mods"]     # https://github.com/ppy/osu-api/wiki#mods
        self.time    = d["time"]     # Timestamp of the play.
        self.scoreid = d["scoreid"]  # Online score id.


##### DB parsing #####

def processdb(filename):
    """Return all new unranked scores."""
    scores = []
    f = open(filename, "rb")
    f.seek(4 + 4)  # Ignore the first two int fields.
    f.close()
    return scores

def readnum(f, n):
    """Read an n-byte integer from f."""
    return int.from_bytes(f.read(n), "little")

def readbool(f):
    """Read a boolean from f."""
    return bool(f.read(1))

def readstring(f):
    """Read a variable-length string from f."""
    if not readnum(f, 1):
        return ""
    return f.read(readuleb(f)).decode("utf-8")


def readuleb(f):
    """Read and decode a ULEB12 number from f."""
    # https://en.wikipedia.org/wiki/LEB128
    n = 0;
    shift = 0;
    while True:
        byte = readnum(f, 1)
        n |= (byte & 0x3f << shift)
        if not (byte & 0x80):
            break
        shift += 7
    return n


##### AWS functions #####

def triggerlamdbda(scores):
    """Trigger a Lambda function to add new scores to the remote database."""
    pass


##### Filesystem monitoring #####

class Handler(PatternMatchingEventHandler):
    def __init__(self, pat):
        self.ready = False
        super(Handler, self).__init__(patterns=[pat], ignore_directories=True)

    def on_modified(self, event):
        self.ready = True


def monitorloop(filename):
    """
    Continually wait until filename is written to,
    then trigger the rest of the script.
    """
    print("Monitoring: %s" % filename)
    handler = Handler(filename)
    observer = Observer()
    observer.schedule(handler, dirname(filename))
    observer.start()

    try:
        while True:
            sleep(1)
            if handler.ready:
                triggerlamdbda(processdb(filename))
                handler.ready = False
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


##### Utils #####

def dbroot():
    """Determine the directory containing the database file."""
    # https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
    if sys.platform in ["win32", "cygwin"]:
        return "C:\\\\Program Files (x86)\osu!\\"
    elif sys.platform == "darwin":
        return "/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/"
    else:
        # TODO: Where will it go on Linux?
        return "./"
