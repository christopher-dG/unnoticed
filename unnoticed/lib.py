import sys
from os.path import dirname
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


##### Notifications #####

# TODO: Check if square brackets work on Windows and Linux.
if sys.platform in ["win32", "cygwin"]:
    dbroot = "C:\\\\Program Files (x86)\\osu!\\"
    import win10toast
    notifier = win10toast.ToastNotifier()
    def shownotif(msg):
        notifier.show_toast("[Unnoticed]", msg)
elif sys.platform == "darwin":
    dbroot = "/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/"
    import pync
    def shownotif(msg):
        # Square brackets don't work.
        pync.Notifier.notify(msg, title="Unnoticed")
else:
    dbroot = "./"  # TODO: Where will this go?
    import notify2
    notify2.init("[Unnoticed]")
    def shownotif(msg):
        notify2.Notification("[Unnoticed]", msg).show()

def notify(msg):
    """Show a desktop notification."""
    print(msg)
    try:
        shownotif(msg)
    except Exception as e:
        print("Notification error: %s" % e)


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
    notify("Processing new scores...")
    scores = []
    f = open(filename, "rb")
    f.seek(4 + 4)  # Ignore the first two int fields.
    f.close()
    sleep(1)  # Helps to make sure the notifications stay in order.
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
    """Read and decode a ULEB128 number from f."""
    # https://en.wikipedia.org/wiki/LEB128#Decode_unsigned_integer
    n, shift = 0, 0;
    while True:
        byte = readnum(f, 1)
        n |= byte & 0x3f << shift
        if not byte & 0x80:
            break
        shift += 7
    return n


##### AWS functions #####

def triggerlamdbda(scores):
    """Trigger a Lambda function to add new scores to the remote database."""
    notify("Uploading %d new scores..." % len(scores))
    sleep(1)  # Helps to make sure the notifications stay in order.
    notify("Done uploading new scores.")


##### Filesystem monitoring #####

class Handler(PatternMatchingEventHandler):
    def __init__(self, pat):
        self.ready = False
        super(Handler, self).__init__(patterns=[pat], ignore_directories=True)

    def on_modified(self, event):
        self.ready = True


def monitorloop(fn):
    """
    Continually wait until fn is written to,
    then trigger the lambda function.
    """
    notify("Monitoring: %s" % fn)
    handler = Handler(fn)
    observer = Observer()
    observer.schedule(handler, dirname(fn))
    observer.start()

    try:
        while True:
            sleep(1)
            if handler.ready:
                sleep(3)  # We only want to run once per "batch" of writes.
                triggerlamdbda(processdb(fn))
                handler.ready = False
    except KeyboardInterrupt:
        notify("Exiting.")
        observer.stop()
    observer.join()
