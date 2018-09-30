package main

import (
	"io"
	"os"

	"github.com/pkg/errors"
)

// ScoresDB is a parsed scores.db file containing score data.
type ScoresDB struct {
	Beatmaps []ScoresDBBeatmap
}

// NewScoresDB reads the given file and parses it into a ScoresDB.
func NewScoresDB(path string) (*ScoresDB, error) {
	r, err := os.Open(path)
	if err != nil {
		return nil, errors.WithStack(err)
	}
	defer r.Close()

	if _, err = readInt(r); err != nil { // Version.
		return nil, errors.WithStack(err)
	}
	n, err := readInt(r) // Number of beatmaps.
	if err != nil {
		return nil, errors.WithStack(err)
	}

	db := &ScoresDB{}
	for i := uint32(0); i < n; i++ {
		b, err := parseScoresDBBeatmap(r)
		if err != nil {
			return nil, err
		}
		db.Beatmaps = append(db.Beatmaps, b)
	}

	return db, nil
}

// ScoresDBBeatmap is a beatmap found in scores.db.
type ScoresDBBeatmap struct {
	MD5    string
	Scores []ScoresDBScore
}

// parseScoresDBBeatmap parses a single beatmap and its scores from the reader.
func parseScoresDBBeatmap(r io.ReadSeeker) (ScoresDBBeatmap, error) {
	b := &ScoresDBBeatmap{}
	var err error

	if b.MD5, err = readString(r); err != nil {
		return ScoresDBBeatmap{}, errors.WithStack(err)
	}
	n, err := readInt(r)
	if err != nil {
		return ScoresDBBeatmap{}, errors.WithStack(err)
	}

	for i := uint32(0); i < n; i++ {
		s, err := parseScoresDBScore(r)
		if err != nil {
			return ScoresDBBeatmap{}, err
		}
		b.Scores = append(b.Scores, s)
	}

	return *b, nil
}

// ScoresDBScore is a score found in a ScoresDBBeatmap.
// Fields to fill in server-side:
// - user_id
// - pp
// - beatmap_id
// - rank
type ScoresDBScore struct {
	GameMode   uint8  `json:"mode"`
	BeatmapMD5 string `json:"beatmap_md5"` // Needed for beatmap versioning.
	PlayerName string `json:"username"`
	ReplayMD5  string `json:"replay_md5"`
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
	Timestamp  uint64 `json:"date:"`
}

// parseScore parses a single score from the reader.
func parseScoresDBScore(r io.ReadSeeker) (ScoresDBScore, error) {
	s := ScoresDBScore{}
	var err error

	if s.GameMode, err = readByte(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}

	// Skipping: Version.
	if _, err = r.Seek(SizeInt, io.SeekCurrent); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}

	if s.BeatmapMD5, err = readString(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.PlayerName, err = readString(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.ReplayMD5, err = readString(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.Count300, err = readShort(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.Count100, err = readShort(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.Count50, err = readShort(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.CountGeki, err = readShort(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.CountKatu, err = readShort(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.CountMiss, err = readShort(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.Score, err = readInt(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.MaxCombo, err = readShort(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.Perfect, err = readBool(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}
	if s.Mods, err = readInt(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}

	// Skipping: "Empty" string (not always the case).
	if err := skipString(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}

	if s.Timestamp, err = readLong(r); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}

	// Skipping: -1 and score ID.
	if _, err = r.Seek(SizeInt+SizeLong, io.SeekCurrent); err != nil {
		return ScoresDBScore{}, errors.WithStack(err)
	}

	return s, nil
}
