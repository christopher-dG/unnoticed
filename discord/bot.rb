#!/usr/bin/env ruby

require 'discordrb'
require 'httparty'
require 'terminal-table'

OLD_SAMPLE = 'https://osu.ppy.sh/b/123'
NEW_SAMPLE = 'https://osu.ppy.sh/beatmapsets/123#osu/123'
OLD_REGEX = /osu.ppy.sh\/b\/([0-9]+)/
NEW_REGEX = /osu.ppy.sh\/beatmapsets\/[0-9]+\/?#[a-z]+\/([0-9]+)/
UNNOTICED_API = "https://p9bztcmks6.execute-api.us-east-1.amazonaws.com/unnoticed/proxy"
OSU_API = "https://osu.ppy.sh/api/get_beatmaps"
MODS = [  # Reference: https://github.com/ppy/osu-api/wiki#mods
  # Mods are intentionally out of order; they're in the order in which they're displayed.
  ['EZ', 1 << 1], ['HD', 1 << 3], ['HT', 1 << 8], ['DT', 1 << 6], ['NC', 1 << 9],
  ['HR', 1 << 4], ['FL', 1 << 10], ['NF', 1 << 0], ['SD', 1 << 5], ['PF', 1 << 14],
  ['RX', 1 << 7], ['AP', 1 << 13], ['SO', 1 << 12], ['AT', 1 << 11], ['V2', 1 << 29],
  ['1K', 1 << 26], ['2K', 1 << 28], ['3K', 1 << 27], ['4K', 1 << 15], ['5K', 1 << 16],
  ['6K', 1 << 17], ['7K', 1 << 18], ['8K', 1 << 19], ['9K', 1 << 24], ['TK', 1 << 25],
  ['FI', 1 << 20], ['RN', 1 << 21],
]

# Reply to a message containing a beatmap link with a leaderboard table.
def process_map(msg)
  if OLD_REGEX.match?(msg)
    map_id = Integer(OLD_REGEX.match(msg).captures[0])
  elsif NEW_REGEX.match?(msg)
    map_id = Integer(NEW_REGEX.match(msg).captures[0])
  else
    puts("'#{msg}' does not match any regex")
    return nil
  end

  map_dict = map_info(map_id)
  header = map_dict.key?(:string) ? map_dict[:string] : ''
  header += " - https://osu.ppy.sh/b/#{map_id}" if should_add_url(msg)

  begin
    resp = HTTParty.get("#{UNNOTICED_API}?b=#{map_id}")
  rescue => e
    puts("API request failed: #{e}")
    return nil
  end
  unless resp.code == 200
    puts("API response returned #{resp.code}")
    puts(resp.parsed_response)
    return nil
  end
  resp = resp.parsed_response
  puts("API response returned info: #{info}") unless resp['info'].empty?

  scores = resp['scores'][map_id.to_s].sort_by {|s| s['score']}
           .reverse.uniq {|s| s['player_id']}
  scores.select! {|s| s['mode'] == map_dict[:mode]} unless map_dict[:mode].nil?

  if scores.empty?
    table = 'No scores'
  else
    columns = ['#', 'Player', 'Score', 'pp', 'Mods', 'Acc', 'Combo', 'Misses']
    table = Terminal::Table.new(:headings => columns, :style => {:alignment => :right})
    warning = nil

    scores[0...25].each_with_index do |s, i|
      if s['outdated']
        warning = ' * This play was made on an outdated/edited version of the map'
        idx = "#{i + 1}*"
      else
        idx = i + 1
      end

      table.add_row(
        [
          idx,
          s['player'],
          s['score'],
          s['pp'].nil? ? 'NA' : s['pp'].round,
          mods(s['mods']),
          "#{accuracy(s)}%",
          "#{s['combo']}x",
          s['nmiss'],
        ]
      )
    end
    # Left-align non-numeric columns.
    [1, 4].each {|i| table.align_column(i, :left)}
  end

  return "#{header}\n```#{table}\n#{warning}```"
end

# Determine whether we should add the beatmap url to the reply
# (owo bot doesn't use regexes and misses some patterns).
def should_add_url(msg) not (OLD_REGEX.match?(msg) and msg.include?('https://osu')) end

# Convert an integer into a mod string.
def mods(n)
  return 'None' if n == 0
  mods = MODS.select{|m| n & m[1] > 0}.map {|m| m[0]}
  mods.delete('DT') if mods.include?('NC')
  mods.delete('SD') if mods.include?('PF')
  return mods.empty? ? 'None' : "+#{mods.join}"
end

# Return a string with the map name and the game mode.
def map_info(map_id)
  url = "#{OSU_API}?k=#{ENV['OSU_API_KEY']}&b=#{map_id}"
  begin
    d = HTTParty.get(url).parsed_response[0]
  rescue => e
    puts("Fetching map #{map_id} failed: #{e}")
    return {}
  end
  s = "**#{d['artist']} - #{d['title']} [#{d['version']}]** by **#{d['creator']}**"
  return {:string => s, :mode => Integer(d['mode'])}
end

# Calculate accuracy for a given score (https://osu.ppy.sh/help/wiki/Accuracy).
def accuracy(s)
  if s['mode'] == 0  # Standard.
    acc = (s['n300'] + s['n100']/3.0 + s['n50']/6.0) /
          (s['n300'] + s['n100'] + s['n50'] + s['nmiss'])
  elsif s['mode'] == 1  # Taiko.
    acc = (s['n300'] + s['n100']/2.0) /
          (s['n300'] + s['n100'] + s['nmiss'])
  elsif s['mode'] == 2  # CTB.
    acc = (s['n300'] + s['n100'] + s['n50']) /
          (s['n300'] + s['n100'] + s['n50'] + s['nkatu'] + s['nmiss'])
  elsif s['mode'] == 3  # Mania.
    acc = (s['ngeki'] + s['n300'] + 2*s['nkatu']/3.0 + s['n100']/3.0 + s['n50']/6.0) /
          (s['ngeki'] + s['n300'] + s['nkatu'] + s['n100'] + s['n50'] + s['nmiss'])
  else
    puts("Invalid mode for score #{s['id']}: #{s['mode']}")
    acc = 0
  end
  return (acc * 100).round(2)
end

BOT = Discordrb::Bot.new(
  token: ENV['DISCORD_TOKEN'],
  client_id: ENV['DISCORD_CLIENT_ID'],
)

# Old website URL.
BOT.message(contains: OLD_REGEX) do |event|
  response = process_map(event.text)
  event.respond(response) unless response.nil?
end

# New website URL.
BOT.message(contains: NEW_REGEX) do |event|
  response = process_map(event.text)
  event.respond(response) unless response.nil?
end

# Old website beatmapset URL.
BOT.message(contains: /osu.ppy.sh\/s\/[0-9]+/) do |event|
  event.respond("That's a beatmapset URL, it should look more like this: `#{OLD_SAMPLE}`")
end

# New website beatmapset URL.
BOT.message(contains: /osu.ppy.sh\/beatmapsets\/[0-9]+(#[a-z]*)?\/?\z/) do |event|
  event.respond("That's a beatmapset URL, it should look more like this: `#{NEW_SAMPLE}`")
end

BOT.run
