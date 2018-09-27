package main

import "errors"

// OsuDB is a parsed osu!.db file containing beatmap information.
type OsuDB struct {
}

// NewOsuDB reads the given file and parses it into an OsuDB.
func NewOsuDB(path string) (*OsuDB, error) {
	return nil, errors.New("TODO")
}
