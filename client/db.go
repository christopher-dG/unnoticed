package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"path/filepath"
	"strconv"
)

type SyncState struct {
	BeatmapHashes []string
	ScoreHashes   []string
}

func NewSyncState() *SyncState {
	return &SyncState{
		BeatmapHashes: []string{},
		ScoreHashes:   []string{},
	}
}

// DB contains data from both database files.
type DB struct {
	Dir       string
	Osu       *OsuDB
	Scores    *ScoresDB
	UserID    int
	SyncState *SyncState
}

// NewDB creates a new DB by reading both database files.
func NewDB(osuRoot string) (*DB, error) {
	db := &DB{Dir: osuRoot, SyncState: NewSyncState()}
	var err error

	if db.Osu, err = NewOsuDB(filepath.Join(osuRoot, "osu!.db")); err != nil {
		return nil, err
	}

	if db.Scores, err = NewScoresDB(filepath.Join(osuRoot, "scores.db")); err != nil {
		return nil, err
	}

	return db, nil
}

func (db *DB) ResetSyncState() {
	db.SyncState = NewSyncState()
}

// Wait blocks until the scores.db is updated.
func (db DB) Wait() error {
	return Wait(db.Dir, "scores.db")
}

// getUserID gets a player's user ID from their username.
func (db *DB) GetUserID() error {
	log.Println("GET:", getUserIDEndpoint+db.Osu.PlayerName)
	r, err := httpClient.Get(apiURL + getUserIDEndpoint + db.Osu.PlayerName)
	if err != nil {
		return err
	}

	b, err := checkReadResp(r)
	if err != nil {
		return err
	}

	userID, err := strconv.Atoi(string(b))
	if err != nil {
		return err
	}

	db.UserID = userID
	return nil
}

func (db *DB) GetScoreHashes() error {
	log.Println("POST:", getScoreHashesEndpoint+db.Osu.PlayerName)
	r, err := httpClient.Post(
		apiURL+getScoreHashesEndpoint+strconv.Itoa(db.UserID),
		"application/json",
		body,
	)
	if err != nil {
		return err
	}

	b, err := checkReadResp(r)
	if err != nil {
		return err
	}

	var h []string
	if err = json.Unmarshal(b, &h); err != nil {
		return err
	}

	db.SyncState.ScoreHashes = h
	return nil
}

func (db DB) PutScores() error {

}

// Payload returns the request body for uploading scores.
func (db DB) Payload(exclude []string) map[string]interface{} {
	var beatmaps []OsuDBBeatmap
	for _, b := range db.Osu.Beatmaps {
		if b.Unranked() {
			beatmaps = append(beatmaps, b)
		}
	}

	var scores []ScoresDBScore
	scoreMap := make(map[string]bool)
	for _, s := range exclude {
		scoreMap[s] = true
	}
	for _, b := range db.Scores.Beatmaps {
		for _, s := range b.Scores {
			if _, ok := scoreMap[s.ReplayMD5]; !ok {
				scores = append(scores, s)
			}
		}
	}

	return map[string]interface{}{
		"beatmaps": beatmaps,
		"scores":   scores,
		"version":  version,
	}
}

// checkReadResp checks a response's success and returns its body.
func checkReadResp(r *http.Response) ([]byte, error) {
	defer r.Body.Close()

	b, err := ioutil.ReadAll(r.Body)
	if err != nil {
		return nil, err
	}

	if r.StatusCode != http.StatusOK {
		log.Println("status code:", r.Status)
		if len(b) > 0 {
			log.Println("body:", string(b))
		}
		return nil, ErrBadStatus
	}

	return b, nil
}
