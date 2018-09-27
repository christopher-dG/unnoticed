package main

import "runtime"

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
	// TODO
	switch runtime.GOOS {
	case "windows":
		return "."
	case "darwin":
		return "."
	default:
		return "."
	}
}
