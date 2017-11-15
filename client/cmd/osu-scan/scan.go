package main

import (
	"bufio"
	"fmt"
	"os"
	"path"

	"github.com/christopher-dG/unnoticed"
)

func main() {
	logFile := path.Join(os.TempDir(), "osu-scan.log")
	if f, err := unnoticed.LogSetup(logFile); err == nil {
		defer f.Close()
		unnoticed.LogMsgf("log file: %s", logFile)
	}

	reader := bufio.NewReader(os.Stdin)
	osuDir, err := unnoticed.OsuDir()
	if err != nil {
		fmt.Println("osu! database files were not found.")
		fmt.Println("Enter the full path to your osu! install folder:")
		line, _, err := reader.ReadLine()
		if err != nil { // This should really not happen.
			unnoticed.LogFatal("Error reading line")
		}
		osuDir = string(line)
		_, err1 := os.Stat(path.Join(osuDir, "osu!.db"))
		_, err2 := os.Stat(path.Join(osuDir, "scores.db"))
		if err1 != nil || err2 != nil {
			fmt.Println("osu! database files were not found, press enter to exit.")
			reader.ReadByte()
			os.Exit(1)
		}
	}

	osuPath := path.Join(osuDir, "osu!.db")
	scoresPath := path.Join(osuDir, "scores.db")
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

	fmt.Printf("\nDone: Your log file is at %s.\nPress enter to exit.", logFile)
	reader.ReadByte()
}
