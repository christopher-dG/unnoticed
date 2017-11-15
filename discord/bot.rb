#!/usr/bin/env ruby

require 'discordrb'
require 'httparty'
require 'sequel'
require 'terminal-table'

OLD_SAMPLE = 'https://osu.ppy.sh/b/123'
NEW_SAMPLE = 'https://osu.ppy.sh/beatmapsets/123#osu/123'
OLD_REGEX = /osu.ppy.sh\/b\/([0-9]+)/
NEW_REGEX = /osu.ppy.sh\/beatmapsets\/[0-9]+#[a-z]+\/([0-9]+)/

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

  # TODO: This gets all scores for the map rather than just the top 25.
  # Figure out a way to get around the weird distinct constraint.
  if map_dict[:mode].nil?
    ds = DB[:scores].where(:map => map_id).distinct(:player)
  else
    ds = DB[:scores].where(:map => map_id, :mode => map_dict[:mode]).distinct(:player)
  end
  scores = ds.sort_by{|s| s[:score]}.reverse[0...25]

  if scores.empty?
    table = 'No scores'
  else
    table = Terminal::Table.new(
      :headings => ['#', 'Player', 'Score', 'Mods', 'Acc', 'Combo', 'Misses', 'Date'],
    )
    missing = map_dict[:md5].nil?
    outdated = false
    scores.each_with_index do |s, i|
      next if map_dict[:mode] != s[:mode]  # TODO: Let users specify the game mode.
      # If the map hashes don't match up, then the map has been updated
      # since the play was made and therefore the score is not reliable.
      if not missing and s[:mhash] != map_dict[:md5]
        outdated = true
        idx = "#{i + 1}*"
      else
        idx = i + 1
      end

      table.add_row(
        [
          idx,
          s[:player],
          s[:score],
          mods(s[:mods]),
          "#{accuracy(s)}%",
          "#{s[:combo]}x",
          s[:nmiss],
          Time.at(s[:date]).to_date,
        ]
      )
    end
  end

  if missing
    warning = ' * The most recent version of the map could not be found; '
    warning += 'any of these scores could be outdated/edited'
  elsif outdated
    warning = ' * This play was made on an outdated/edited version of the map'
  else
    warning = nil
  end

  return "#{header}\n```#{table}\n#{warning}```"
end

def should_add_url(msg) not (OLD_REGEX.match?(msg) and msg.include?('https://osu')) end

def mods(n)
  return 'None' if n == 0
  mods = {
    1 << 0  => :NF,   # 1         - NoFail
    1 << 1  => :EZ,   # 2         - Easy
    1 << 2  => :NV,   # 4         - No Video, deprecated and unused for like 4 years
    1 << 3  => :HD,   # 8         - Hidden
    1 << 4  => :HR,   # 16        - HardRock
    1 << 5  => :SD,   # 32        - SuddenDeath
    1 << 6  => :DT,   # 64        - DoubleTime
    1 << 7  => :RX,   # 128       - Relax
    1 << 8  => :HT,   # 256       - HalfTime
    1 << 9  => :NC,   # 512       - Nightcore
    1 << 10 => :FL,   # 1024      - Flashlight
    1 << 11 => :AT,   # 2048      - Autoplay
    1 << 12 => :SO,   # 4096      - SpunOut
    1 << 13 => :AP,   # 8192      - AutoPilot, "Relax2"
    1 << 14 => :PF,   # 16384     - Perfect
    1 << 29 => :V2,   # 536870912 - ScoreV2
  }

  order = [:EZ, :HD, :HT, :DT, :NC, :HR, :FL, :NF, :SD, :PF, :RL, :SO, :AP, :AT, :V2]
  enabled = []
  mods.keys.reverse.each do |mod|
    if mod <= n
      enabled.push(mods[mod])
      n -= mod
      break if n <= 0
    end
  end
  return "+#{order.select {|m| enabled.include?(m)}.join}"
end

# Return a string with the map name, the game mode, and the map file's MD5.
def map_info(map_id)
  url = "https://osu.ppy.sh/api/get_beatmaps?k=#{ENV['OSU_API_KEY']}&b=#{map_id}"
  begin
    d = HTTParty.get(url).parsed_response[0]
  rescue => e
    puts("Fetching map #{map_id} failed: #{e}")
    return {}
  end
  s = "**#{d['artist']} - #{d['title']} [#{d['version']}]** by **#{d['creator']}**"
  return {:string => s, :md5 => d['file_md5'], :mode => Integer(d['mode'])}
end

# https://osu.ppy.sh/help/wiki/Accuracy/
def accuracy(s)
  if s[:mode] == 0  # Standard.
    acc = (s[:n300] + s[:n100]/3.0 + s[:n50]/6.0) /
          (s[:n300] + s[:n100] + s[:n50] + s[:nmiss])
  elsif s[:mode] == 1  # Taiko.
    acc = (s[:n300] + s[:n100]/2.0) /
          (s[:n300] + s[:n100] + s[:nmiss])
  elsif s[:mode] == 2  # CTB.
    acc = (s[:n300] + s[:n100] + s[:n50]) /
          (s[:n300] + s[:n100] + s[:n50] + s[:nkatu] + s[:nmiss])
  elsif s[:mode] == 3  # Mania.
    acc = (s[:ngeki] + s[:n300] + 2*s[:nkatu]/3.0 + s[:n100]/3.0 + s[:n50]/6.0) /
          (s[:ngeki] + s[:n300] + s[:nkatu] + s[:n100] + s[:n50] + s[:nmiss])
  else
    puts("Invalid mode for score #{s[:id]}: #{s[:mode]}")
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
  event.respond(response) if not response.nil?
end

# New website URL.
BOT.message(contains: NEW_REGEX) do |event|
  response = process_map(event.text)
  event.respond(response) if not response.nil?
end

# Old website beatmapset URL.
BOT.message(contains: /osu.ppy.sh\/s\/[0-9]+/) do |event|
  event.respond("That's a beatmapset URL, it should look more like this: `#{OLD_SAMPLE}`")
end

# New website beatmapset URL.
BOT.message(contains: /osu.ppy.sh\/beatmapsets\/[0-9]+(#[a-z]*)?\/?\z/) do |event|
  event.respond("That's a beatmapset URL, it should look more like this: `#{NEW_SAMPLE}`")
end

DB = Sequel.connect("postgres://#{ENV['DB_USER']}:#{ENV['DB_PASSWORD']}@#{ENV['DB_HOST']}/#{ENV['DB_NAME']}")
BOT.run