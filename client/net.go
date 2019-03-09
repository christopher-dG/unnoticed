package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

const (
	getUserIDEndpoint      = "/get_user_id/"
	getScoreHashesEndpoint = "/get_score_hashes/"
	putScoresEndpoint      = "/put_scores/"
)

var (
	apiURL       = os.Getenv("API_URL") // TODO: Get the real URL and move to const.
	httpClient   = http.Client{Timeout: time.Minute}
	ErrBadStatus = errors.New("non-200 response")
)

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

// getUserID gets a player's user ID from their username.
func getUserID(db *DB) (int, error) {
	log.Println("GET:", getUserIDEndpoint+db.Osu.PlayerName)
	r, err := httpClient.Get(apiURL + getUserIDEndpoint + db.Osu.PlayerName)
	if err != nil {
		return 0, err
	}

	b, err := checkReadResp(r)
	if err != nil {
		return 0, err
	}

	return strconv.Atoi(string(b))
}

// getScoreHashes gets a list of all scores that are already stored.
func getScoreHashes(db DB) ([]string, error) {
	log.Println("GET:", getScoreHashesEndpoint+db.Osu.PlayerName)
	r, err := httpClient.Get(apiURL + getScoreHashesEndpoint + db.Osu.PlayerName)
	if err != nil {
		return GetScoreHashesResp{}, err
	}

	b, err := checkReadResp(r)
	if err != nil {
		return GetScoreHashesResp{}, err
	}

	var sh GetScoreHashesResp
	err = json.Unmarshal(b, &sh)
	return sh, err
}

// PutScores uploads scores.
func PutScores(db DB) error {
	sh, err := getScoreHashes(db)
	if err != nil {
		return err
	}

	b, err := json.Marshal(db.Payload(sh.Scores))
	if err != nil {
		return err
	}

	log.Println("POST:", putScoresEndpoint+strconv.Itoa(sh.UserID))
	r, err := httpClient.Post(
		apiURL+putScoresEndpoint+db.Osu.PlayerName,
		"application/json",
		bytes.NewBuffer(b),
	)
	if err != nil {
		return err
	}

	b, err = checkReadResp(r)
	if len(b) > 0 {
		log.Println("put_scores response:", string(b))
	}
	return nil
}
