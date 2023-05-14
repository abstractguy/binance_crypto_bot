#!/usr/bin/env bash

# File:        install/uninstall_micromamba.sh
# By:          Samuel Duclos
# For:         Myself
# Description: Uninstall micromamba if needed.
# Usage:       bash install/uninstall_micromamba.sh <PASSWORD>
# Example 1:   bash install/uninstall_micromamba.sh password123
# Example 2:   bash install/uninstall_micromamba.sh
# Arguments:   <PASSWORD>: optional sudo password    (default is "")

# Parse and set optional password argument from command-line.
PASSWORD=$(echo "${1:-}")

# Take password from command-line if set, else ask live.
if [[ "$(echo ${PASSWORD})" == "" ]]
then
    read -s -p "Enter your password: " PASSWORD
fi

# Automagic.
if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" != "base" ]]
then
    /opt/micromamba/bin/micromamba deactivate
fi
/opt/micromamba/bin/micromamba clean --yes --all --force-pkgs-dirs && \
/opt/micromamba/bin/micromamba install --yes anaconda-clean && \
$( which anaconda-clean ) --yes
/opt/micromamba/bin/micromamba shell deinit --shell bash --prefix /opt/micromamba && \
echo $PASSWORD | sudo -S rm -rf /opt/micromamba && \
echo "micromamba is uninstalled!"
