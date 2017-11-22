package unnoticed

import (
	"crypto/md5"
	"io"
	"os"
	"time"
)

// Watch waits until fn is modified.
func Watch(fn string) error {
	initHash, err := getHash(fn)
	if err != nil {
		// This shouldn't happen, but if it does then wait a
		// bit before returning to avoid spamming my API.
		LogMsgf("couldn't get initial hash value for %s; idling for 1 minute", fn)
		time.Sleep(time.Minute)
		return err
	}

	for {
		hash, err := getHash(fn)
		if err != nil {
			LogMsg(err)
		} else if string(hash) != string(initHash) {
			LogMsgf("%s was modified", fn)
			return nil
		}
		time.Sleep(10 * time.Second)
	}
}

// getHash computes the MD5 hash value for the file fn.
func getHash(fn string) ([]byte, error) {
	f, err := os.Open(fn)
	if err != nil {
		LogMsgf("reading %s failed: %s", fn, err)
		return nil, err
	}
	defer f.Close()
	h := md5.New()
	if _, err := io.Copy(h, f); err != nil {
		LogMsgf("computing the hash for %s failed: %s", fn, err)
		return nil, err
	} else {
		return h.Sum(nil), nil
	}
}
