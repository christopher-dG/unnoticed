package unnoticed

import (
	"log"
	"path/filepath"

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
			log.Println(event)
			if event.Op&fsnotify.Write == fsnotify.Write {
				return
			}
		case err := <-watcher.Errors:
			log.Println(err)
		}
	}
}
