#!/usr/bin/env bash

# File:        bootstrap.sh
# By:          Samuel Duclos
# For:         Myself
# Description: Convenience script to bootstrap and start crypto_logger services.
# Usage:       bash bootstrap.sh

CONDA_ENV_NAME="crypto_logger"

read -s -p "Password: " PASSWORD

echo $PASSWORD | sudo -S supervisorctl stop all
echo $PASSWORD | sudo -S rm -rf /tmp/crypto.[err,out]
echo $PASSWORD | sudo -S rm -rf ~/workspace/build
echo $PASSWORD | sudo -S rm -rf *.[c,cpp,so]
echo $PASSWORD | sudo -S supervisorctl status all

source activate ${CONDA_ENV_NAME} && \
if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" == "${CONDA_ENV_NAME}" ]]
then
    python setup.py build_ext --inplace && \
    python bootstrap.py
else
    echo "Could not source activate ${CONDA_ENV_NAME}..."
fi

echo $PASSWORD | sudo -S supervisorctl start all
sleep 15

echo $PASSWORD | sudo -S supervisorctl status all
sleep 15

watch -n 5 tail -n 40 ~/workspace/crypto_logs/crypto_input_log_*_screened.txt
