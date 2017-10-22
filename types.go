package unnoticed

import (
	"bytes"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"time"
)

type Beatmap struct {
	MD5    string `json:"md5"`  // Beatmap hash.
	Status uint8  `json:"-"`    // Ranked status (0-2 = ranked).
	ID     uint32 `json:"id"`   // Map ID.
	Mode   uint8  `json:"mode"` // Game mode (0=STD, 1=Taiko, 2=CTB, 3=Mania).
}

type Score struct {
	Mode  uint8  `json:"mode"`  // Game mode (0=STD, 1=Taiko, 2=CTB, 3=Mania).
	Date  uint32 `json:"date"`  // Date of the play (yyyymmdd).
	MD5   string `json:"-"`     // Hash of the beatmap.
	N300  uint16 `json:"n300"`  // Number of 300s.
	N100  uint16 `json:"n100"`  // Number of 100s/150/100s/200s.
	N50   uint16 `json:"n50"`   // Number of 50s/NA/small fruits/50s.
	NGeki uint16 `json:"ngeki"` // Number of Gekis/NA/NA/Max 300s.
	NKatu uint16 `json:"nkatu"` // Number of Katus/NA/NA/100s.
	NMiss uint16 `json:"nmiss"` // Number of misses.
	Score uint32 `json:"score"` // Total score.
	Combo uint16 `json:"combo"` // Maximum combo.
	IsFC  bool   `json:"isfc"`  // Perfect combo.
	Mods  uint32 `json:"mods"`  // Enabled mods: https://github.com/ppy/osu-api/wiki#mods.
	ID    uint64 `json:"id"`    // Online score ID.
}

type DB struct {
	json.Marshaler
	Username string     `json:"username"` // Player username.
	DateTime string     `json:"datetime"` // Current date and time.
	Scores   []*Score   `json:"scores"`   // List of scores.
	Beatmaps []*Beatmap `json:"beatmaps"` // List of beatmaps.
}

func (db *DB) MarshalJSON() ([]byte, error) {
	self := make(map[string]interface{})
	self["username"] = db.Username
	self["datetime"] = db.DateTime

	mapMap := make(map[uint32]*Beatmap)
	for _, beatmap := range db.Beatmaps {
		mapMap[beatmap.ID] = beatmap
	}
	self["beatmaps"] = mapMap

	md5Map := make(map[string]*Beatmap)
	for _, beatmap := range db.Beatmaps {
		md5Map[beatmap.MD5] = beatmap
	}

	scoreMap := make(map[uint32][]*Score)
	for _, score := range db.Scores {
		id := md5Map[score.MD5].ID
		if val, ok := scoreMap[id]; ok {
			scoreMap[id] = append(val, score)
		} else {
			scoreMap[id] = []*Score{score}
		}
	}
	self["scores"] = scoreMap

	return json.Marshal(self)
}

// Upload posts the
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
	db.DateTime = time.Now().Format(time.RFC3339)
	db.Username = username

	// Get rid of non-unranked scores/maps.
	filteredMaps := []*Beatmap{}
	for _, beatmap := range beatmaps {
		if beatmap.Status < 3 {
			filteredMaps = append(filteredMaps, beatmap)
		}
	}
	log.Printf("pruned %d non-unranked beatmaps\n", len(beatmaps)-len(filteredMaps))

	md5Map := make(map[string]*Beatmap)
	for _, beatmap := range filteredMaps {
		md5Map[beatmap.MD5] = beatmap
	}
	filteredScores := []*Score{}
	for _, score := range scores {
		for md5, _ := range md5Map {
			if md5 == score.MD5 {
				filteredScores = append(filteredScores, score)
			}
		}
	}
	log.Printf("pruned %d non-unranked scores\n", len(scores)-len(filteredScores))

	db.Scores = filteredScores
	db.Beatmaps = filteredMaps
	return db
}
