package unnoticed

import (
	"fmt"
	"os"
	"testing"
	"time"
)

// TestWatch tests that Watch returns when the file it's monitoring is modified.
func TestWatch(t *testing.T) {
	count := 5
	wd, err := os.Getwd()
	if err != nil {
		t.Skipf("couldn't get working directory: %s", err)
	}

	go func() {
		for i := 1; i <= count; i++ {
			time.Sleep(time.Second)
			_, err := os.Create(fmt.Sprintf("unnoticed%d.tmp", i))
			if err != nil {
				t.Skipf("couldn't create file: %s", err)
			}
		}
	}()

	go func() { // The call to Watch should return immediately after the above goroutine.
		time.Sleep(10 * time.Second)
		t.Error("TestWatch took too long")
	}()
	err = Watch(wd)

	if err != nil {
		t.Errorf("expected err == nil, got '%s'", err)
	}

	for i := 1; i <= count; i++ {
		os.Remove(fmt.Sprintf("unnoticed%d.tmp", i))
	}
}
