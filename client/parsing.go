package unnoticed

import (
	"encoding/binary"
	"errors"
	"os"
	"runtime"
	"time"
)

const (
	BYTE   = 1
	SHORT  = 2
	INT    = 4
	LONG   = 8
	SINGLE = 4
	DOUBLE = 8
)

// readByte reads a single byte from f.
func readByte(f *os.File) (uint8, error) {
	buf := make([]byte, BYTE)
	_, err := f.Read(buf)
	return buf[0], err
}

// readShort reads a 2-byte unsigned integer from f.
func readShort(f *os.File) (uint16, error) {
	buf := make([]byte, SHORT)
	if _, err := f.Read(buf); err != nil {
		return 0, err
	}
	return binary.LittleEndian.Uint16(buf), nil
}

// readInt reads a 4-byte unsigned integer from f.
func readInt(f *os.File) (uint32, error) {
	buf := make([]byte, INT)
	if _, err := f.Read(buf); err != nil {
		return 0, err
	}
	return binary.LittleEndian.Uint32(buf), nil
}

// readLong reads an 8-byte unsigned integer from f.
func readLong(f *os.File) (uint64, error) {
	buf := make([]byte, LONG)
	if _, err := f.Read(buf); err != nil {
		return 0, err
	}
	return binary.LittleEndian.Uint64(buf), nil
}

// readBool reads a boolean from f.
func readBool(f *os.File) (bool, error) {
	n, err := readByte(f)
	return n != 0, err
}

// readULEB reads and decodes a ULEB128 number from f.
// https://en.wikipedia.org/wiki/LEB128#Decode_unsigned_integer
func readULEB(f *os.File) (uint, error) {
	n, shift := uint(0), uint(0)
	for {
		b8, err := readByte(f)
		if err != nil {
			return 0, err
		}
		b := uint(b8) // Convert to 8-bit.
		n |= ((b & 0x7f) << shift)
		if (b & 0x80) == 0 {
			break
		}
		shift += 7
	}
	return n, nil
}

// readString reads a variable-length string from f.
func readString(f *os.File) (string, error) {
	if b, err := readByte(f); err != nil {
		return "", err
	} else if b == 0 {
		return "", err
	}
	n, err := readULEB(f)
	if err != nil {
		return "", err
	}
	buf := make([]byte, n)
	if _, err := f.Read(buf); err != nil {
		return "", err
	}
	return string(buf), nil
}

// readScore reads a Score from f.
func readScore(f *os.File) (score *Score, err error) {
	score = new(Score)
	// There's no size field so we'll avoid early returns, although it's
	// unlikely that this will actually get us back on track.
	flag := false
	score.Mode, err = readByte(f)
	flag = flag || err != nil
	score.Ver, err = readInt(f)
	flag = flag || err != nil
	score.MHash, err = readString(f)
	flag = flag || err != nil
	score.Player, err = readString(f)
	flag = flag || err != nil
	score.SHash, err = readString(f)
	flag = flag || err != nil
	score.N300, err = readShort(f)
	flag = flag || err != nil
	score.N100, err = readShort(f)
	flag = flag || err != nil
	score.N50, err = readShort(f)
	flag = flag || err != nil
	score.NGeki, err = readShort(f)
	flag = flag || err != nil
	score.NKatu, err = readShort(f)
	flag = flag || err != nil
	score.NMiss, err = readShort(f)
	flag = flag || err != nil
	score.Score, err = readInt(f)
	flag = flag || err != nil
	score.Combo, err = readShort(f)
	flag = flag || err != nil
	score.FC, err = readBool(f)
	flag = flag || err != nil
	score.Mods, err = readInt(f)
	flag = flag || err != nil
	_, err = readString(f) // This is supposedly always an empty string.
	flag = flag || err != nil
	ts, err := readLong(f)
	flag = flag || err != nil
	// https://github.com/worldwidewat/TicksToDateTime/
	// Windows ticks don't overflow a signed int for a veeeeeery long time.
	score.Date = (int64(ts) - 621355968000000000) / 10000000
	_, err = f.Seek(1*INT, 1) // This is supposedly always -1.
	flag = flag || err != nil
	_, err = readLong(f) // This is score ID, which is always 0 for unranked maps.
	flag = flag || err != nil

	if flag {
		return nil, errors.New("score parsing error")
	}
	return score, nil
}

