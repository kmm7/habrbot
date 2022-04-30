FROM python:3-slim

WORKDIR /usr/src/app

RUN apt-get update

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY /src .

EXPOSE 8080:8080

CMD [ "python", "./server.py" ]