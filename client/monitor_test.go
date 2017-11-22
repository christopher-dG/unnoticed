package unnoticed

import (
	"os"
	"testing"
	"time"
)

// TestWatch tests that Watch returns when the file it's monitoring is modified.
func TestWatch(t *testing.T) {
	if !testing.Short() {
		// This will wait for one minute, so we can skip it if necessary.
		if err := Watch("unnoticed.tmp"); err == nil {
			t.Error("expected err != nil, got nil")
		}
	}

	f, err := os.Create("unnoticed.tmp")
	if err != nil {
		t.Skipf("couldn't create file: %s", err)
	}
	if _, err = f.Write([]byte{'a', 'b', 'c'}); err != nil {
		t.Skipf("couldn't write to file: %s", err)
	}

	t.Log("monitoring unoticed.tmp")
	go func() {
		time.Sleep(time.Second)
		if _, err = f.Write([]byte{'d', 'e', 'f'}); err != nil {
			t.Skipf("couldn't write to file: %s", err)
		}
	}()

	if err = Watch("unnoticed.tmp"); err != nil {
		t.Errorf("expected err == nil, got '%s'", err)
	} else {
		t.Log("successfully returned from Watch")
	}
	os.Remove("unnoticed.tmp")
}
