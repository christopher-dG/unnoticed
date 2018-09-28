package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestNewScoresDB(t *testing.T) {
	path := filepath.Join("data", "scores.db")
	if _, err := os.Stat(path); os.IsNotExist(err) {
		t.Skip("no test files")
	}

	_, err := NewScoresDB(path)
	if err != nil {
		t.Fatal("expected err == nil, got:", err)
	}
}
