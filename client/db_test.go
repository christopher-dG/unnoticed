package unnoticed

import (
	"encoding/json"
	"io/ioutil"
	"path"
	"testing"
)

// TestDB tests database generation and JSON marshalling.
// This covers everything in parsing and a bunch of stuff in types.
func TestDB(t *testing.T) {
	db, err := BuildDB(
		path.Join("testdata", "scores.db"),
		path.Join("testdata", "osu!.db"),
	)
	if err != nil {
		t.Errorf("Expected err == nil, got '%s'", err)
	}
	if db.Username != "Node" {
		t.Errorf("Expected db.Username == 'Node', got '%s'", db.Username)
	}
	if len(db.Scores) != 5569 {
		t.Errorf("Expected len(db.Scores) == 5569, got %d", len(db.Scores))
	}
	if len(db.Beatmaps) != 60660 {
		t.Errorf("Expected len(db.Beatmaps) == 60660, got %d", len(db.Beatmaps))
	}

	out, err := json.Marshal(db)
	if err != nil {
		t.Errorf("Expected err == nil, got '%s'", err)
	}
	expected, _ := ioutil.ReadFile(path.Join("testdata", "db.json"))
	if err != nil {
		t.Errorf("Expected err == nil, got '%s'", err)
	}
	if string(out) != string(expected) {
		t.Error("JSON output differs from expected value")
	}
}
