package main

import (
	"os"
	"path"

	"github.com/christopher-dG/unnoticed"
)

func main() {
	LogFile := path.Join(os.TempDir(), "unnoticed-scan.log")
	if f, err := unnoticed.LogSetup(LogFile); err == nil {
		defer f.Close()
		unnoticed.LogMsgf("log file: %s", LogFile)
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

	db, err := unnoticed.BuildDB(scoresPath, osuPath)
	if err != nil {
		unnoticed.Notify("Processing scores failed")
		unnoticed.LogFatal(err)
	}

	if resp, err := db.Upload(); err != nil {
		unnoticed.Notify("Uploading scores failed")
		unnoticed.LogFatal(err)
	} else if resp.StatusCode != 200 {
		unnoticed.Notify("Uploading scores failed")
		unnoticed.LogMsgf("status: %s", resp.Status)
	} else {
		unnoticed.Notify("Uploading scores succeeded")
	}
}
