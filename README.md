# [Unnoticed]

[![Build Status](https://travis-ci.org/christopher-dG/unnoticed.svg?branch=master)](https://travis-ci.org/christopher-dG/unnoticed)
[![Discord](https://img.shields.io/badge/Discord-[Unnoticed]-7289da.svg)](https://discord.gg/8gbhTNA)

**Unranked leaderboards for [osu!](https://osu.ppy.sh/home).**

## Uploading Scores

To upload your scores, use one of the executables found on the
[releases page](https://github.com/christopher-dG/unnoticed/releases).
You can either use `scan` every time you wish to upload, or leave `watch`
running in the background to have your scores uploaded every time you finish
playing.

## Viewing Leaderboards

Leaderboards are accessible via the public
[Discord server](https://discord.gg/8gbhTNA). To check a specific map's
leaderboard, just paste its link into any channel (it should look like
`osu.ppy.sh/b/123`, and not `osu.ppy.sh/s/123`).

## Log File

If something goes wrong with processing and uploading your scores, it's a good
idea to investigate the log file. Its location is dependent on your OS:

* Windows: `C:\\Users\YourUsername\AppData\Local\Temp\unnoticed{scan,watch}.log`
* MacOS: `$TMPDIR/unnoticed-{scan,watch}.log`
* Linux: `/tmp/unnoticed-{scan,watch}.log`

## osu! Directory
