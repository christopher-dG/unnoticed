package unnoticed

import (
	"bytes"
	"encoding/json"
	"errors"
	"io/ioutil"
	"net/http"
	"os"
	"sort"
)

// Beatmap is an osu! beatmap.
type Beatmap struct {
	MD5 string `json:"md5"` // Beatmap hash.
	ID  uint32 `json:"id"`  // Map ID.
}

// Score is a score on a particular beatmap.
type Score struct {
	Mode   uint8  `json:"mode"`   // Game mode (0=STD, 1=Taiko, 2=CTB, 3=Mania).
	Ver    uint32 `json:"ver"`    // Version of the score/replay.
	MHash  string `json:"mhash"`  // Hash of the beatmap.
	Player string `json:"player"` // Player username.
	SHash  string `json:"shash"`  // Hash of the replay.
	N300   uint16 `json:"n300"`   // Number of 300s.
	N100   uint16 `json:"n100"`   // Number of 100s/150/100s/200s.
	N50    uint16 `json:"n50"`    // Number of 50s/NA/small fruits/50s.
	NGeki  uint16 `json:"ngeki"`  // Number of Gekis/NA/NA/Max 300s.
	NKatu  uint16 `json:"nkatu"`  // Number of Katus/NA/NA/100s.
	NMiss  uint16 `json:"nmiss"`  // Number of misses.
	Score  uint32 `json:"score"`  // Total score.
	Combo  uint16 `json:"combo"`  // Maximum combo.
	FC     bool   `json:"fc"`     // Perfect combo.
	Mods   uint32 `json:"mods"`   // https://github.com/ppy/osu-api/wiki#mods.
	Date   int64  `json:"date"`   // Unix timestamp of the play.
	Map    uint32 `json:"map"`    // ID of the beatmap.
}

// DB is a collection of unranked beatmaps and scores.
type DB struct {
	Username string     `json:"username"` // Player username.
	Scores   []*Score   `json:"scores"`   // List of scores.
	Beatmaps []*Beatmap `json:"beatmaps"` // List of beatmaps.
}

// ResponseBody is the JSON object returned by the score upload request.
type ResponseBody struct {
	Error   string `json:"error"`
	NScores int    `json:"nscores"`
}

func (db *DB) MarshalJSON() ([]byte, error) {
	self := make(map[string]interface{})
	self["username"] = db.Username
	mapMap := make(map[string]uint32)
	for _, beatmap := range db.Beatmaps {
		mapMap[beatmap.MD5] = beatmap.ID
	}

	// Only include scores with a matching beatmap.
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

// FilterNew removes all scores contained in fn.
func (db *DB) FilterNew(fn string) error {
	if _, err := os.Stat(fn); err != nil {
		// If the file isn't found, we don't consider it an error, we just don't filter.
		LogMsgf("file %s was not found", fn)
		return nil
	}

	b, err := ioutil.ReadFile(fn)
	if err != nil {
		return err
	}

	hashes := []string{} // Hashes of existing scores.
	if err := json.Unmarshal(b, &hashes); err != nil {
		return err
	}

	filtered := []*Score{}
	for _, score := range db.Scores {
		found := false
		for _, hash := range hashes {
			if hash == score.SHash {
				found = true
				break
			}
		}
		if !found {
			filtered = append(filtered, score)
		}
	}

	nScores := len(db.Scores)
	LogMsgf("dropped %d old scores out of %d", nScores-len(filtered), nScores)
	db.Scores = filtered

	return nil
}

// Upload posts the scores database to an API endpoint.
func (db *DB) Upload(cache string) (*http.Response, error) {
	if err := db.FilterNew(cache); err != nil {
		LogMsg("filtering old scores failed; uploading all scores")
	}

	out, err := json.Marshal(db)
	if err != nil {
		return nil, err
	}
	LogMsgf("Starting upload (%dKB)", len(out)/1000)

	hc := http.Client{}
	req, err := http.NewRequest(
		http.MethodPut,
		"https://p9bztcmks6.execute-api.us-east-1.amazonaws.com/unnoticed/proxy",
		bytes.NewReader(out),
	)
	if err != nil {
		return nil, err
	}

	resp, err := hc.Do(req)
	if err != nil {
		return nil, err
	}

	defer resp.Body.Close()
	bodyText, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		LogMsg("reading response body failed")
	} else {
		body := new(ResponseBody)
		err = json.Unmarshal(bodyText, body)
		if err != nil {
			LogMsgf("decoding response body failed: %s", string(bodyText))
		} else {
			LogMsgf("%d new scores were added", body.NScores)
			if len(body.Error) > 0 {
				LogMsgf("response error: %s", body.Error)
			}
		}
	}

	if resp.StatusCode != 200 {
		return nil, errors.New("Upload returned error code " + resp.Status)
	}
	return resp, nil
}

// NewDB creates a new score database.
func NewDB(username string, scores []*Score, beatmaps []*Beatmap) *DB {
	db := new(DB)
	db.Username = username
	db.Beatmaps = beatmaps

	// Get rid of any scores that don't have a matching beatmap,
	// since we have no way to identify which map they belong to.
	md5s := []string{}
	for _, beatmap := range beatmaps {
		md5s = append(md5s, beatmap.MD5)
	}
	sort.Strings(md5s)
	l := len(md5s)

	filteredScores := []*Score{}
	for _, score := range scores {
		if i := sort.SearchStrings(md5s, score.MHash); i < l && md5s[i] == score.MHash {
			filteredScores = append(filteredScores, score)
		}
	}

	LogMsgf(
		"pruned %d scores without matching beatmaps",
		len(scores)-len(filteredScores),
	)

	db.Scores = filteredScores
	return db
}
