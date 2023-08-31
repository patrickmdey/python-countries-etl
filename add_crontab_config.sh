#!/bin/bash

# link: https://www.geeksforgeeks.org/python-script-that-is-executed-every-5-minutes/

# Runs the daily_email.py script every day at 8am
echo "0 8 * * * .env/bin/python3 daily_email.py" >>/tmp/temp_cron
crontab /tmp/temp_cron
rm /tmp/temp_cron