// readScores reads all scores for one map.
func readScores(f *os.File, nMap uint32) ([]*Score, error) {
	scores := []*Score{}
	md5, err := readString(f)
	if err != nil {
		return scores, err
	}
	nScores, err := readInt(f)
	if err != nil {
		return scores, err
	}

	for i := uint32(1); i <= nScores; i++ {
		if score, err := readScore(f); err != nil {
			LogMsgf("scores.db score %d on map %d: %s", i, nMap, err)
		} else {
			scores = append(scores, score)
		}
	}

	for _, score := range scores {
		if score.MHash != md5 {
			LogMsgf("mismatched beatmap MD5: expected %s, got %s", md5, score.MHash)
		}
	}

	return scores, err
}

// readMap reads a Beatmap from f.
func readMap(f *os.File, v uint32) (*Beatmap, error) {
	beatmap := new(Beatmap)
	start, err := f.Seek(0, 1) // Don't seek, just get the current place.
	if err != nil {
		return beatmap, err // If we return here, we're pretty much screwed.
	}

	// The MacOS osu!.db file doesn't have beatmap size fields, so rather than seeking,
	// to start + size, we'll read the remaining fields and hope that we end up at the next
	// map's start. However, if it turns out that this is not the norm, we'll give users a
	// way to force the default parsing method via an environment variable (if this problem
	// is indeed rare enough, we should instead always use the default method except in the
	// presence of such an environment variable).
	// See issue #9: https://github.com/christopher-dG/unnoticed/issues/9
	var deferred func()
	// There's no use error checking here, we can't do anything about it.
	if runtime.GOOS == "darwin" && len(os.Getenv("UNNOTICED_FORCE_DEFAULT_PARSING")) == 0 {
		deferred = func() {
			f.Seek(2*INT+4*BYTE+1*SHORT+1*SINGLE+1*BYTE, 1)
			readString(f)
			readString(f)
			f.Seek(1*SHORT, 1)
			readString(f)
			f.Seek(1*BYTE+1*LONG+1*BYTE, 1)
			readString(f)
			f.Seek(1*LONG+5*BYTE, 1)
			if v < 20140609 {
				f.Seek(1*SHORT, 1) // This is apparently of questionable type.
			}
			f.Seek(1*INT+1*BYTE, 1) // This int as well.
		}
	} else {
		size, _ := readInt(f)
		deferred = func() { f.Seek(start+int64(size)+4, 0) }
	}

	defer deferred()

	// In the MacOS case where we don't know the size, error checking is unlikely to help.
	if _, err = readString(f); err != nil {
		return beatmap, err
	}
	if _, err = readString(f); err != nil {
		return beatmap, err
	}
	if _, err = readString(f); err != nil {
		return beatmap, err
	}
	if _, err = readString(f); err != nil {
		return beatmap, err
	}
	if _, err = readString(f); err != nil {
		return beatmap, err
	}
	if _, err = readString(f); err != nil {
		return beatmap, err
	}
	if _, err = readString(f); err != nil {
		return beatmap, err
	}
	if beatmap.MD5, err = readString(f); err != nil {
		return beatmap, err
	}
	if _, err = readString(f); err != nil {
		return beatmap, err
	}
	if _, err = readByte(f); err != nil {
		return beatmap, err
	}
	if _, err = f.Seek(3*SHORT+1*LONG, 1); err != nil {
		return beatmap, err
	}
	n := SINGLE
	if v < 20140609 {
		n = BYTE
	}
	if _, err = f.Seek(int64(4*n+1*DOUBLE), 1); err != nil {
		return beatmap, err
	}
	if v >= 20140609 {
		for i := 0; i < 4; i++ {
			nPairs, err := readInt(f)
			if err != nil {
				return beatmap, err
			}
			if _, err = f.Seek(int64(nPairs*14), 1); err != nil {
				return beatmap, err
			}
		}
	}
	if _, err = f.Seek(3*INT, 1); err != nil {
		return beatmap, err
	}
	nTimingPoints, err := readInt(f)
	if err != nil {
		return beatmap, err
	}
	if _, err = f.Seek(int64(nTimingPoints*17), 1); err != nil {
		return beatmap, err
	}
	if beatmap.ID, err = readInt(f); err != nil {
		return beatmap, err
	}
	if beatmap.ID == 0 {
		return beatmap, errors.New("beatmap id is 0")
	}

	return beatmap, err
}

