package main

import (
	"errors"
	"io"
	"os"
)

const modern = 20140609

var ErrDBTooOld = errors.New("database version too old")

// OsuDB is a parsed osu!.db file containing beatmap information.
type OsuDB struct {
	Unlocked   bool
	PlayerName string
	Beatmaps   []OsuDBBeatmap
}

// NewOsuDB reads the given file and parses it into an OsuDB.
func NewOsuDB(path string) (*OsuDB, error) {
	r, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer r.Close()

	if v, err := readInt(r); err != nil {
		return nil, err
	} else if v < modern {
		return nil, ErrDBTooOld
	}

	// Skipping: Number of folders.
	if _, err := r.Seek(SizeInt, io.SeekCurrent); err != nil {
		return nil, err
	}

	db := &OsuDB{}
	if db.Unlocked, err = readBool(r); err != nil {
		return nil, err
	}

	// Skipping: Account unlock date.
	if _, err = r.Seek(SizeLong, io.SeekCurrent); err != nil {
		return nil, err
	}

	if db.PlayerName, err = readString(r); err != nil {
		return nil, err
	}

	n, err := readInt(r)
	if err != nil {
		return nil, err
	}
	for i := uint32(0); i < n; i++ {
		b, err := parseOsuDBBeatmap(r)
		if err != nil {
			return nil, err
		}
		db.Beatmaps = append(db.Beatmaps, b)
	}

	return db, nil
}

// OsuDBBeatmap is a beatmap found in osu!.db.
// We're skipping just about everything here, but we'll fill it in server side.
type OsuDBBeatmap struct {
	MD5          string
	BeatmapID    uint32
	BeatmapsetID uint32
}

// parseOsuDBBeatmap parses a single beatmap from the reader.
func parseOsuDBBeatmap(r io.ReadSeeker) (b OsuDBBeatmap, err error) {
	size, err := readInt(r)
	if err != nil {
		return
	}
	curr, err := r.Seek(0, io.SeekCurrent)
	if err != nil {
		return OsuDBBeatmap{}, err
	}
	defer r.Seek(curr+int64(size), io.SeekStart)

	// Skipping: Artist, artist Unicode, title, title Unicode, creator,
	// difficulty, and audio file name.
	for i := 0; i < 7; i++ {
		if err = skipString(r); err != nil {
			return OsuDBBeatmap{}, err
		}
	}

	if b.MD5, err = readString(r); err != nil {
		return OsuDBBeatmap{}, err
	}
	if err = skipString(r); err != nil { // .osu file name.
		return OsuDBBeatmap{}, err
	}

	// Skipping: Ranked status, hitcircles, sliders, spinners, last modification time,
	// approach rate, circle size, HP drain, overall difficulty, and slider velocity.
	if _, err = r.Seek(SizeByte+SizeShort+SizeShort+SizeShort+SizeLong+SizeSingle+SizeSingle+SizeSingle+SizeSingle+SizeDouble, io.SeekCurrent); err != nil {
		return OsuDBBeatmap{}, err
	}

	// Skipping: Standard/Taiko/Catch/Mania mod -> star ratings.
	for i := 0; i < 4; i++ {
		n, err := readInt(r)
		if err != nil {
			return OsuDBBeatmap{}, err
		}
		if _, err = r.Seek(int64(n)*(SizeByte+SizeInt+SizeByte+SizeDouble), io.SeekCurrent); err != nil {
			return OsuDBBeatmap{}, err
		}
	}

	// Skipping: Drain time, total time, and audio preview offset.
	if _, err = r.Seek(SizeInt+SizeInt+SizeInt, io.SeekCurrent); err != nil {
		return OsuDBBeatmap{}, err
	}

	// Skipping: Timing points.
	n, err := readInt(r)
	if err != nil {
		return OsuDBBeatmap{}, err
	}
	if _, err = r.Seek(int64(n)*(SizeLong+SizeLong+SizeBool), io.SeekCurrent); err != nil {
		return OsuDBBeatmap{}, err
	}

	if b.BeatmapID, err = readInt(r); err != nil {
		return OsuDBBeatmap{}, err
	}
	if b.BeatmapsetID, err = readInt(r); err != nil {
		return OsuDBBeatmap{}, err
	}

	// There are more values, but they'll be skipped by the deferred seek.

	return b, nil
}
