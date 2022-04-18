FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY /src .

ADD ingest.sh /usr/src/app/ingest.sh

# Give execution rights on the cron scripts
RUN chmod 0644 /usr/src/app/ingest.sh

#Install Cron
RUN apt-get update
RUN apt-get -y install cron

# Add the cron job
RUN crontab -l | { cat; echo "0 0 1 * * ? bash /usr/src/app/ingest.sh"; } | crontab -

CMD [ "python", "./server.py" ]