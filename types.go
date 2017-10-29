package unnoticed

import (
	"bytes"
	"encoding/json"
	"errors"
	"net/http"
)

// Beatmap is an osu! beatmap.
type Beatmap struct {
	MD5    string `json:"md5"` // Beatmap hash.
	Status uint8  `json:"-"`   // Ranked status (0-2 = ranked).
	ID     uint32 `json:"id"`  // Map ID.
}

// Score is a score on a particular beatmap.
type Score struct {
	Mode  uint8  `json:"mode"`  // Game mode (0=STD, 1=Taiko, 2=CTB, 3=Mania).
	MHash string `json:"mhash"` // Hash of the beatmap.
	Name  string `json:"name"`  // Player username.
	SHash string `json:"shash"` // Hash of the replay.
	N300  uint16 `json:"n300"`  // Number of 300s.
	N100  uint16 `json:"n100"`  // Number of 100s/150/100s/200s.
	N50   uint16 `json:"n50"`   // Number of 50s/NA/small fruits/50s.
	NGeki uint16 `json:"ngeki"` // Number of Gekis/NA/NA/Max 300s.
	NKatu uint16 `json:"nkatu"` // Number of Katus/NA/NA/100s.
	NMiss uint16 `json:"nmiss"` // Number of misses.
	Score uint32 `json:"score"` // Total score.
	Combo uint16 `json:"combo"` // Maximum combo.
	IsFC  bool   `json:"fc"`    // Perfect combo.
	Mods  uint32 `json:"mods"`  // Enabled mods: https://github.com/ppy/osu-api/wiki#mods.
	Date  int64  `json:"date"`  // Unix timestamp of the play.
	Map   uint32 `json:"map"`   // ID of the beatmap.
}

// DB is a collection of unranked beatmaps and scores.
type DB struct {
	json.Marshaler
	Username string     // Player username.
	Scores   []*Score   // List of scores.
	Beatmaps []*Beatmap // List of beatmaps.
}

func (db *DB) MarshalJSON() ([]byte, error) {
	self := make(map[string]interface{})
	self["username"] = db.Username
	mapMap := make(map[string]uint32)
	for _, beatmap := range db.Beatmaps {
		mapMap[beatmap.MD5] = beatmap.ID
	}

	scores := []*Score{}
	for _, score := range db.Scores {
		if val, ok := mapMap[score.MHash]; ok {
			score.Map = val
			scores = append(scores, score)
		} else {
			LogMsgf("no beatmap matched %s", score.MHash)
		}
	}
	self["scores"] = scores

	return json.Marshal(self)
}

// Upload posts the scores database to an API endpoint.
func (db *DB) Upload() (*http.Response, error) {
	out, err := json.Marshal(db)
	if err != nil {
		return nil, err
	}
	hc := http.Client{}
	req, err := http.NewRequest(
		http.MethodPut,
		"https://tcx6ldznwk.execute-api.us-east-1.amazonaws.com/unnoticed/upload",
		bytes.NewReader(out),
	)
	if err != nil {
		return nil, err
	}
	resp, err := hc.Do(req)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != 200 {
		return nil, errors.New("Upload returned error code " + resp.Status)
	}
	return resp, err
}

// NewDB creates a new score database.
func NewDB(username string, scores []*Score, beatmaps []*Beatmap) *DB {
	db := new(DB)
	db.Username = username
	// Ideally we'd like to filter out non-unranked beatmaps here,
	// but the ranked status values are not consistent so we'll post
	// them all and let the frontend deal with that.
	db.Beatmaps = beatmaps

	filteredScores := []*Score{}
	for _, score := range scores {
		// TODO: Sort + binary search. But this only takes a few seconds anyways.
		for _, beatmap := range beatmaps {
			if beatmap.MD5 == score.MHash {
				filteredScores = append(filteredScores, score)
				break
			}
		}
	}
	LogMsgf(
		"pruned %d scores without matching beatmaps",
		len(scores)-len(filteredScores),
	)

	db.Scores = filteredScores
	return db
}
