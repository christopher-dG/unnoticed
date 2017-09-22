import sys

if sys.platform in ["win32", "cygwin"]:
    dbroot = "C:\\\\Program Files (x86)\\osu!\\"
    import win10toast
    notifier = win10toast.ToastNotifier()

    def shownotif(msg):
        notifier.show_toast("[Unnoticed]", msg)

elif sys.platform == "darwin":
    dbroot = "/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/"  # noqa
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
