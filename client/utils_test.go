package unnoticed

import (
	"os"
	"os/user"
	"path"
	"runtime"
	"testing"
)

func TestOsuDir(t *testing.T) {
	if _, err := OsuDir(); err == nil {
		t.Error("expected OsuDir() != nil, got nil")
	}

	var dirs []string
	switch runtime.GOOS {
	case "windows":
		dirs = []string{
			path.Join("C", "Program Files (x86)", "osu!"),
			path.Join("C", "osu!"),
		}
		if usr, err := user.Current(); err == nil {
			dirs = append(dirs, path.Join(usr.HomeDir, "AppData", "Local", "osu!"))
		}

	case "darwin":
		dirs = []string{path.Join(
			"Applications", "osu!.app", "Contents", "Resources",
			"drive_c", "Program Files", "osu!",
		)}
	case "linux":
		dirs = []string{"./"}
	}

	// Other OSs will probably run into permission issues here,
	// so only test on Linux where we search the current directory.
	if runtime.GOOS == "linux" {
		testDirs(t, dirs)
	}

	// Test the behaviour when OSU_ROOT is set.
	if err := os.Mkdir("osu!", os.ModePerm); err != nil {
		t.Skipf("couldn't create directory: %s", err)
	}
	if err := os.Setenv("OSU_ROOT", "osu!"); err != nil {
		t.Skipf("couldn't set environment variable: %s", err)
	}
	if _, err := OsuDir(); err == nil {
		t.Error("expected err != nil, got nil")
	}
	if _, err := os.Create(path.Join("osu!", "osu!.db")); err != nil {
		t.Skipf("couldn't create file: %s", err)
	}
	if _, err := OsuDir(); err == nil {
		t.Error("expected err != nil, got nil")
	}
	if _, err := os.Create(path.Join("osu!", "scores.db")); err != nil {
		t.Skipf("couldn't create file: %s", err)
	}
	if osuDir, err := OsuDir(); err != nil {
		t.Errorf("expected err == nil, got '%s'", err)
	} else if osuDir != "osu!" {
		t.Errorf("expected OsuDir() == 'osu!', got '%s'", osuDir)
	}
	os.RemoveAll("osu!")
}

func testDirs(t *testing.T, dirs []string) {
	t.Logf("testing directories: %s", dirs)
	for _, dir := range dirs {
		remove := false
		if _, err := os.Stat(dir); err != nil {
			remove = true
		}
		if err := os.MkdirAll(dir, os.ModePerm); err != nil {
			t.Logf("couldn't create directory %s: %s", dir, err)
		} else if _, err := OsuDir(); err == nil {
			t.Error("expected OsuDir() != nil, got nil")
		} else if _, err = os.Create(path.Join(dir, "osu!.db")); err != nil {
			t.Logf("couldn't create file osu!.db: %s", err)
		} else if _, err := OsuDir(); err == nil {
			t.Error("expected OsuDir() != nil, got nil")
		} else if _, err := os.Create(path.Join(dir, "scores.db")); err != nil {
			t.Logf("couldn't create file scores.db: %s", err)
		} else if osuDir, err := OsuDir(); err != nil {
			t.Errorf("expected err == nil, got '%s'", err)
		} else if osuDir != dir {
			t.Errorf("expected OsuDir() == %s, got '%s'", dir, osuDir)
		}
		if remove {
			os.RemoveAll(dir)
		} else {
			os.Remove("osu!.db")
			os.Remove("scores.db")
		}
	}
}
