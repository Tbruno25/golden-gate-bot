FROM python:3-slim

RUN apt-get update && apt-get upgrade

# Set up cron job
RUN apt-get -y install cron vim
RUN touch /var/log/cron.log
RUN echo "*/30 * * * * root /usr/local/bin/python3 /bot/app.py" >> /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab

# Install dependencies
COPY . /bot/
RUN pip3 install -r /bot/requirements.txt

CMD ["cron", "-f"]