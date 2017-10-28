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
func OsuPath(fn string) (filePath string, err error) {
	dbRoot := ""
	switch runtime.GOOS {
	case "windows":
		dbRoot = "C:\\\\Program Files (x86)\\osu!\\"
	case "darwin":
		dbRoot = "/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/"
	default:
		dbRoot = "./" // TODO: Where will this go?
	}
	filePath = path.Join(dbRoot, fn)
	_, err = os.Stat(filePath)
	return
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

// accuracy parses a score's accuracy in percent.
func accuracy(score *Score) float64 {
	acc := 0.0
	switch score.Mode {
	case 0: // Standard.
		acc = float64(score.N300+score.N100/3+score.N50/6) /
			float64(score.N300+score.N100+score.N50+score.NMiss)
	case 1: // Taiko.
		acc = float64(score.N300+score.N100/2) /
			float64(score.N300+score.N100+score.NMiss)
	case 2: // CTB.
		acc = float64(score.N300+score.N100+score.N50) /
			float64(score.N300+score.N100+score.N50+score.NKatu+score.NMiss)
	case 3: // Mania.
		acc = float64(score.NGeki+score.N300+2*score.NKatu/3+score.N100/3+score.N50/6) /
			float64(score.NGeki+score.N300+score.NKatu+score.N100+score.N50+score.NMiss)
	}
	return 100 * acc
}
