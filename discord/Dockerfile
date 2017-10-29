FROM ruby:2.4.2
RUN gem install discordrb httparty pg sequel terminal-table
COPY . /root/app
ENTRYPOINT ["/root/app/entrypoint.sh"]
