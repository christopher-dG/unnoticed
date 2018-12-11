// ==UserScript==
// @name         [Unnoticed] Leaderboards
// @namespace    https://github.com/christopher-dG/unnoticed
// @version      1.2.2
// @description  Display unranked leaderboard entries gathered by [Unnoticed] on their respective beatmap pages
// @author       LazyLea
// @updateURL    https://github.com/christopher-dG/unnoticed/raw/master/contrib/userscript/unnoticed.user.js
// @match        https://osu.ppy.sh/*/*
// @include      https://p9bztcmks6.execute-api.us-east-1.amazonaws.com/*
// @grant        GM_xmlhttpRequest
// @require      https://code.jquery.com/jquery-3.2.1.min.js
// @require      https://momentjs.com/downloads/moment.min.js
// @require      https://cdnjs.cloudflare.com/ajax/libs/arrive/2.4.1/arrive.min.js
// @connect      p9bztcmks6.execute-api.us-east-1.amazonaws.com
// @run-at document-end
// ==/UserScript==

'use strict';

var mods_enum = {
    ''    : 0,
    'NF'  : 1,
    'EZ'  : 2,
    'TD'  : 4,
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
    'V2'  : 536870912,
};

var mods_name = {
  'NF': 'No Fail',
  'EZ': 'Easy',
  'TD': 'Touch Device',
  'HD': 'Hidden',
  'HR': 'Hard Rock',
  'SD': 'Sudden Death',
  'DT': 'Double Time',
  'RX': 'Relax',
  'HT': 'Half Time',
  'NC': 'Nightcore',
  'FL': 'Flashlight',
  'AT': 'Auto',
  'SO': 'Spun Out',
  'AP': 'Autopilot',
  'PF': 'Perfect',
  '4K': '4 Keys',
  '5K': '5 Keys',
  '6K': '6 Keys',
  '7K': '7 Keys',
  '8K': '8 Keys',
  'FI': 'Fade In',
  'RD': 'Random',
  'LM': 'Last Mod',
  '9K': '9 Keys',
  '10K': '10 Keys',
  '1K': '1 Key',
  '3K': '3 Keys',
  '2K': '2 Keys',
  'V2': 'Score V2'
}

var api_base = "https://p9bztcmks6.execute-api.us-east-1.amazonaws.com/unnoticed/proxy?b=";
var xhr;
var friends_array = [];
var tab = "all";

function mode_number(mode){
  switch(mode){
    case "osu":
      return 0;
    case "taiko":
      return 1;
    case "fruits":
      return 2;
    case "mania":
      return 3;
  }
}

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

function return_scores(beatmap_id, mode, outdated, cb){
  xhr = GM_xmlhttpRequest({
      method: "GET",
      url: api_base + beatmap_id,
      onload: function(response_raw){
          if(response_raw.status != 200){
              console.log(response_raw.responseText);
          }else{
              var response = JSON.parse(response_raw.responseText);
              var scores = [];
              var scores_mode = response.scores[beatmap_id].filter(function(a){ return a.mode == mode; });
              if(!outdated) scores_mode = scores_mode.filter(function(a){ return !a.outdated; });

              if(tab == "friend") scores_mode = scores_mode.filter(function(a){ return friends_array.includes(a.player_id); });
              if(tab == "country") scores_mode = scores_mode.filter(function(a){ return a.flag == currentUser.country.code; });

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

              scores.forEach(function(score, index){
                scores[index].place = index + 1;
                scores[index].accuracy = accuracy(mode, score.n300, score.n100, score.n50, score.nmiss, score.nkatu, score.ngeki);
                scores[index].mods_array = mods(score.mods);
                scores[index].grade = grade(mode, scores[index].mods_array, score.accuracy, score.n300, score.n100, score.n50, score.nmiss);
              });

              cb(scores);
          }
      }
  });
}

