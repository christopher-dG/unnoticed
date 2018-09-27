package main

import "errors"

// getOnlineScores gets a list of all scores that are already stored.
func getOnlineScores(db *DB) ([]string, error) {
	return nil, errors.New("TODO")
}

// PutScores uploads scores.
func PutScores(db *DB) error {
	_, err := getOnlineScores(db)
	if err != nil {
		return err
	}
	return errors.New("TODO")
}
