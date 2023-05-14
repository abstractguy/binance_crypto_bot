#!/usr/bin/env bash

# File:        install/install_unetbootin.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       sudo -H bash install/install_unetbootin.sh
# Description: Install unetbootin to flash Linux on a USB key.

add-apt-repository ppa:gezakovacs/ppa
apt-get update
apt-get install -y unetbootin
unetbootin &

