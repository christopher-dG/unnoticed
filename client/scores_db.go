package main

import (
	"errors"
)

// ScoresDB is a parsed scores.db file containing score information.
type ScoresDB struct {
	Beatmaps []ScoresDBBeatmap
}

// NewScoresDB reads the given file and parses it into a ScoresDB.
func NewScoresDB(path string) (*ScoresDB, error) {
	return nil, errors.New("TODO")
}

// ScoresDBBeatmap is a beatmap found in scores.db.
type ScoresDBBeatmap struct {
	MD5    string
	Scores []Score
}

// Missing fields (relative to API):
// - user_id
// - pp
// - replay_available
// - beatmap_id (could get from DB)
// - rank
type Score struct {
	GameMode   uint8  `json:"-"`
	Version    uint32 `json:"-"`
	BeatmapMD5 string `json:"beatmap_md5"` // Needed for beatmap versioning.
	PlayerName string `json:"username"`
	ReplayMD5  string `json:"-"`
	Count300   uint16 `json:"count300"`
	Count100   uint16 `json:"count100"`
	Count50    uint16 `json:"count50"`
	CountGeki  uint16 `json:"countgeki"`
	CountKatu  uint16 `json:"countkatu"`
	CountMiss  uint16 `json:"countmiss"`
	Score      uint32 `json:"score"`
	MaxCombo   uint16 `json:"maxcombo"`
	Perfect    bool   `json:"perfect"`
	Mods       uint32 `json:"enabled_mods"`
	Timestamp  uint64 `json:"date"`
	ScoreID    uint64 `json:"score_id"`
}
