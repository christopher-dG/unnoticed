package unnoticed

import (
	"errors"
	"fmt"
	"log"
	"os"
	"os/user"
	"path"
	"runtime"

	"github.com/0xAX/notificator"
)

var (
	printLogger *log.Logger = log.New(os.Stdout, log.Prefix(), log.Flags())
	fileLogger  *log.Logger = nil
	fileLogging bool        = false
)

// OsuDir finds the root osu! directory where osu!.db and scores.db can be found.
func OsuDir() (string, error) {
	if dbRootEnv := os.Getenv("OSU_ROOT"); len(dbRootEnv) > 0 {
		if _, err := os.Stat(path.Join(dbRootEnv, "osu!.db")); err != nil {
			return "", errors.New(fmt.Sprintf("osu!.db was not found at %s", dbRootEnv))
		}
		if _, err := os.Stat(path.Join(dbRootEnv, "scores.db")); err != nil {
			return "", errors.New(fmt.Sprintf("scores.db was not found at %s", dbRootEnv))
		}
		return dbRootEnv, nil
	}

	dbRoot := []string{}
	switch runtime.GOOS {
	case "windows":
		dbRoot = append(dbRoot, "C:\\\\Program Files (x86)\\osu!\\", "C:\\\\osu!\\")
		if usr, err := user.Current(); err == nil {
			dbRoot = append(dbRoot, path.Join(usr.HomeDir, "AppData", "Local", "osu!"))
		}

	case "darwin":
		dbRoot = append(
			dbRoot,
			"/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/",
		)
	default:
		dbRoot = append(dbRoot, "./") // TODO: Where will this go?
	}

	for _, dir := range dbRoot {
		if _, err := os.Stat(path.Join(dir, "osu!.db")); err != nil {
			continue
		}
		if _, err := os.Stat(path.Join(dir, "scores.db")); err != nil {
			continue
		}
		LogMsgf("found .db files at %s", dir)
		return dir, nil
	}

	return "", errors.New(".db files were not found")
}

// Notify sends a desktop notification with the given string.
func Notify(msg string) {
	LogMsg(msg)
	notify := notificator.New(notificator.Options{
		DefaultIcon: "",
		AppName:     "Unnoticed",
	})
	if err := notify.Push("Unnoticed", msg, "", notificator.UR_NORMAL); err != nil {
		LogMsgf("sending desktop notification failed: %s", err)
	}
}

// Notifyf sends a desktop notification with the given formatted string.
func Notifyf(format string, a ...interface{}) {
	Notify(fmt.Sprintf(format, a...))
}

// LogSetup tries sto set up file logging with with fn.
func LogSetup(fn string) (*os.File, error) {
	f, err := os.OpenFile(fn, os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
	if err != nil {
		return nil, err
	}
	fileLogger = log.New(f, log.Prefix(), log.Flags())
	fileLogging = true
	return f, nil
}

// LogMsg logs a message.
func LogMsg(msg interface{}) {
	printLogger.Println(msg)
	if fileLogging {
		fileLogger.Println(msg)
	}
}

// LogMsgf logs a formatted message.
func LogMsgf(format string, a ...interface{}) {
	LogMsg(fmt.Sprintf(format, a...))
}

// LoFatal logs a fatal error and exits.
func LogFatal(msg interface{}) {
	LogMsg(msg)
	os.Exit(1)
}

// LogFatalf logs a formatted fatal error and exits.
func LogFatalf(format string, a ...interface{}) {
	LogFatal(fmt.Sprintf(format, a...))
}
