package unnoticed

import (
	"encoding/json"
	"io/ioutil"
	"path"
	"runtime"
	"testing"
)

func TestDB(t *testing.T) {
	if runtime.GOOS == "darwin" {
		t.SkipNow()
	}
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

func TestDarwin(t *testing.T) {
	if runtime.GOOS != "darwin" {
		t.SkipNow()
	}
	db, err := BuildDB(
		path.Join("testdata", "scores_darwin.db"),
		path.Join("testdata", "osu!_darwin.db"),
	)
	if err != nil {
		t.Errorf("Expected err == nil, got '%s'", err)
	}
	if db.Username != "Raspberriel" {
		t.Errorf("Expected db.Username == 'Raspberriel', got '%s'", db.Username)
	}
	if len(db.Scores) != 6226 {
		t.Errorf("Expected len(db.Scores) == 6226, got %d", len(db.Scores))
	}
	if len(db.Beatmaps) != 3220 {
		t.Errorf("Expected len(db.Beatmaps) == 3220, got %d", len(db.Beatmaps))
	}
}
