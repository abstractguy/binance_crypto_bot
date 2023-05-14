#!/usr/bin/env bash

# File:        install/repair_boot.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       sudo -H bash install/repair_boot.sh
# Description: Install unetbootin to flash Linux on a USB key.

add-apt-repository ppa:yannubuntu/boot-repair
apt-get update
apt-get install -y boot-repair
boot-repair &

