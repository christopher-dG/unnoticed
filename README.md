# [Unnoticed]

[![Build Status](https://travis-ci.org/christopher-dG/unnoticed.svg?branch=master)](https://travis-ci.org/christopher-dG/unnoticed)
[![Discord](https://img.shields.io/badge/Discord-[Unnoticed]-7289da.svg)](https://discord.gg/F8GqFMF)

**[Unnoticed] provides leaderboards for [osu!](https://osu.ppy.sh/home)
beatmaps of any game mode and any ranked status.**

## Uploading Scores

To upload your scores, use one of the executables found on the
[releases page](https://github.com/christopher-dG/unnoticed/releases).
You can either use `scan` every time you wish to upload, or leave `watch`
running in the background to have your scores uploaded every time you finish
playing.

## Viewing Leaderboards

Leaderboards are accessible via the public
[Discord server](https://discord.gg/F8GqFMF). To check a specific map's
leaderboard, just paste its link into `#leaderboards` (it should look like
`osu.ppy.sh/b/123`, and not `osu.ppy.sh/s/123`). While unranked maps are the
intended use case, other scores are also recorded so you won't lose that
awesome score you set on Haitai when it was still qualified.

## osu! Directory

By default, your osu! database files (`scores.db` and `osu!.db`) are assumed to
be in the following locations, dependent on your OS:

* Windows: `C:\\Program Files (x86)\osu!\` or
  `C:\\Users\YourUsername\AppData\Local\osu!`
* MacOS: `/Applications/osu!.app/Contents/Resources/drive_c/Program Files/osu!/`
* Linux: `./` (whatever directory you run the executable in)

If you keep your osu! directory somewhere else, you can set the `OSU_ROOT`
system variable to specify where it is. Otherwise, you'll be prompted to enter
the location yourself.

## Log File

If something goes wrong with processing and uploading your scores, it's a good
idea to investigate the log file. Its location is dependent on your OS:

* Windows: `C:\\Users\YourUsername\AppData\Local\Temp\osu-{scan,watch}.log`
* MacOS: `$TMPDIR/osu-{scan,watch}.log`
* Linux: `/tmp/osu-{scan,watch}.log`

## API

A public HTTP endpoint is provided for retrieving scores. It can be used like so:

* `GET https://p9bztcmks6.execute-api.us-east-1.amazonaws.com/unnoticed/proxy?b=BEATMAP_ID`
* `GET https://p9bztcmks6.execute-api.us-east-1.amazonaws.com/unnoticed/proxy?b=ID1,ID2,ID3`

The response comes in this format:

```json
{
  "info": "",
  "error": "",
  "nscores": 1,
  "scores": {
    "1181750": [
      {
        "player_id": 1,
        "mode": 0,
        "player": "username",
        "n300": 682,
        "n100": 36,
        "n50": 1,
        "ngeki": 112,
        "nkatu": 16,
        "nmiss": 8,
        "score": 6159390,
        "combo": 502,
        "fc": false,
        "mods": 0,
        "date": 1492835820,
        "outdated": false
      },
    ]
  }
}
```

Note that the beatmap ID keys inside `scores` are strings rather than integers
(more information on why [here](https://stackoverflow.com/a/1451857)).

***

This project is in no way affiliated with [osu!](https://osu.ppy.sh/home).