function old_leaderboard(){
  var mode = 0;
  if(window.location.href.split("&m=").length > 1)
      mode = parseInt(window.location.href.split("&m=").pop().split("&")[0]);

  var active_beatmap = $(".beatmapTab.active");
  var beatmap_id =
      active_beatmap.attr("href").split("/").pop().split("&")[0];

  var forced_mode =
      parseInt(active_beatmap.attr("href").split("&m=").pop());

  if(forced_mode != 0) mode = forced_mode;

  var showOutdated = window.location.hash == "#showOutdated"

  return_scores(beatmap_id, mode, showOutdated, function(scores){
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
          var pp = score.pp == null ? 'NA' : score.pp.toFixed(2);

          var outdated_style = score.outdated ? "opacity: 0.7;" : "";

          if(index == 0){
              insert_html
                  += '<div style="text-align: center; width: 100%;">'
                  + '<div style="display: inline-block; margin: 3px; text-align: left;">'
                  + '<table class="scoreLeader" style="margin-top: 10px;' + outdated_style + '" cellpadding="0" cellspacing="0">'
                  + '<tr><td class="title" colspan=3>'
                  + '<img class="flag" src="//s.ppy.sh/images/flags/' + score.flag.toLowerCase() + '.gif" />'
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
                  += '<tr class="row1p"><td><strong>Mods</strong></td><td>' + mods_string(score.mods_array) + '</td></tr>'
                  + '<tr class="row2p"><td><strong>pp</strong></td><td>' + score.pp.toFixed(2) + '</td></tr>'
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
              + '<td><img class="flag" src="//s.ppy.sh/images/flags/' + score.flag.toLowerCase() + '.gif" />'
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
              + '<td>' + mods_string(score.mods_array) + '</td>'
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
  });
}

function top_item(score, mode){
  var output =
    '<div class="beatmap-scoreboard-top__item">'
  + '<div class="beatmap-score-top">'
  + '<div class="beatmap-score-top__section">'
  + '<div class="beatmap-score-top__wrapping-container beatmap-score-top__wrapping-container--left">'
  + '<div class="beatmap-score-top__position">'
  + '<div class="beatmap-score-top__position-number">#' + score.place + '</div>'
  + '<div class="badge-rank badge-rank--tiny badge-rank--' + score.grade + '"></div>'
  + '</div>'
  + '<div class="beatmap-score-top__avatar">'
  + '<a href="/users/' + score.player_id + '" class="avatar" style="background-image: url(https://a.ppy.sh/' + score.player_id + ');"></a>'
  + '</div>'
  + '<div class="beatmap-score-top__user-box"><a class="beatmap-score-top__username js-usercard" data-user-id="' + score.player_id
  + '" href="/users/' + score.player_id + '">' + score.player + '</a>'
  + '<div class="beatmap-score-top__achieved">achieved '
  + '<time class="timeago" datetime="' + moment.unix(score.date).format() + '" title="' + moment.unix(score.date).format() + '">' + moment.unix(score.date).fromNow() + '</time>'
  + '</div><a href="/rankings/osu/performance?country=' + score.flag + '">'
  + '<span class="flag-country flag-country--scoreboard flag-country--small-box" title="' + score.flag
  + '" style="background-image: url(/images/flags/' + score.flag + '.png);"></span></a></div>'
  + '</div>'
  + '<div class="beatmap-score-top__wrapping-container beatmap-score-top__wrapping-container--right">'
  + '<div class="beatmap-score-top__stats">'
  + '<div class="beatmap-score-top__stat">'
  + '<div class="beatmap-score-top__stat-header beatmap-score-top__stat-header--wider">Total Score</div>'
  + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score">' + score.score.toLocaleString() + '</div>'
  + '</div>'
  + '</div>'
  + '<div class="beatmap-score-top__stats">'
  + '<div class="beatmap-score-top__stat">'
  + '<div class="beatmap-score-top__stat-header beatmap-score-top__stat-header--wider">Accuracy</div>'
  + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score">' + score.accuracy.toFixed(2) + '%</div>'
  + '</div>'
  + '<div class="beatmap-score-top__stat">'
  + '<div class="beatmap-score-top__stat-header beatmap-score-top__stat-header--wider">Max Combo</div>'
  + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score">' + score.combo + 'x</div>'
  + '</div>'
  + '</div>'
  + '<div class="beatmap-score-top__stats beatmap-score-top__stats--wrappable">';
  if(mode == 0){
    output +=
      '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">300</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n300 + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">100</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n100 + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">50</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n50 + '</div>'
    + '</div>';
  }else if(mode == 1){
    output +=
      '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">Great</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n300 + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">Good</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n100 + '</div>'
    + '</div>';
  }else if(mode == 2){
    output +=
      '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">Fruits</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n300 + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">Ticks</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n100 + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">Droplets</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n50 + '</div>'
    + '</div>';
  }else if(mode == 3){
    output +=
      '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">Max</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.ngeki + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">300</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n300 + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">200</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.nkatu + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">100</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n100 + '</div>'
    + '</div>'
    + '<div class="beatmap-score-top__stat">'
    + '<div class="beatmap-score-top__stat-header">50</div>'
    + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.n50 + '</div>'
    + '</div>';
  }
  output +=
    '<div class="beatmap-score-top__stat">'
  + '<div class="beatmap-score-top__stat-header">Miss</div>'
  + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + score.nmiss + '</div>'
  + '</div>'
  + '<div class="beatmap-score-top__stat">'
  + '<div class="beatmap-score-top__stat-header">pp</div>'
  + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">' + Math.round(score.pp) + '</div>'
  + '</div>'
  + '<div class="beatmap-score-top__stat">'
  + '<div class="beatmap-score-top__stat-header beatmap-score-top__stat-header--mods">Mods</div>'
  + '<div class="beatmap-score-top__stat-value beatmap-score-top__stat-value--score beatmap-score-top__stat-value--smaller">'
  + '<div class="mods mods--scoreboard">';
  score.mods_array.forEach(function(mod){
    output +=
      '<div class="mods__mod">'
    + '<div class="mods__mod-image">'
    + '<div class="mod mod--' + mod + '" title="' + mods_name[mod] + '"></div>'
    + '</div>'
    + '</div>'
  });
  output +=
    '</div>'
  + '</div>'
  + '</div>'
  + '</div>'
  + '</div>'
  + '</div>'
  + '</div>'
  + '</div>'
  return output;
}

function perfect_class(number){
  if(number == 100)
    return 'beatmap-scoreboard-table__perfect';
  else if(number === true)
    return 'beatmap-scoreboard-table__perfect';
  else
    return '';
}

function zero_class(number){
  if(number == 0)
    return 'beatmap-scoreboard-table__zero';
  else
    return '';
}

function new_leaderboard(){
    console.log("waiting for lb");
  $(document).arrive(".beatmapset-status--show", {existing: true}, function(){
      console.log("loading lb");
    if($(".beatmapset-status--show").text() == "graveyard"
    || $(".beatmapset-status--show").text() == "wip"
    || $(".beatmapset-status--show").text() == "pending"){
      $(".osu-layout__section.osu-layout__section--extra").prepend('<p class="beatmapset-scoreboard__notice beatmapset-scoreboard__notice--no-scores osu-page osu-page--generic">Loading scores...</p>');
      var id_mode = window.location.hash.split("/");
      var mode = mode_number(id_mode[0].substr(1))
      var beatmap_id = id_mode[1];
      console.log("retrieving scores for", beatmap_id, mode);
      return_scores(beatmap_id, mode, false, function(scores){
        if(scores.length > 0){
          var insert_html =
            '<div class="osu-page osu-page--generic">'
          + '<div class="beatmapset-scoreboard">'
          + '<div class="page-tabs">'
          + '<div class="page-tabs__tab ' + (tab == "all" ? "page-tabs__tab--active" : "") + '">Global Ranking</div>'
          + '<div class="page-tabs__tab ' + (tab == "country" ? "page-tabs__tab--active" : "") + '">Country Ranking</div>'
          + '<div class="page-tabs__tab ' + (tab == "friend" ? "page-tabs__tab--active" : "") + '">Friend Ranking</div>'
          + '</div>'
          + '<div class="beatmapset-scoreboard__main">'
          + '<div>'
          + '<div class="beatmap-scoreboard-top">';
          insert_html += top_item(scores[0], mode);
          var own_score = false;
          scores.forEach(function(score, index){
            if(score.player_id == currentUser.id)
              own_score = score;
          });
          if(own_score && own_score.place != 1) insert_html += top_item(own_score, mode);
          insert_html +=
            '</div>'
          + '<div class="beatmap-scoreboard-table">'
          + '<table class="beatmap-scoreboard-table__table">'
          + '<thead>'
          + '<tr>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--rank">Rank</th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--grade"></th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--score">Score</th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--accuracy">Accuracy</th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--flag"></th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--player">Player</th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--maxcombo">Max Combo</th>';
          if(mode == 0){
            insert_html +=
              '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">300</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">100</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">50</th>';
          }else if(mode == 1){
            insert_html +=
              '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">Great</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">Good</th>'
          }else if(mode == 2){
            insert_html +=
              '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">Fruits</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">Ticks</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">Droplets</th>';
          }else if(mode == 3){
            insert_html +=
              '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">Max</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">300</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">200</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">100</th>'
            + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--hitstat">50</th>';
          }
          insert_html +=
            '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--miss">Miss</th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--pp">pp</th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--mods">Mods</th>'
          + '<th class="beatmap-scoreboard-table__header beatmap-scoreboard-table__header--play-detail-menu"></th>'
          + '</tr>'
          + '</thead>'
          + '<tbody class="beatmap-scoreboard-table__body">';

          scores.forEach(function(score, index){
            insert_html +=
              '<tr class="beatmap-scoreboard-table__body-row beatmap-scoreboard-table__body-row--highlightable beatmap-scoreboard-table__body-row--first ';
            if(score.player_id == currentUser.id) insert_html += 'beatmap-scoreboard-table__body-row--self';
            if(friends_array.includes(score.player_id)) insert_html += 'beatmap-scoreboard-table__body-row--friend';

            insert_html +=
              '">'
            + '<td class="beatmap-scoreboard-table__cell beatmap-scoreboard-table__rank">#' + (index + 1) + '</td>'
            + '<td class="beatmap-scoreboard-table__cell beatmap-scoreboard-table__grade">'
            + '<div class="badge-rank badge-rank--tiny badge-rank--' + score.grade + '"></div>'
            + '</td>'
            + '<td class="beatmap-scoreboard-table__cell beatmap-scoreboard-table__score">' + score.score.toLocaleString() + '</td>'
            + '<td class="beatmap-scoreboard-table__cell ' + perfect_class(score.accuracy) + '">' + score.accuracy.toFixed(2) + '%</td>'
            + '<td class="beatmap-scoreboard-table__cell"><a href="/rankings/osu/performance?country=' + score.flag + '"><span class="flag-country flag-country--scoreboard flag-country--small-box" title="'
            + score.flag + '" style="background-image: url(/images/flags/' + score.flag + '.png);"></span></a></td>'
            + '<td class="beatmap-scoreboard-table__cell"><a class="beatmap-scoreboard-table__user-link js-usercard" data-user-id="' + score.player_id + '" href="/users/' + score.player_id + '">' + score.player + '</a></td>'
            + '<td class="beatmap-scoreboard-table__cell ' + perfect_class(score.fc) + '">' + score.combo + '</td>';

            if(mode == 0 || mode == 2){
              insert_html +=
                '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.n300) + '">' + score.n300 + '</td>'
              + '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.n100) + '">' + score.n100 + '</td>'
              + '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.n50) + '">' + score.n50 + '</td>'
            }else if(mode == 1){
              insert_html +=
                '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.n300) + '">' + score.n300 + '</td>'
              + '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.n100) + '">' + score.n100 + '</td>'
            }else if(mode == 3){
              insert_html +=
                '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.ngeki) + '">' + score.ngeki + '</td>'
              + '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.n300) + '">' + score.n300 + '</td>'
              + '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.nkatu) + '">' + score.nkatu + '</td>'
              + '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.n100) + '">' + score.n100 + '</td>'
              + '<td class="beatmap-scoreboard-table__cell ' + zero_class(score.n50) + '">' + score.n50 + '</td>';
            }

            insert_html +=
              '<td class="beatmap-scoreboard-table__cell' + zero_class(score.nmiss) + '">' + score.nmiss + '</td>'
            + '<td class="beatmap-scoreboard-table__cell">' + Math.round(score.pp) + '</td>'
            + '<td class="beatmap-scoreboard-table__cell beatmap-scoreboard-table__mods">'
            + '<div class="mods mods--scoreboard">';
            score.mods_array.forEach(function(mod){
              insert_html +=
                '<div class="mods__mod">'
              + '<div class="mods__mod-image">'
              + '<div class="mod mod--' + mod + '" title="' + mods_name[mod] + '"></div>'
              + '</div>'
              + '</div>'
            });
            insert_html +=
              '</div>'
            + '</td>'
            + '<td class="beatmap-scoreboard-table__play-detail-menu"></td>'
            + '</tr>';
          });
          insert_html +=
            '</tbody>'
          + '</table>'

          insert_html +=
            '</div>';
          $(".osu-layout__section.osu-layout__section--extra .osu-page.osu-page--generic").remove();
          $(".osu-layout__section.osu-layout__section--extra").prepend(insert_html);
          $(".beatmapset-scoreboard__notice--no-scores").remove();
        }else{
            $(".beatmapset-scoreboard__notice--no-scores").remove();
          $(".osu-layout__section.osu-layout__section--extra").prepend('<p class="beatmapset-scoreboard__notice beatmapset-scoreboard__notice--no-scores osu-page osu-page--generic">No scores yet. Maybe you should try setting some?</p>');
        }
      });
    }
  });
}

function page_change(){
  if(xhr) xhr.abort();
  console.log("[Unnoticed] page change", window.location.pathname);
  if(window.location.pathname.startsWith("/s/") || window.location.pathname.startsWith("/b/")
  || window.location.pathname.startsWith("/p/beatmap")){
    if($(".beatmapTab").length > 0 && $("h2:contains(Top 50 Scoreboard)").length === 0)
      old_leaderboard();
  }else if(window.location.pathname.startsWith("/beatmapsets/")){
    new_leaderboard();
  }
}

var pushState = history.pushState;
history.pushState = function(){
    pushState.apply(history, arguments);
    page_change();
};

var replaceState = history.replaceState;
history.replaceState = function(){
    replaceState.apply(history, arguments);
    page_change();
};

window.addEventListener("popstate", page_change, false);
window.addEventListener("hashchange", page_change, false);

(function(){
  page_change();
  if(typeof currentUser !== 'undefined'){
    currentUser.friends.forEach(function(friend){
      friends_array.push(friend.target_id);
    });
    $("body").on("click", ".beatmapset-scoreboard .page-tabs .page-tabs__tab", function(){
      switch($(this).text()){
        case "Country Ranking":
          tab = "country";
          break;
        case "Friend Ranking":
          tab = "friend";
          break;
        default:
          tab = "all";
      }
      new_leaderboard();
    });
  }
})();
