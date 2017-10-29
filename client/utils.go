package unnoticed

import (
	"fmt"
	"log"
	"os"
	"path"
	"runtime"

	"github.com/0xAX/notificator"
)

var (
	printLogger *log.Logger = log.New(os.Stdout, log.Prefix(), log.Flags())
	fileLogger  *log.Logger = nil
	fileLogging bool        = false
)

// OsuPath joins fn to the root osu! directory.
func OsuPath(fn string) (string, error) {
	dbRoot := ""

	if dbRoot = os.Getenv("OSU_ROOT"); len(dbRoot) > 0 {
		return path.Join(dbRoot, fn), nil
	}

	switch runtime.GOOS {
	case "windows":
		dbRoot = "C:\\\\Program Files (x86)\\osu!\\"
	case "darwin":
		dbRoot = "/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/"
	default:
		dbRoot = "./" // TODO: Where will this go?
	}

	filePath := path.Join(dbRoot, fn)
	_, err := os.Stat(filePath)
	return filePath, err
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
