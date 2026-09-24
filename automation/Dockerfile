FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY cron/crontab /etc/cron.d/media-automation
RUN chmod 0644 /etc/cron.d/media-automation \
    && crontab /etc/cron.d/media-automation

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