// osuDB reads beatmaps from the osu! database file.
// https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
func osuDB(fn string) (string, []*Beatmap, error) {
	start := time.Now()
	beatmaps := []*Beatmap{}
	username := ""
	f, err := os.Open(fn)
	if err != nil {
		return username, beatmaps, err
	}
	defer f.Close()

	v, err := readInt(f)
	if err != nil {
		return username, beatmaps, err
	}
	LogMsgf("osu!.db version: %d", v)

	if _, err = f.Seek(1*INT+1*BYTE+1*LONG, 1); err != nil {
		return username, beatmaps, err
	}

	if username, err = readString(f); err != nil {
		return username, beatmaps, err
	}
	LogMsgf("username: %s", username)

	nMaps, err := readInt(f)
	if err != nil {
		return username, beatmaps, err
	}
	LogMsgf("osu.db contains %d beatmaps", nMaps)

	zeros := 0
	for i := 1; i <= int(nMaps); i++ {
		if beatmap, err := readMap(f, v); err != nil {
			if err.Error() == "beatmap id is 0" {
				// This "error" occurs really frequently,
				// so don't spam the log file.
				zeros++
			} else {
				LogMsgf("osu!.db map %d: %s", i, err)
			}
		} else {
			beatmaps = append(beatmaps, beatmap)
		}
	}

	if zeros > 0 {
		LogMsgf("%d beatmaps couldn't be parsed because their ID was 0", zeros)
	}
	LogMsgf("parsed %d/%d beatmaps", len(beatmaps), nMaps)
	LogMsgf("took %.3f seconds", time.Now().Sub(start).Seconds())
	return username, beatmaps, err
}

// scoresDB reads scores from the scores database file.
// https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
func scoresDB(fn string) ([]*Score, error) {
	start := time.Now()
	scores := []*Score{}
	f, err := os.Open(fn)
	if err != nil {
		return scores, err
	}
	defer f.Close()

	v, err := readInt(f)
	if err != nil {
		return scores, err
	}
	LogMsgf("scores.db version: %d", v)
	nMaps, err := readInt(f)
	if err != nil {
		return scores, err
	}
	LogMsgf("scores.db contains %d beatmaps", nMaps)

	for i := uint32(1); i <= nMaps; i++ {
		if mapScores, err := readScores(f, i); err != nil {
			LogMsgf("scores.db map %d: %s", err)
		} else {
			for _, score := range mapScores {
				scores = append(scores, score)
			}
		}
	}

	LogMsgf("parsed %d scores for %d beatmaps", len(scores), nMaps)
	LogMsgf("took %.3f seconds", time.Now().Sub(start).Seconds())
	return scores, err
}

// BuildDB parses the osu!.db and scores.db files and builds a DB.
func BuildDB(scoresPath, osuPath string) (*DB, error) {
	db := new(DB)
	scores, err := scoresDB(scoresPath)
	if err != nil {
		return db, err
	}
	username, beatmaps, err := osuDB(osuPath)
	if err != nil {
		return db, err
	}
	return NewDB(username, scores, beatmaps), err
}
