// ==UserScript==
// @name         [Unnoticed] Leaderboards
// @namespace    https://github.com/christopher-dG/unnoticed
// @version      0.2
// @description  Display unranked leaderboard entries gathered by Unnoticed on their respective beatmap pages
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
        ''   : 0,
        'NF' : 1,
        'EZ' : 2,
        ''   : 4,
        'HD' : 8,
        'HR' : 16,
        'SD' : 32,
        'DT' : 64,
        'RX' : 128,
        'HT' : 256,
        'NC' : 512,
        'FL' : 1024,
        'AT' : 2048,
        'SO' : 4096,
        'AP' : 8192,
        'PF' : 16384,
    };

    function accuracy(c300, c100, c50, cmiss){
        return +
            ((c300 * 300 + c100 * 100 + c50 * 50)
            /  (c300 * 300 + c100 * 300 + c50 * 300 + cmiss * 300)
            *  100)
            .toFixed(2);
    }

    function grade(c300, c100, c50, cmiss, mods){
        var ctotal = c300 + c100 + c50 + cmiss;
        var p300 = c300 / ctotal;
        if(c100 == 0 && c50 == 0 && cmiss == 0){
            if(mods.includes("HD") || mods.includes("FL"))
                return "XH";
            else
                return "X";
        }else if(p300 > 0.9 && c50 / ctotal < 0.01 && cmiss == 0){
            if(mods.includes("HD") || mods.includes("FL"))
                return "SH";
            else
                return "S";
        }else if(p300 > 0.8 && cmiss == 0 || p300 > 0.9){
            return "A";
        }else if(p300 > 0.7 && cmiss == 0 || p300 > 0.8){
            return "B";
        }else if(c300 > 0.6){
            return "C";
        }else{
            return "D";
        }
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

    // check if a on an unranked beatmap page
    if($(".beatmapTab").length > 0 && $(".scoreLeader").length === 0){
        console.log("beatmap unranked, retrieving scores via unnoticed api");
        var beatmap_id = $(".beatmapTab.active")
                        .attr("href").split("/").pop().split("&")[0];
        console.log(beatmap_id);
        GM_xmlhttpRequest({
            method: "GET",
            url: api_base + beatmap_id,
            onload: function(response_raw){
                var response = JSON.parse(response_raw.responseText);

                var scores = [];

                response.scores[beatmap_id].forEach(function(score){
                    var exists = false;

                    scores.forEach(function(score_check, index){
                        if(score_check.player_id == score.player_id){
                            exists = true;
                            if(score_check.score < score.score)
                                scores[index] = score;
                        }
                    });

                    if(!exists){
                        scores.push(score);
                    }
                });

                scores = scores.sort(function(a, b){ return a.score - b.score; })
                               .reverse();

                if(scores.length > 0){
                    $('<div style="margin:20px auto; background: rgb(208, 231, 249); border-radius: 5px; width: 50%; padding: 15px;">'
                    + '<center>This map is UNRANKED.<br />'
                    + 'As such, it doesn\'t reward any pp and scores are retrieved via <a target="_blank" href="https://github.com/christopher-dG/unnoticed">[Unnoticed]</a>.</center>'
                    + '</div>').insertAfter("#songinfo");

                var insert_html = 
                      '<div style="text-align: center; width: 100%;">'
                    + '<div style="display: inline-block; margin: 3px; text-align: left;">'
                    + '<table class="scoreLeader" style="margin-top: 10px;" cellpadding="0" cellspacing="0">'
                    + '<tr><td class="title" colspan=3><a href="/u/' + scores[0].player_id + '"> '
                    + scores[0].player + '</a> is in the lead! (<time class="timeago" datetime="' 
                    + moment.unix(scores[0].date).format() + '">'
                    + moment.unix(scores[0].date).fromNow() + '</time>)</td></tr>'
                    + '<tr class="row1p">'
                    + '<td><strong>Score</strong></td><td>' + scores[0].score.toLocaleString() 
                    + ' (' + accuracy(scores[0].n300, scores[0].n100, scores[0].n50, scores[0].nmiss) + '%)</td>'
                    + '<td class="rank" width="120px" align="center" colspan="1" rowspan="7"><img src="//s.ppy.sh/images/'
                    + grade(scores[0].n300, scores[0].n100, scores[0].n50, scores[0].nmiss, mods(scores[0].mods))
                    + '.png" /></td>'
                    + '</tr>'
                    + '<tr class="row2p"><td><strong>Max Combo</strong></td><td>' + scores[0].combo + '</td></tr>'
                    + '<tr class="row1p"><td><strong>300 / 100 / 50</strong></td><td>'
                    + scores[0].n300 + ' / ' + scores[0].n100 + ' / ' + scores[0].n50 + '</td></tr>'
                    + '<tr class="row2p"><td><strong>Misses</strong></td><td>' + scores[0].nmiss + '</td></tr>'
                    + '<tr class="row1p"><td><strong>Geki (Elite Beat!)</strong></td><td>' + scores[0].ngeki + '</td></tr>'
                    + '<tr class="row2p"><td><strong>Katu (Beat!)</strong></td><td>' + scores[0].nkatu + '</td></tr>'
                    + '<tr class="row1p"><td><strong>Mods</strong></td><td>' + mods_string(mods(scores[0].mods)) + '</td></tr>'
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
                    + '<th><strong>Accuracy</strong></th>'
                    + '<th><strong>Player</strong></th>'
                    + '<th><strong>Max Combo</th>'
                    + '<th><strong>300 / 100 / 50</strong></th>'
                    + '<th><strong>Geki</strong></th>'
                    + '<th><strong>Katu</strong></th>'
                    + '<th><strong>Misses</strong></th>'
                    + '<th><strong>Mods</strong></th><th></th>'
                    + '</tr>';

                scores.forEach(function(score, index){
                    var mods_array = mods(score.mods);
                    insert_html += '<tr class="';
                    if(index % 2 == 0) insert_html += 'row2p'
                        else insert_html += 'row1p';
                    insert_html 
                    += '">'
                    + '<td><span>#' + (index + 1) + '</span></td>'
                    + '<td><img src="//s.ppy.sh/images/' 
                    + grade(score.n300, score.n100, score.n50, score.nmiss, mods_array) + '_small.png" /></td>'
                    + '<td><b>' + score.score.toLocaleString() + '</b></td>'
                    + '<td>' + accuracy(score.n300, score.n100, score.n50, score.nmiss) + '%</td>'
                    + '<td> <a href="/u/' + score.player_id + '">' + score.player + '</a></td>'
                    + '<td>' + score.combo + '</td>'
                    + '<td>' + score.n300 + '&nbsp&nbsp/&nbsp;&nbsp;' + score.n100 + '&nbsp;&nbsp;/&nbsp;&nbsp;' + score.n50 + '</td>'
                    + '<td>' + score.ngeki + '</td>'
                    + '<td>' + score.nkatu + '</td>'
                    + '<td>' + score.nmiss + '</td>'
                    + '<td>' + mods_string(mods_array) + '</td>'
                    + '<td></td>'
                    + '</tr>';
                });
                insert_html += '</table></div>';
                $(insert_html).insertAfter(".paddingboth");
                }
            }
        });

    }
})();
