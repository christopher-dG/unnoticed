package unnoticed

import (
	"path"

	"github.com/rjeczalik/notify"
)

const (
	FileNotification = iota
	DirNotification
	ErrorNotification
)

// WatchFile waits until fn is modified, then writes to the fs channel.
func WatchFile(fs chan int, fn string) {
	events := make(chan notify.EventInfo, 1)
	if err := notify.Watch(fn, events, notify.All); err != nil {
		LogMsgf("error watching file %s: %s", fn, err)
		fs <- ErrorNotification
		return
	}
	defer notify.Stop(events)
	ei := <-events
	LogMsgf("%s was updated: %s", fn, ei.Event().String())
	fs <- FileNotification
}

// WatchDir waits until a new file is created in dir, then writes to the fs channel.
// Runs until the stop channel receives a message.
func WatchDir(fs chan int, stop chan bool, dir string) {
	events := make(chan notify.EventInfo, 1)
	path := path.Join(dir, "...")
	if err := notify.Watch(path, events, notify.Create); err != nil {
		LogMsgf("error watching directory %s: %s", dir, err)
		fs <- ErrorNotification
		return
	}
	defer notify.Stop(events)

	for {
		select {
		case ei := <-events:
			LogMsgf("new file: %s", ei.Path())
			fs <- DirNotification
		case <-stop:
			return
		}
	}
}
