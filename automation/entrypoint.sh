#!/bin/sh
set -e

# Start the daily expiry-sweep cron daemon in the background, then run the
# webhook receiver as the container's foreground (PID 1) process.
cron

exec gunicorn --bind 0.0.0.0:5000 --access-logfile - app.receiver:app
