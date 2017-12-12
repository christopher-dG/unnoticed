package unnoticed

import (
	"os"
	"testing"
	"time"
)

func TestWatchDir(t *testing.T) {
	wd, err := os.Getwd()
	if err != nil {
		t.Skipf("couldn't get working directory: %s", err)
	}

	tmpFile := "f1.tmp"
	defer os.RemoveAll(tmpFile)
	fs := make(chan int)

	go WatchDir(fs, make(chan bool, 1), wd)
	time.Sleep(time.Second)
	if _, err := os.Create(tmpFile); err != nil {
		t.Skipf("couldn't create file: %s", err)
	}
	select {
	case notif := <-fs:
		if notif != DirNotification {
			t.Errorf("expected notif == DirNotification (2), got %d", notif)
		}
	case <-time.After(time.Second):
		t.Error("TestWatchDir took too long")
	}
}

func TestWatchFile(t *testing.T) {
	tmpFile := "f2.tmp"
	f, err := os.Create(tmpFile)
	if err != nil {
		t.Skipf("couldn't create file: %s", err)
	}
	defer os.RemoveAll(tmpFile)
	fs := make(chan int)

	go WatchFile(fs, tmpFile)
	time.Sleep(time.Second)
	if _, err = f.Write([]byte{'.'}); err != nil {
		t.Skipf("couldn't write to file: %s", err)
	}
	select {
	case notif := <-fs:
		if notif != FileNotification {
			t.Errorf("expected notif == FileNotification (1), got %d", notif)
		}
	case <-time.After(time.Second):
		t.Error("TestWatchFile took too long")
	}
}
