package main

import "errors"

// ScoresDB is a parsed scores.db file containing score information.
type ScoresDB struct {
}

// NewScoresDB reads the given file and parses it into a ScoresDB.
func NewScoresDB(path string) (*ScoresDB, error) {
	return nil, errors.New("TODO")
}
