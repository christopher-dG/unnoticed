package unnoticed

import (
	"fmt"
	"log"
	"os"
	"path"
	"runtime"

	"github.com/0xAX/notificator"
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
	log.Println(msg)
	notify := notificator.New(notificator.Options{
		DefaultIcon: "",
		AppName:     "Unnoticed",
	})
	if err := notify.Push("Unnoticed", msg, "", notificator.UR_NORMAL); err != nil {
		log.Printf("sending desktop notification failed: %s\n", err)
	}
}

// Notifyf sends a desktop notification with the given formatted string.
func Notifyf(format string, a ...interface{}) {
	Notify(fmt.Sprintf(format, a...))
}
