import logging
import sys
import threading

log = logging.getLogger()
title = "[Unnoticed]"

if sys.platform in ["win32", "cygwin"]:
    DBROOT = "C:\\\\Program Files (x86)\\osu!\\"
    import win10toast
    tn = win10toast.ToastNotifier()

    def shownotif(msg):
        threading.Thread(target=tn.show_toast, args=[title, msg]).start()

elif sys.platform == "darwin":
    DBROOT = "/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/"  # noqa
    import pync

    def shownotif(msg):
        # Square brackets don't work on MacOS.
        pync.Notifier.notify(msg, title=title[1:-1])

else:
    DBROOT = "./"  # TODO: Where will this go?
    import notify2
    notify2.init(title)

    def shownotif(msg):
        notify2.Notification(title, msg).show()


def notify(msg):
    """Show a desktop notification."""
    log.debug("Desktop notification: %s" % msg)
    try:
        shownotif(msg)
    except Exception as e:
        log.error("Notification error: %s" % e)
