from time import sleep

from .util import notify


def triggerlamdbda(scores):
    """Trigger a Lambda function to add new scores to the remote database."""
    notify("Uploading %d new scores..." % len(scores))
    sleep(1)  # Helps to make sure the notifications stay in order.
    notify("Done uploading new scores.")
