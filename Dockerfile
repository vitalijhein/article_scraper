FROM python:3

# Update packages and install cron
RUN apt-get update && apt-get -y install cron

WORKDIR /usr/src/app

COPY requirements.txt ./

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files to container working directory
COPY . .
# Copy cron job configuration for crawler
COPY crawler-cron /etc/cron.d/crawler-cron

# Give execution rights to crontab and python script
RUN chmod 0744 /etc/cron.d/crawler-cron
RUN chmod 0744 ./entrypoint.sh
RUN chmod 0744 ./__main__.py

# Apply crontab
RUN crontab /etc/cron.d/crawler-cron

# Run cron in the foreground
ENTRYPOINT [ "./entrypoint.sh" ]