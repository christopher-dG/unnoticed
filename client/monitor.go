package unnoticed

import (
	"crypto/md5"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"
)

// Watch waits until fn is modified.
func Watch(fn string) {
	path, err := filepath.Abs(fn)
	if err != nil {
		LogMsg(err)
		path = fn
	}

	initHash, err := getHash(path)
	if err != nil {
		// This shouldn't happen, but if it does then wait a
		// bit before returning to avoid spamming my API.
		LogMsg(err)
		LogMsgf("Couldn't get initial hash value for %s", path)
		time.Sleep(time.Minute)
		return
	}
	fmt.Printf("%x\n", initHash)
	for {
		hash, err := getHash(path)
		if err != nil {
			LogMsg(err)
		} else if string(hash) != string(initHash) {
			LogMsgf("%s was modified", path)
			return
		}
		time.Sleep(time.Second * 10)
	}
}

// getHash computes the MD5 hash value for the file fn.
func getHash(fn string) ([]byte, error) {
	f, err := os.Open(fn)
	if err != nil {
		LogMsgf("reading %s failed", fn)
		return nil, err
	}
	defer f.Close()
	h := md5.New()
	if _, err := io.Copy(h, f); err != nil {
		LogMsgf("computing the hash for %s failed", fn)
		return nil, err
	} else {
		return h.Sum(nil), nil
	}
}
