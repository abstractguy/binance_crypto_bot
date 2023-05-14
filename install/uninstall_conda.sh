#!/usr/bin/env bash

# File:        install/uninstall_conda.sh
# By:          Samuel Duclos
# For:         Myself
# Description: Uninstall conda if needed.
# Usage:       bash install/uninstall_conda.sh <PASSWORD>
# Example 1:   bash install/uninstall_conda.sh password123
# Example 2:   bash install/uninstall_conda.sh
# Arguments:   <PASSWORD>: optional sudo password    (default is "")

# Parse and set optional password argument from command-line.
PASSWORD=$(echo "${1:-}")

# Take password from command-line if set, else ask live.
if [[ "$(echo ${PASSWORD})" == "" ]]
then
    read -s -p "Enter your password: " PASSWORD
fi

# Automagic.
if [[ "$(which conda)" != "" ]]
then
    if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" != "base" ]]
    then
        /opt/conda/bin/conda deactivate
    fi
    /opt/conda/bin/conda clean --yes --all --force-pkgs-dirs && \
    /opt/conda/bin/conda install --yes anaconda-clean && \
    $( which anaconda-clean ) --yes && \
    echo $PASSWORD | sudo -S rm -rf /opt/conda && \
    echo "Don't forget to manually remove anaconda3 PATH in ~/.bash_profile and ~/.bashrc!"
fi
