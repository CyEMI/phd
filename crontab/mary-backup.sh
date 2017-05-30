#!/usr/bin/env bash
#
# Backup mary server.
#
set -eu

# maximum runtime in seconds
JOB_TIMEOUT=21600  # 6 hrs

df -h

# backup crontab
mkdir -pv ~/.local/etc
echo "crontab -l > ~/.local/etc/crontab.txt"
crontab -l > ~/.local/etc/crontab.txt

cd /
echo "emu-push -v"
set +e
sudo timeout $JOB_TIMEOUT emu-push -v -f
ret=$?
test $ret != 124 || { echo "timeout after $JOB_TIMEOUT seconds"; exit $ret; }
test $ret = 0 || exit $ret
