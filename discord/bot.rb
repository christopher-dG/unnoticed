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

  map_line = map_string(map_id)
  header = map_line.nil? ? '' : map_line
  header += " - https://osu.ppy.sh/b/#{map_id}" if should_add_url(msg)

  # TODO: This gets all scores for the map rather than just the top 25.
  # Figure out a way to get around the weird distinct constraint.
  ds = DB[:scores].where(:map => map_id).distinct(:player)
  scores = ds.sort_by{|s| s[:score]}.reverse[0...25]

  if scores.empty?
    table = 'No scores'
  else
    table = Terminal::Table.new(
      :headings => ['#', 'Player', 'Score', 'Mods', 'Acc', 'Combo', 'Misses', 'Date'],
    )
    scores.each_with_index do |s, i|
      table.add_row(
        [
          i+1,
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

  return "#{header}\n```#{table}```"
end

def should_add_url(msg) not (OLD_REGEX.match?(msg) and msg.include?('https://osu')) end

def mods(n)
  return 'None' if n == 0
  mods = {
    1 => 'NF', 2 => 'EZ', 4 => '', 8 => 'HD', 16 => 'HR', 32 => 'SD', 64 => 'DT',
    128 => 'RL', 256 => 'HT', 64 | 512 => 'NC', 1024 => 'FL', 2048 => 'AT',
    4096 => 'SO', 8192 => 'AP', 32 | 16384 => 'PF',
  }
  order = ['EZ', 'HD', 'HT', 'DT', 'NC', 'HR', 'FL', 'NF', 'SD', 'PF', 'RL', 'SO', 'AP', 'AT']
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

def map_string(map_id)
  url = "https://osu.ppy.sh/api/get_beatmaps?k=#{ENV['OSU_API_KEY']}&b=#{map_id}"
  begin
    d = HTTParty.get(url).parsed_response[0]
  rescue => e
    puts("Fetching map #{map_id} failed: #{e}")
    return nil
  end
  return "**#{d['artist']} - #{d['title']} [#{d['version']}]** by **#{d['creator']}**"
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
