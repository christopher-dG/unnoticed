package main

import (
	"bufio"
	"fmt"
	"os"
	"os/signal"
	"path"

	"github.com/ProtonMail/go-appdir"
	"github.com/christopher-dG/unnoticed"
)

func main() {
	dirs := appdir.New("unnoticed")
	logDir := dirs.UserLogs()
	cacheDir := dirs.UserCache()
	unnoticed.LogMsgf("log directory: %s", logDir)
	unnoticed.LogMsgf("cache directory: %s", cacheDir)
	logFile := path.Join(logDir, "unnoticed.log")
	scoreCache := path.Join(cacheDir, "scores.json")

	if err := os.MkdirAll(cacheDir, 0755); err != nil {
		unnoticed.LogMsgf("couldn't create cache directory %s: %s", cacheDir, err)
	}
	if _, err := unnoticed.LogSetup(logFile); err != nil {
		unnoticed.LogMsgf("log file could not be opened: %s", err)
	}

	osuDir, err := unnoticed.OsuDir()
	if err != nil {
		unnoticed.LogMsg(err)
		fmt.Printf("\n> Enter the full path to your osu! install folder:\n> ")
		line, _, err := bufio.NewReader(os.Stdin).ReadLine()
		fmt.Println()
		if err != nil { // This should really not happen.
			unnoticed.LogMsg("error reading line")
			done(logFile, 1)
		}

		osuDir = string(line)
		_, err1 := os.Stat(path.Join(osuDir, "osu!.db"))
		_, err2 := os.Stat(path.Join(osuDir, "scores.db"))
		if err1 != nil || err2 != nil {
			unnoticed.LogMsgf("osu! database files were not found at %s", osuDir)
			done(logFile, 1)
		}
	}

	osuPath := path.Join(osuDir, "osu!.db")
	scoresPath := path.Join(osuDir, "scores.db")
	replaysPath := path.Join(osuDir, "Data", "r")

	// Exit by keyboard interrupt.
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() {
		<-c
		done(logFile, 0)
	}()

	limit := 10
	fs := make(chan int, limit) // Filesystem notifications.

	for {
		db, err := unnoticed.BuildDB(scoresPath, osuPath)
		if err != nil {
			unnoticed.LogMsgf("processing scores failed: %s", err)
			continue
		}

		scores := db.Scores[:] // Store this before db gets mutated.
		if _, err := db.Upload(scoreCache); err != nil {
			unnoticed.LogMsgf("uploading scores failed: %s", err)
			unnoticed.LogMsg("clearing score cache")
			os.RemoveAll(scoreCache)
		} else {
			unnoticed.LogMsg("uploading scores succeeded")
			if err = unnoticed.DumpScores(scoreCache, scores); err != nil {
				unnoticed.LogMsgf("dumping scores failed: %s", err)
			}
		}
		fmt.Println()

		// Wait for new replays or scores.db update, then upload again.
		// For new replays, only upload after a few have been made to avoid spamming.
		nReplays := 0
		stop := make(chan bool, 1)
		unnoticed.LogMsg("monitoring... press ctrl-c at any time to exit")
		go unnoticed.WatchFile(fs, scoresPath)
		go unnoticed.WatchDir(fs, stop, replaysPath)

		for nReplays < limit {
			switch <-fs {
			case unnoticed.ErrorNotification:
				unnoticed.LogMsg("monitoring failed, uploading just in case")
				fallthrough
			case unnoticed.FileNotification: // scores.db updated.
				nReplays = limit // I guess break doesn't work here.
			case unnoticed.DirNotification: // New replay.
				nReplays++
			}
		}
		stop <- true
	}
}

func done(logFile string, status int) {
	fmt.Printf("\n> Done: Your log file is at %s.\n> Press enter to exit.", logFile)
	bufio.NewReader(os.Stdin).ReadByte()
	os.Exit(status)
}
