package main

import (
	"path/filepath"
)

// DB contains data from both database files.
type DB struct {
	Dir    string
	Osu    *OsuDB
	Scores *ScoresDB
}

// NewDB creates a new DB by reading both database files.
func NewDB(osuRoot string) (*DB, error) {
	osu, err := NewOsuDB(filepath.Join(osuRoot, "osu!.db"))
	if err != nil {
		return nil, err
	}

	scores, err := NewScoresDB(filepath.Join(osuRoot, "scores.db"))
	if err != nil {
		return nil, err
	}

	return &DB{Dir: osuRoot, Osu: osu, Scores: scores}, nil
}

// Wait blocks until the scores.db is updated.
func (db *DB) Wait() error {
	return Wait(db.Dir, "scores.db")
}
