package main

import (
	"log"
	"os"
	"path"

	"github.com/christopher-dG/unnoticed"
)

var logFile string = path.Join(os.TempDir(), "unnoticed-scan.log")

func main() {
	if f, err := os.OpenFile(
		logFile,
		os.O_RDWR|os.O_CREATE|os.O_APPEND,
		0666,
	); err == nil {
		defer f.Close()
		log.SetOutput(f)
	}

	// TODO: Make these paths configurable with environment variables.
	scoresPath, err := unnoticed.OsuPath("scores.db")
	if err != nil {
		unnoticed.Notifyf("Couldn't find scores.db at %s", scoresPath)
		log.Fatal(err)
	}
	osuPath, err := unnoticed.OsuPath("osu!.db")
	if err != nil {
		unnoticed.Notifyf("Couldn't find osu!.db at %s", osuPath)
		log.Fatal(err)
	}

	db, err := unnoticed.BuildDB(scoresPath, osuPath)
	if err != nil {
		unnoticed.Notify("Processing scores failed")
		log.Fatal(err)
	}

	resp, err := db.Upload()
	if err != nil {
		unnoticed.Notify("Uploading scores failed")
		log.Fatal(err)
	}
	unnoticed.Notify("Uploading scores succeeded")
	log.Println(resp)
}
