#!/usr/bin/env bash

# File:          install/install_conda.sh
# By:            Samuel Duclos
# For            Myself
# Description:   Install conda.
# Usage:         bash install/install_conda.sh <PASSWORD>
# Example 1:     bash install/install_conda.sh password123
# Example 2:     bash install/install_conda.sh
# Arguments:     <PASSWORD>: optional sudo password    (default is "")

# Parse and set optional password argument from command-line.
PASSWORD=$(echo "${1:-}")

# Take password from command-line if set, else ask live.
if [[ "$(echo ${PASSWORD})" == "" ]]
then
    read -s -p "Enter your password: " PASSWORD
fi

# Automagic.
echo ${PASSWORD} | sudo -S apt-get update && \
echo ${PASSWORD} | sudo -S apt-get install -y avrdude bzip2 ca-certificates git libglib2.0-0 libxext6 libsm6 libxrender1 mercurial subversion wget && \
echo ${PASSWORD} | sudo -S apt clean && \
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
echo ${PASSWORD} | sudo -S /bin/bash ~/miniconda.sh -b -p /opt/conda && \
rm ~/miniconda.sh && \
WHOAMI=$(env | grep "USER=" | sed 's/USER=//') && \
echo ${PASSWORD} | sudo -S chown -R ${WHOAMI} /opt/conda && \
/opt/conda/bin/conda init && \
/opt/conda/bin/conda clean -tipy && \
/opt/conda/bin/conda clean -afy && \
echo ${PASSWORD} | sudo -S chown -R ${WHOAMI} /home/${WHOAMI} && \
source ~/.bashrc && \
echo "conda install done. Please exit the terminal and open another one..."
