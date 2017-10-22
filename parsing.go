package unnoticed

import (
	"encoding/binary"
	"log"
	"os"
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
	if score.Mode, err = readByte(f); err != nil {
		flag = true
	}
	if score.Date, err = readInt(f); !flag && err != nil {
		flag = true
	}
	if score.MD5, err = readString(f); !flag && err != nil {
		flag = true
	}
	if _, err = readString(f); !flag && err != nil {
		flag = true
	}
	if _, err = readString(f); !flag && err != nil {
		flag = true
	}
	if score.N300, err = readShort(f); !flag && err != nil {
		flag = true
	}
	if score.N100, err = readShort(f); !flag && err != nil {
		flag = true
	}
	if score.N50, err = readShort(f); !flag && err != nil {
		flag = true
	}
	if score.NGeki, err = readShort(f); !flag && err != nil {
		flag = true
	}
	if score.NKatu, err = readShort(f); !flag && err != nil {
		flag = true
	}
	if score.NMiss, err = readShort(f); !flag && err != nil {
		flag = true
	}
	if score.Score, err = readInt(f); !flag && err != nil {
		flag = true
	}
	if score.Combo, err = readShort(f); !flag && err != nil {
		flag = true
	}
	if score.IsFC, err = readBool(f); !flag && err != nil {
		flag = true
	}
	if score.Mods, err = readInt(f); !flag && err != nil {
		flag = true
	}
	if _, err = readString(f); !flag && err != nil {
		flag = true
	}
	if _, err := readLong(f); !flag && err != nil {
		flag = true
	}
	if _, err = f.Seek(1*INT, 1); !flag && err != nil {
		flag = true
	}
	score.ID, err = readLong(f)
	return
}

// readScores reads all scores for one map.
func readScores(f *os.File) ([]*Score, error) {
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
			log.Printf("score %d: %s\n", i, err)
		} else {
			scores = append(scores, score)
		}
	}

	for _, score := range scores {
		if score.MD5 != md5 {
			log.Printf("mismatched beatmap MD5: expected %s, got %s\n", md5, score.MD5)
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
	size, err := readInt(f)
	if err != nil {
		return beatmap, err // This too.
	}
	defer f.Seek(start+int64(size)+4, 0)

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
	if beatmap.Status, err = readByte(f); err != nil {
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
	if _, err = f.Seek(2*INT+4*BYTE+1*SHORT+1*SINGLE, 1); err != nil {
		return beatmap, err
	}
	beatmap.Mode, err = readByte(f)
	return beatmap, err
}

// osuDB reads beatmaps from the osu! database file.
// https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
func osuDB(fn string) (string, []*Beatmap, error) {
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
	log.Printf("osu!.db version: %d\n", v)

	if _, err = f.Seek(1*INT+1*BYTE+1*LONG, 1); err != nil {
		return username, beatmaps, err
	}

	if username, err = readString(f); err != nil {
		return username, beatmaps, err
	}
	log.Printf("username: %s\n", username)

	nMaps, err := readInt(f)
	if err != nil {
		return username, beatmaps, err
	}
	log.Printf("osu.db contains %d beatmaps\n", nMaps)

	for i := 1; i <= int(nMaps); i++ {
		if beatmap, err := readMap(f, v); err != nil {
			log.Printf("map %d: %s\n", i, err)
		} else {
			beatmaps = append(beatmaps, beatmap)
		}
	}

	log.Printf("parsed %d/%d beatmaps\n", len(beatmaps), nMaps)
	return username, beatmaps, err
}

// scoresDB reads scores from the scores database file.
// https://osu.ppy.sh/help/wiki/osu!_File_Formats/Db_(file_format)
func scoresDB(fn string) ([]*Score, error) {
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
	log.Printf("scores.db version: %d\n", v)
	nMaps, err := readInt(f)
	if err != nil {
		return scores, err
	}
	log.Printf("scores.db contains %d beatmaps\n", nMaps)

	for i := uint32(1); i <= nMaps; i++ {
		if mapScores, err := readScores(f); err != nil {
			log.Printf("score %d: %s\n", err)
		} else {
			for _, score := range mapScores {
				scores = append(scores, score)
			}
		}
	}

	log.Printf("parsed %d scores for %d beatmaps\n", len(scores), nMaps)
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
