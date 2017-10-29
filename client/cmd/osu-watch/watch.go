package main

import (
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

	scoresPath, err := unnoticed.OsuPath("scores.db")
	if err != nil {
		unnoticed.Notifyf("Couldn't find scores.db at %s", scoresPath)
		unnoticed.LogFatal(err)
	}
	osuPath, err := unnoticed.OsuPath("osu!.db")
	if err != nil {
		unnoticed.Notifyf("Couldn't find osu!.db at %s", osuPath)
		unnoticed.LogFatal(err)
	}

	for {
		unnoticed.Notifyf("Monitoring %s", scoresPath)
		unnoticed.Watch(scoresPath)

		db, err := unnoticed.BuildDB(scoresPath, osuPath)
		if err != nil {
			unnoticed.Notify("Processing scores failed")
			unnoticed.LogMsg(err)
			continue
		}

		if resp, err := db.Upload(); err != nil {
			unnoticed.Notify("Uploading scores failed")
			unnoticed.LogMsg(err)
		} else if resp.StatusCode != 200 {
			unnoticed.Notify("Uploading scores failed")
			unnoticed.LogMsgf("status: %s", resp.Status)
		} else {
			unnoticed.Notify("Uploading scores succeeded")
		}
	}
}
