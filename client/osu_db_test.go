package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestNewOsuDB(t *testing.T) {
	path := filepath.Join("data", "osu!.db")
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Skip("no test files")
	}

	_, err := NewOsuDB(path)
	if err != nil {
		t.Fatal("expected err == nil, got:", err)
	}
}
