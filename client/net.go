package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"
)

const (
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
		log.Println("status code:", r.StatusCode, r.Status)
		if len(b) > 0 {
			log.Println("body:", string(b))
		}
		return nil, ErrBadStatus
	}

	return b, nil
}

// getScoreHashes gets a list of all scores that are already stored.
func getScoreHashes(db DB) ([]string, error) {
	log.Println("GET:", getScoreHashesEndpoint+db.Osu.PlayerName)
	r, err := httpClient.Get(apiURL + getScoreHashesEndpoint + db.Osu.PlayerName)
	if err != nil {
		return nil, err
	}

	b, err := checkReadResp(r)
	if err != nil {
		return nil, err
	}

	var hashes []string
	err = json.Unmarshal(b, &hashes)
	return hashes, err
}

// PutScores uploads scores.
func PutScores(db DB) error {
	exclude, err := getScoreHashes(db)
	if err != nil {
		return err
	}

	b, err := json.Marshal(db.Payload(exclude))
	if err != nil {
		return err
	}

	log.Println("POST:", putScoresEndpoint+db.Osu.PlayerName)
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
