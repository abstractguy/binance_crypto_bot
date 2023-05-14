#!/usr/bin/env bash

# File:          install/install_micromamba.sh
# By:            Samuel Duclos
# For            Myself
# Description:   Install micromamba.
# Usage:         bash install/install_micromamba.sh <PASSWORD>
# Example 1:     bash install/install_micromamba.sh password123
# Example 2:     bash install/install_micromamba.sh
# Arguments:     <PASSWORD>: optional sudo password    (default is "")

# Parse and set optional password argument from command-line.
PASSWORD=$(echo "${1:-}")

# Take password from command-line if set, else ask live.
if [[ "$(echo ${PASSWORD})" == "" ]]
then
    read -s -p "Enter your password: " PASSWORD
fi

# Parse and select architecture.
ARCH=$(uname -m)
OS=$(uname)

if [[ "$OS" == "Linux" ]]
then
    PLATFORM="linux"
    if [[ "$ARCH" == "aarch64" ]]
    then
        ARCH="aarch64"
    elif [[ $ARCH == "ppc64le" ]]
    then
        ARCH="ppc64le"
    else
        ARCH="64"
    fi		
fi

if [[ "$OS" == "Darwin" ]]
then
    PLATFORM="osx"
    if [[ "$ARCH" == "arm64" ]]
    then
        ARCH="arm64"
    else
        ARCH="64"
    fi
fi

# Automagic.
echo ${PASSWORD} | sudo -S apt-get update && \
echo ${PASSWORD} | sudo -S apt-get install -y avrdude curl bzip2 ca-certificates git libglib2.0-0 libxext6 libsm6 libxrender1 mercurial subversion wget && \
echo ${PASSWORD} | sudo -S apt clean && \
echo ${PASSWORD} | sudo -S mkdir -p /opt/micromamba/bin && \
WHOAMI=$(env | grep "USER=" | sed 's/USER=//') && \
echo ${PASSWORD} | sudo -S chown -R ${WHOAMI} /opt/micromamba && \
curl -Ls https://micro.mamba.pm/api/micromamba/$PLATFORM-$ARCH/latest | tar -xvj -C /opt/micromamba/bin/ --strip-components=1 bin/micromamba && \
/opt/micromamba/bin/micromamba shell init --prefix /opt/micromamba && \
eval "$(/opt/micromamba/bin/micromamba shell hook --shell=bash)" && \
micromamba config prepend channels conda-forge && \
/opt/micromamba/bin/micromamba clean -tiply --trash && \
/opt/micromamba/bin/micromamba clean -afy && \
source ~/.bashrc && \
micromamba self-update
echo "micromamba install done."
