FROM python:alpine3.15

WORKDIR /usr/src/app

#Install Cron
RUN apk add --update cron

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY /src .

ADD ingest.sh /usr/src/app/ingest.sh

# Give execution rights on the cron scripts
RUN chmod 0644 /usr/src/app/ingest.sh

# Add the cron job
RUN crontab -l | { cat; echo "35 1 * * * bash /usr/src/app/ingest.sh"; } | crontab -

EXPOSE 8080:8080

CMD [ "python", "./server.py" ]