package main

import (
	"io"
	"os"
)

// ScoresDB is a parsed scores.db file containing score data.
type ScoresDB struct {
	Beatmaps []ScoresDBBeatmap
}

// NewScoresDB reads the given file and parses it into a ScoresDB.
func NewScoresDB(path string) (*ScoresDB, error) {
	r, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer r.Close()

	if _, err = readInt(r); err != nil { // Version.
		return nil, err
	}
	n, err := readInt(r) // Number of beatmaps.
	if err != nil {
		return nil, err
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
	Scores []Score
}

// parseScoresDBBeatmap parses a single beatmap and its scores from the reader.
func parseScoresDBBeatmap(r io.ReadSeeker) (ScoresDBBeatmap, error) {
	b := &ScoresDBBeatmap{}
	var err error

	if b.MD5, err = readString(r); err != nil {
		return ScoresDBBeatmap{}, err
	}
	n, err := readInt(r)
	if err != nil {
		return ScoresDBBeatmap{}, err
	}

	for i := uint32(0); i < n; i++ {
		s, err := parseScore(r)
		if err != nil {
			return ScoresDBBeatmap{}, err
		}
		b.Scores = append(b.Scores, s)
	}

	return *b, nil
}

// Score is a score found in a ScoresDBBeatmap.
// Fields to fill in server-side:
// - user_id
// - pp
// - beatmap_id
// - rank
type Score struct {
	GameMode   uint8
	BeatmapMD5 string // Needed for beatmap versioning.
	PlayerName string
	ReplayMD5  string
	Count300   uint16
	Count100   uint16
	Count50    uint16
	CountGeki  uint16
	CountKatu  uint16
	CountMiss  uint16
	Score      uint32
	MaxCombo   uint16
	Perfect    bool
	Mods       uint32
	Timestamp  uint64
	ScoreID    uint64
}

// parseScore parses a single score from the reader.
func parseScore(r io.ReadSeeker) (Score, error) {
	s := Score{}
	var err error

	if s.GameMode, err = readByte(r); err != nil {
		return Score{}, err
	}

	// Skipping: Version.
	if _, err = r.Seek(SizeInt, io.SeekCurrent); err != nil {
		return Score{}, err
	}

	if s.BeatmapMD5, err = readString(r); err != nil {
		return Score{}, err
	}
	if s.PlayerName, err = readString(r); err != nil {
		return Score{}, err
	}
	if s.ReplayMD5, err = readString(r); err != nil {
		return Score{}, err
	}
	if s.Count300, err = readShort(r); err != nil {
		return Score{}, err
	}
	if s.Count100, err = readShort(r); err != nil {
		return Score{}, err
	}
	if s.Count50, err = readShort(r); err != nil {
		return Score{}, err
	}
	if s.CountGeki, err = readShort(r); err != nil {
		return Score{}, err
	}
	if s.CountKatu, err = readShort(r); err != nil {
		return Score{}, err
	}
	if s.CountMiss, err = readShort(r); err != nil {
		return Score{}, err
	}
	if s.Score, err = readInt(r); err != nil {
		return Score{}, err
	}
	if s.MaxCombo, err = readShort(r); err != nil {
		return Score{}, err
	}
	if s.Perfect, err = readBool(r); err != nil {
		return Score{}, err
	}
	if s.Mods, err = readInt(r); err != nil {
		return Score{}, err
	}

	// Skipping: "Empty" string (not always the case).
	if err := skipString(r); err != nil {
		return Score{}, err
	}

	if s.Timestamp, err = readLong(r); err != nil {
		return Score{}, err
	}

	// Skipping: -1.
	if _, err = r.Seek(SizeInt, io.SeekCurrent); err != nil {
		return Score{}, err
	}

	if s.ScoreID, err = readLong(r); err != nil {
		return Score{}, err
	}

	return s, nil
}
