package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"

	yaml "gopkg.in/yaml.v2"
)

func main() {
	var config Config
	if len(os.Args) < 2 {
		config = DefaultConfig()
	} else {
		b, err := ioutil.ReadFile(os.Args[1])
		if err != nil {
			log.Fatalf("couldn't read configuration file %s: %v\n", os.Args[1], err)
		}
		if err = yaml.Unmarshal(b, &config); err != nil {
			log.Fatalf("invalid config file %s: %v\n", os.Args[1], err)
		}
	}

	for {
		log.Println("loading database files")
		db, err := NewDB(config.OsuRoot)
		if err != nil {
			userFatal(err)
		}

		log.Println("uploading scores")
		if err := PutScores(*db); err != nil {
			userLog(err)
		}

		log.Println("waiting for database file updates")
		if err := db.Wait(); err != nil {
			userFatal(err)
		}
		log.Println("database files were updated")
	}
}

// userLog records an error and prompts the user to report it.
func userLog(err error) {
	log.Println("[Unnoticed] encounted an error")
	fmt.Println("please report the following on Discord: https://discord.gg/fwC36sS")
	fmt.Printf("%+v\n", err)
}

// userFatal records a fatal error and exits.
func userFatal(err error) {
	log.Println("===== UNRECOVERABLE ERROR =====")
	userLog(err)
	os.Exit(1)
}
