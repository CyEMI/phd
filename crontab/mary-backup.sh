#!/usr/bin/env bash
#
# Backup mary server.
#
# ****************************************************************************
# *                               Configuration                              *
# ****************************************************************************
JOB_TIMEOUT=21600  # 6 hrs
LMK="/usr/local/bin/lmk"
LMK_TO="chrisc.101@gmail.com"

CRONTAB_BACKUP=~/.local/etc/crontab.txt  # crontab is exported to here
RM_DSSTORE=~/.local/bin/rm-dsstore
EMU="/usr/local/bin/emu"


# ****************************************************************************
# *                                  Program                                 *
# ****************************************************************************
set -eux

if [[ -z "${1:-}" ]]; then
    $LMK "timeout $JOB_TIMEOUT $0 --porcelain"
else
    df -h

    # backup crontab
    mkdir -pv ~/.local/etc
    crontab -l > $CRONTAB_BACKUP

    $RM_DSSTORE ~

    cd /
    sudo -E $EMU push -v -f
fi
