FROM ruby:2.4.2
RUN gem install discordrb httparty terminal-table
COPY . /root/app
ENTRYPOINT ["/root/app/entrypoint.sh"]
