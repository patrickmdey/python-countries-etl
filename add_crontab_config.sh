#!/bin/bash

# link: https://www.geeksforgeeks.org/python-script-that-is-executed-every-5-minutes/

# Runs the daily_email.py script every day at 8am
# to remove the cron job, run crontab -r

path=$(pwd)
echo "0 8 * * * $path/.venv/bin/python3 $path/daily_email.py $path" >>/tmp/temp_cron
crontab /tmp/temp_cron
rm /tmp/temp_cron
