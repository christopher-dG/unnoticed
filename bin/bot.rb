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
  end
  # TODO: This gets all scores for the map rather than just the top 50.
  # Figure out a way to get around the weird distinct constraint.
  ds = DB[:scores].where(:map => map_id).distinct(:player)
  scores = ds.sort_by{|s| s[:score]}.reverse[0...50]
  map_line = map_string(map_id)
  table = Terminal::Table.new(:headings => ['Player', 'Score', 'Combo'])

  scores.each do |score|
    table.add_row([score[:player], score[:score], "#{score[:combo]}x"])
  end

  return "#{map_line}\n```\n#{table}\n```"
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
