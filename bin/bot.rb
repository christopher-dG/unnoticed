require 'discordrb'
# require 'pg'

OLD_SAMPLE = 'https://osu.ppy.sh/b/123'
NEW_SAMPLE = 'https://osu.ppy.sh/beatmapsets/123#osu/123'

def process_map(msg)
  return 'test'
end

bot = Discordrb::Bot.new(
  token: ENV['DISCORD_TOKEN'],
  client_id: ENV['DISCORD_CLIENT_ID'],
)

# Old website URL.
bot.message(contains: /osu.ppy.sh\/b\/[0-9]+/) do |event|
  response = process_map(event.text)
  event.respond(response) if not response.nil?
end

# New website URL.
bot.message(contains: /osu.ppy.sh\/beatmapsets\/[0-9]+#[a-z]+\/[0-9]+/) do |event|
  response = process_map(event.text)
  event.respond(response) if not response.nil?
end

# Old website beatmapset URL.
bot.message(contains: /osu.ppy.sh\/s\/[0-9]+/) do |event|
  event.respond("That's a beatmapset URL, it should look more like this: `#{OLD_SAMPLE}`")
end

# New website beatmapset URL.
bot.message(contains: /osu.ppy.sh\/beatmapsets\/[0-9]+(#[a-z]*)?\/?\z/) do |event|
  event.respond("That's a beatmapset URL, it should look more like this: `#{NEW_SAMPLE}`")
end

bot.run
