package main

import (
	"bufio"
	"fmt"
	"os"
	"path"

	"github.com/christopher-dG/unnoticed"
)

func main() {
	logFile := path.Join(os.TempDir(), "osu-watch.log")
	if f, err := unnoticed.LogSetup(logFile); err == nil {
		defer f.Close()
		unnoticed.LogMsgf("log file: %s", logFile)
	}

	osuDir, err := unnoticed.OsuDir()
	if err != nil {
		unnoticed.LogMsg(err)
		fmt.Printf("\n> Enter the full path to your osu! install folder:\n> ")
		line, _, err := bufio.NewReader(os.Stdin).ReadLine()
		fmt.Println()
		if err != nil { // This should really not happen.
			unnoticed.LogMsg("Error reading line")
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

	for {
		unnoticed.Notifyf("Monitoring %s", scoresPath)
		unnoticed.Watch(scoresPath)

		db, err := unnoticed.BuildDB(scoresPath, osuPath)
		if err != nil {
			unnoticed.Notify("Processing scores failed")
			unnoticed.LogMsg(err)
			continue
		}

		if _, err := db.Upload(); err != nil {
			unnoticed.Notify("Uploading scores failed")
			unnoticed.LogMsg(err)
		} else {
			unnoticed.Notify("Uploading scores succeeded")
		}
	}
}

func done(logFile string, status int) {
	fmt.Printf("\n> Done: Your log file is at %s.\n> Press enter to exit.", logFile)
	bufio.NewReader(os.Stdin).ReadByte()
	os.Exit(status)
}
