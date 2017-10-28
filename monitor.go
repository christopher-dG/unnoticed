package unnoticed

import (
	"log"
	"path/filepath"
	"time"

	"github.com/fsnotify/fsnotify"
)

// Watch waits until fn is modified.
func Watch(fn string) {
	fn, err := filepath.Abs(fn)
	if err != nil {
		log.Println(err)
	}
	log.Println(fn)
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatalf("couldn't get a watcher for %s", fn)
	}
	watcher.Add(fn)
	defer watcher.Close()
	for {
		select {
		case event := <-watcher.Events:
			// Wait a bit to make sure we don't process bursts of events.
			time.Sleep(5 * time.Second)
			log.Println(event)
			return
		case err := <-watcher.Errors:
			log.Println(err)
		}
	}
}
