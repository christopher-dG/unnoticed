package main

import (
	"errors"
)

// OsuDB is a parsed osu!.db file containing beatmap information.
type OsuDB struct {
	PlayerName string
	Beatmaps   []OsuDBBeatmap
}

// NewOsuDB reads the given file and parses it into an OsuDB.
func NewOsuDB(path string) (*OsuDB, error) {
	return nil, errors.New("TODO")
}

// OsuDBBeatmap is a beatmap found in osu!.db.
// Missing fields (relative to API):
// - approved_date
// - bpm (use the first timing point?)
// - difficultyrating (could use nomod ModdedStarRating)
// - hit_length (could use drain_time but it's not accurate)
// - genre_id
// - language_id
// - favourite_count
// - playcount
// - max_combo
type OsuDBBeatmap struct {
	Artist               string             `json:"artist"`
	Title                string             `json:"title"`
	Creator              string             `json:"creator"`
	Difficulty           string             `json:"version"`
	MD5                  string             `json:"file_md5"`
	RankedStatus         byte               `json:"approved"`
	LastModificationTime uint64             `json:"last_update"`
	ApproachRate         float32            `json:"diff_approach"`
	CircleSize           float32            `json:"diff_size"`
	HPDrain              float32            `json:"diff_drain"`
	OverallDifficulty    float32            `json:"diff_overall"`
	StarRatingsStandard  []ModdedStarRating `json:"-"` // Could be used for difficulty rating.
	StarRatingsTaiko     []ModdedStarRating `json:"-"`
	StarRatingsCatch     []ModdedStarRating `json:"-"`
	StarRatingsMania     []ModdedStarRating `json:"-"`
	DrainTime            uint32             `json:"-"` // Could be used for hit length.
	TotalTime            uint32             `json:"total_length"`
	TimingPoints         []TimingPoint      `json:"-"` // Could be used for BPM.
	BeatmapID            uint32             `json:"beatmap_id"`
	BeatmapsetID         uint32             `json:"beatmapset_id"`
	GameMode             byte               `json:"mode"`
	SongSource           string             `json:"source"`
	SongTags             string             `json:"tags"`
}

// ModdedStarRating is a pair of mods and star rating found in an OsuDBBeatmap.
type ModdedStarRating struct {
	Mods       uint32  `json:"mods"`
	StarRating float64 `json:"star_rating"`
}

// TimingPoint is a timing point found in an OsuDBBeatmap.
type TimingPoint struct {
	BPM       float64 `json:"bpm"`
	Offset    float64 `json:"offset"`
	Inherited bool    `json:"inherited"`
}
