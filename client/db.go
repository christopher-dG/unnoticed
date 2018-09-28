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
	db := &DB{Dir: osuRoot}
	var err error

	if db.Osu, err = NewOsuDB(filepath.Join(osuRoot, "osu!.db")); err != nil {
		return nil, err
	}

	if db.Scores, err = NewScoresDB(filepath.Join(osuRoot, "scores.db")); err != nil {
		return nil, err
	}

	return db, nil
}

// Wait blocks until the scores.db is updated.
func (db *DB) Wait() error {
	return Wait(db.Dir, "scores.db")
}
