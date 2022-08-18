#!/bin/bash
# Load env variables for cron processes to use
printenv | grep -v "no_proxy" >> /etc/environment
# Run cron process in the foreground
cron -f