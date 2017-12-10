package unnoticed

import (
	"path"

	"github.com/rjeczalik/notify"
)

// Watch waits until some new files are created in dir.
// Don't return for every new file to avoid spamming my API for every replay.
func Watch(dir string) error {
	count := 5
	events := make(chan notify.EventInfo, count)
	path := path.Join(dir, "...")
	if err := notify.Watch(path, events, notify.Create); err != nil {
		LogMsgf("error watching replay directory: %s", err)
		return err
	}
	defer notify.Stop(events)

	for i := 1; i <= count; i++ {
		event := <-events
		LogMsgf("new replay file %d/5: %s", i, event.Path())
	}
	return nil
}
