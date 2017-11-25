// ==UserScript==
// @name         [Unnoticed] Leaderboards
// @namespace    https://github.com/christopher-dG/unnoticed
// @version      1.1.0
// @description  Display unranked leaderboard entries gathered by [Unnoticed] on their respective beatmap pages
// @author       Node
// @updateURL    https://github.com/christopher-dG/unnoticed/raw/master/contrib/userscript/unnoticed.user.js
// @match        https://osu.ppy.sh/*/*
// @include      https://p9bztcmks6.execute-api.us-east-1.amazonaws.com/*
// @grant        GM_xmlhttpRequest
// @require      https://code.jquery.com/jquery-3.2.1.min.js
// @require      http://momentjs.com/downloads/moment.min.js
// @connect      p9bztcmks6.execute-api.us-east-1.amazonaws.com
// @run-at document-end
// ==/UserScript==

(function(){
    'use strict';

    var mods_enum = {
        ''    : 0,
        'NF'  : 1,
        'EZ'  : 2,
        'HD'  : 8,
        'HR'  : 16,
        'SD'  : 32,
        'DT'  : 64,
        'RX'  : 128,
        'HT'  : 256,
        'NC'  : 512,
        'FL'  : 1024,
        'AT'  : 2048,
        'SO'  : 4096,
        'AP'  : 8192,
        'PF'  : 16384,
        '4K'  : 32768,
        '5K'  : 65536,
        '6K'  : 131072,
        '7K'  : 262144,
        '8K'  : 524288,
        'FI'  : 1048576,
        'RD'  : 2097152,
        'LM'  : 4194304,
        '9K'  : 16777216,
        '10K' : 33554432,
        '1K'  : 67108864,
        '3K'  : 134217728,
        '2K'  : 268435456,
    };

    function accuracy(mode, c300, c100, c50, cmiss, ckatu, cgeki){
        var return_int;
        switch(mode){
            case 0:
                return_int =
                    (c300 * 300 + c100 * 100 + c50 * 50) /
                    (c300 * 300 + c100 * 300 + c50 * 300 + cmiss * 300)
                    * 100;
                break;
            case 1:
                return_int =
                    (c300 * 300 + c100 * 150) /
                    (c300 * 300 + c100 * 300 + cmiss * 300)
                    * 100;
                break;
            case 2:
                return_int =
                    (c300 + c100 + c50) /
                    (c300 + c100 + c50 + cmiss + ckatu)
                    * 100;
                break;
            case 3:
                return_int =
                    (c300 * 300 + cgeki * 300 + ckatu * 200 + c100 * 100 + c50 * 50) /
                    (c300 * 300 + cgeki * 300 + ckatu * 300 + c100 * 300 + c50 * 300 + cmiss * 300)
                    * 100;
                break;
        }
        return return_int;
    }

    function grade(mode, mods, accuracy, c300, c100, c50, cmiss){
        var return_string = "D";
        switch(mode){
            case 0:
                var ctotal = c300 + c100 + c50 + cmiss;
                var p300 = c300 / ctotal;
                if(accuracy == 100)
                    return_string = "X";
                else if(p300 > 0.9 && c50 / ctotal < 0.01 && cmiss == 0)
                    return_string = "S";
                else if(p300 > 0.8 && cmiss == 0 || p300 > 0.9)
                    return_string = "A";
                else if(p300 > 0.7 && cmiss == 0 || p300 > 0.8)
                    return_string = "B";
                else if(c300 > 0.6)
                    return_string = "C";
                break;
            case 1:
                if(accuracy == 100)
                    return_string = "X";
                else if(accuracy > 95 && cmiss == 0)
                    return_string = "S";
                else if(accuracy > 90)
                    return_string = "A";
                else if(accuracy > 80)
                    return_string = "B";
                else if(accuracy > 70)
                    return_string = "C";
                break;
            case 2:
                if(accuracy == 100)
                    return_string = "X";
                else if(accuracy > 98)
                    return_string = "S";
                else if(accuracy > 94)
                    return_string = "A";
                else if(accuracy > 90)
                    return_string = "B";
                else if(accuracy > 85)
                    return_string = "C";
            case 3:
                if(accuracy == 100)
                    return_string = "X";
                else if(accuracy > 95)
                    return_string = "S";
                else if(accuracy > 90)
                    return_string = "A";
                else if(accuracy > 80)
                    return_string = "B";
                else if(return_string > 70)
                    return_string = "C";
                break;
        }
        if((return_string == "X" || return_string == "S") && (mods.includes("HD") || mods.includes("FL")))
            return_string += "H";
        return return_string;
    }

    function mods(enabled_mods){
        var return_array = [];
        for(var mod in mods_enum){
            if((mods_enum[mod] & enabled_mods) != 0)
                return_array.push(mod);
        }
        return return_array;
    }

    function mods_string(mods_array){
        if(mods_array.length > 0){
            if(mods_array.includes("NC"))
                mods_array.splice(mods_array.indexOf("DT"), 1);

            if(mods_array.includes("PF"))
                mods_array.splice(mods_array.indexOf("SD"), 1);

            return mods_array.join(",");
        }else{
            return "None";
        }
    }

    var api_base = "https://p9bztcmks6.execute-api.us-east-1.amazonaws.com/unnoticed/proxy?b=";

    // check if on an unranked beatmap page
    if($(".beatmapTab").length > 0 && $("h2:contains(Top 50 Scoreboard)").length === 0){
        var current_url = window.location.href;
        var mode = 0;
        if(current_url.split("&m=").length > 1)
            mode = parseInt(current_url.split("&m=").pop().split("&")[0]);



        var active_beatmap = $(".beatmapTab.active");
        var beatmap_id =
            active_beatmap.attr("href").split("/").pop().split("&")[0];

        var forced_mode =
            parseInt(active_beatmap.attr("href").split("&m=").pop());

        if(forced_mode != 0) mode = forced_mode;

        var showOutdated = window.location.hash == "#showOutdated"

        GM_xmlhttpRequest({
            method: "GET",
            url: api_base + beatmap_id,
            onload: function(response_raw){
                if(response_raw.status != 200){
                    console.log(response_raw.responseText);
                }else{
                    var response = JSON.parse(response_raw.responseText);
                    var scores = [];
                    var scores_mode = response.scores[beatmap_id].filter(function(a){ return a.mode == mode; });
                    if(!showOutdated) scores_mode = scores_mode.filter(function(a){ return !a.outdated; });

                    scores_mode.forEach(function(score){
                        var exists = false;

                        scores.forEach(function(score_check, index){
                            if(score_check.player_id == score.player_id){
                                exists = true;
                                if(score_check.score < score.score)
                                    scores[index] = score;
                            }
                        });

                        if(!exists)
                            scores.push(score);
                    });

                    scores = scores.sort(function(a, b){ return a.score - b.score; })
                                   .reverse().slice(0, 50);

                    $('<div style="margin:20px auto; background: rgb(208, 231, 249); border-radius: 5px; width: 50%; padding: 15px;">'
                    + '<center>This map is UNRANKED.<br />'
                    + 'As such, it doesn\'t reward any pp and scores are retrieved via <a target="_blank" href="https://github.com/christopher-dG/unnoticed">[Unnoticed]</a>.</center>'
                    + '</div>').insertAfter("#songinfo");

                    var insert_html =
                      '<div id="tablist" style="margin-top: 15px; margin-bottom: 15px;">'
                    + '<ul>'
                    + '<li><a class="';
                    if(mode == 0) insert_html += 'active';
                    insert_html +=
                    '" href="/p/beatmap?b=' + beatmap_id + '&m=0">osu! Standard</a></li>'
                    + '<li><a class="';
                    if(mode == 1) insert_html += 'active';
                    insert_html +=
                    '" href="/p/beatmap?b=' + beatmap_id + '&m=1">Taiko</a></li>'
                    + '<li><a class="';
                    if(mode == 2) insert_html += 'active';
                    insert_html +=
                    '" href="/p/beatmap?b=' + beatmap_id + '&m=2">Catch The Beat</a></li>'
                    + '<li><a class="';
                    if(mode == 3) insert_html += 'active';
                    insert_html +=
                    '" href="/p/beatmap?b=' + beatmap_id + '&m=3">osu!mania</a></li>'
                    + '</ul>'
                    + '</div>'
                    + '<label><input type="checkbox" id="showOutdated" style="vertical-align: middle;"> Show outdated scores</label>';

                    scores.forEach(function(score, index){
                        var mods_array = mods(score.mods);
                        var pp = score.pp == null ? 'NA' : score.pp.toFixed(2);
                        score.accuracy = accuracy(mode, score.n300, score.n100, score.n50, score.nmiss, score.nkatu, score.ngeki);
                        score.grade = grade(mode, mods_array, score.accuracy, score.n300, score.n100, score.n50, score.nmiss);
                        score.flag = score.flag.toLowerCase();

                        var outdated_style = score.outdated ? "opacity: 0.7;" : "";

                        if(index == 0){
                            insert_html
                                += '<div style="text-align: center; width: 100%;">'
                                + '<div style="display: inline-block; margin: 3px; text-align: left;">'
                                + '<table class="scoreLeader" style="margin-top: 10px;' + outdated_style + '" cellpadding="0" cellspacing="0">'
                                + '<tr><td class="title" colspan=3>'
                                + '<img class="flag" src="//s.ppy.sh/images/flags/' + score.flag + '.gif" />'
                                + ' <a href="/u/' + score.player_id + '"> '
                                + score.player + '</a> is in the lead! (<time class="timeago" datetime="'
                                + moment.unix(score.date).format() + '">'
                                + moment.unix(score.date).fromNow() + '</time>)</td></tr>'
                                + '<tr class="row1p">'
                                + '<td><strong>Score</strong></td><td>' + score.score.toLocaleString()
                                + ' (' + score.accuracy.toFixed(2) + '%)</td>'
                                + '<td class="rank" width="120px" align="center" colspan="1" rowspan="7"><img src="//s.ppy.sh/images/'
                                + score.grade
                                + '.png" /></td>'
                                + '</tr>'
                                + '<tr class="row2p"><td><strong>Max Combo</strong></td><td>' + score.combo + '</td></tr>';
                            if(mode == 3){
                                insert_html
                                    += '<tr class="row1p"><td><strong>MAX / 300 / 200</strong></td><td>'
                                    + score.ngeki + ' / ' + score.n300 + ' / ' + score.nkatu + '</td></tr>'
                                    + '<tr class="row2p"><td><strong>100 / 50 / Misses</strong></td><td>'
                                    + score.n100 + ' / ' + score.n50 + ' / ' + score.nmiss + '</td></tr>';
                            }else{
                                insert_html
                                    += '<tr class="row1p"><td><strong>300 / 100 / 50</strong></td><td>'
                                    + score.n300 + ' / ' + score.n100 + ' / ' + score.n50 + '</td></tr>'
                                    + '<tr class="row2p"><td><strong>Misses</strong></td><td>' + score.nmiss + '</td></tr>'
                                    + '<tr class="row1p"><td><strong>Geki (Elite Beat!)</strong></td><td>' + score.ngeki + '</td></tr>'
                                    + '<tr class="row2p"><td><strong>';
                                if(mode == 2)
                                    insert_html += 'Droplet misses';
                                else
                                    insert_html += 'Katu (Beat!)';
                                insert_html
                                    += '</strong></td><td>' + score.nkatu + '</td></tr>';
                            }
                            insert_html
                                += '<tr class="row1p"><td><strong>Mods</strong></td><td>' + mods_string(mods_array) + '</td></tr>'
                                + '<tr class="row2p"><td><strong>pp</strong></td><td>' + pp + '</td></tr>'
                                + '</table>'
                                + '</div>'
                                + '<div class="clear"></div>'
                                + '</div>'
                                + '<a name="scores"></a>'
                                + '<h2 style="margin-left: 4px;">Top 50 Scoreboard</h2>'
                                + '<div class="beatmapListing">'
                                + '<table width="100%" cellspacing="0">'
                                + '<tr class="titlerow">'
                                + '<th></th><th><strong>Rank</strong></th>'
                                + '<th><strong>Score</strong></th>'
                                + '<th><strong>pp</strong></th>'
                                + '<th><strong>Accuracy</strong></th>'
                                + '<th><strong>Player</strong></th>'
                                + '<th><strong>Max Combo</th>';
                            if(mode == 3){
                                insert_html
                                    += '<th><strong>MAX</strong></th>'
                                    + '<th><strong>300</strong></th>'
                                    + '<th><strong>200</strong></th>'
                                    + '<th><strong>100</strong></th>'
                                    + '<th><strong>50</strong></th>'
                                    + '<th><strong>Miss</strong></th>';
                            }else{
                                insert_html
                                    += '<th><strong>300 / 100 / 50</strong></th>'
                                    + '<th><strong>Geki</strong></th><th><strong>';
                                if(mode == 2)
                                    insert_html += 'Droplet Miss';
                                else
                                    insert_html += 'Katu';
                                insert_html
                                    += '</strong></th><th><strong>Misses</strong></th>';
                            }
                            insert_html
                                += '<th><strong>Mods</strong></th>'
                                + '<th><strong>Date</strong></th>'
                                + '<th></th></tr>';
                        }

                        insert_html += '<tr class="';
                        if(index % 2 == 0)
                            insert_html += 'row2p'
                        else
                            insert_html += 'row1p';
                        insert_html
                            += '" style="' + outdated_style + '">'
                            + '<td><span>#' + (index + 1) + '</span></td>'
                            + '<td><img src="//s.ppy.sh/images/'
                            + score.grade + '_small.png" /></td>'
                            + '<td><b>' + score.score.toLocaleString() + '</b></td>'
                            + '<td>' + pp + '</td>'
                            + '<td>' + score.accuracy.toFixed(2) + '%</td>'
                            + '<td><img class="flag" src="//s.ppy.sh/images/flags/' + score.flag + '.gif" />'
                            + ' <a href="/u/' + score.player_id + '">' + score.player + '</a></td>'
                            + '<td>' + score.combo + '</td>';
                        if(mode == 3){
                            insert_html
                                += '<td>' + score.ngeki + '</td>'
                                + '<td>' + score.n300 + '</td>'
                                + '<td>' + score.nkatu + '</td>'
                                + '<td>' + score.n100 + '</td>'
                                + '<td>' + score.n50 + '</td>'
                        }else{
                            insert_html
                                += '<td>' + score.n300 + '&nbsp&nbsp/&nbsp;&nbsp;' + score.n100 + '&nbsp;&nbsp;/&nbsp;&nbsp;' + score.n50 + '</td>'
                                + '<td>' + score.ngeki + '</td>'
                                + '<td>' + score.nkatu + '</td>'
                        }
                        insert_html
                            += '<td>' + score.nmiss + '</td>'
                            + '<td>' + mods_string(mods_array) + '</td>'
                            + '<td><time class="timeago" datetime="' + moment.unix(score.date).format()
                            + '">' + moment.unix(score.date).fromNow() + '</time></td>'
                            + '<td><a href=https://github.com/christopher-dG/unnoticed/wiki/Viewing-Leaderboards#outdated-scoresreporting>Report</a></td>'
                            + '<td style="opacity: 0; pointer-events: none;"><a>Report</a></td>'
                            + '</tr>';
                    });

                    insert_html += '</table></div>';
                    $(insert_html).insertAfter(".paddingboth");

                    if(showOutdated){
                        $("#showOutdated").prop('checked', true);
                    }

                    $("#showOutdated").change(function(){
                        if(this.checked){
                            window.location.hash = "#showOutdated";
                            location.reload();
                        }else{
                            window.location.hash = "";
                            location.reload();
                        }
                    });
                }
            }
        });
    }
})();
