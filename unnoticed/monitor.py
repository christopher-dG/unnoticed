from os.path import dirname
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from .aws import triggerlamdbda
from .parsing import builddb
from .util import log, notify


class Handler(PatternMatchingEventHandler):
    def __init__(self, pat):
        self.ready = False
        super(Handler, self).__init__(patterns=[pat], ignore_directories=True)

    def on_modified(self, event):
        log.debug("File was modified")
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
                log.debug("Reacting to handler ready")
                sleep(3)  # We only want to run once per "batch" of writes.
                triggerlamdbda(builddb().scoremap())
                handler.ready = False
    except KeyboardInterrupt:
        notify("Exiting.")
        observer.stop()
    observer.join()
