package main

import (
	"os/user"
	"path/filepath"
	"runtime"

	"github.com/pkg/errors"
)

// Config is the runtime configuration.
type Config struct {
	OsuRoot string `yaml:"osu_root"` // Directory of osu! installation.
}

// DefaultConfig returns a Config with default options.
func DefaultConfig() Config {
	return Config{
		OsuRoot: defaultOsuRoot(),
	}
}

// defaultOsuRoot returns the default osu! installation directory.
func defaultOsuRoot() string {
	switch runtime.GOOS {
	case "windows":
		u, err := user.Current()
		if err != nil {
			userFatal(errors.WithStack(err))
		}
		return filepath.Join(u.HomeDir, "AppData", "Local", "osu!")
	case "darwin":
		return "/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!"
	default:
		return "."
	}
}
