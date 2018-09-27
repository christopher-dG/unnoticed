package main

import (
	"errors"

	"github.com/fsnotify/fsnotify"
)

var ErrWatcher = errors.New("error watching for file updates")

// Wait waits for updates to a given file in dir.
func Wait(dir, file string) error {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		return err
	}
	defer watcher.Close()
	ch := make(chan error)

	go func() {
		for {
			select {
			case evt, ok := <-watcher.Events:
				if !ok {
					ch <- ErrWatcher
					return
				}
				if evt.Name == file {
					ch <- nil
					return
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					ch <- ErrWatcher
				}
				userLog(err)
			}
		}
	}()

	if err = watcher.Add(dir); err != nil {
		return err
	}

	return <-ch
}
