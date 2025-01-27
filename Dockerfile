FROM python:3.10.8-slim-buster
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg

COPY . .

CMD gunicorn app:app & python3 bot.py
