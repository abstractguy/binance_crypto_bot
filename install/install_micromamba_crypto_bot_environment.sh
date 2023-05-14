#!/usr/bin/env bash

# File:        install/install_micromamba_crypto_bot_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       source install/install_micromamba_crypto_bot_environment.sh
# Description: Installs all packages required for the crypto_bot.

MICROMAMBA_ENV_NAME="crypto_bot"
micromamba create --yes --name ${MICROMAMBA_ENV_NAME} gcc \
                                                      gxx_linux-64 \
                                                      cython \
                                                      numpy \
                                                      numba \
                                                      bottleneck \
                                                      numexpr \
                                                      pandas \
                                                      scipy \
                                                      matplotlib \
                                                      seaborn \
                                                      setuptools-git \
                                                      tqdm \
                                                      mosquitto \
                                                      paramiko \
                                                      regex \
                                                      ta \
                                                      ta-lib \
                                                      ipywidgets \
                                                      jupyterlab \
                                                      widgetsnbextension \
                                                      typeguard \
                                                      typing_extensions \
                                                      click \
                                                      dateparser \
                                                      beautifulsoup4 \
                                                      flask-socketio \
                                                      requests \
                                                      websockets \
                                                      python-binance \
                                                      pip \
                                                      python=3 && \
micromamba activate ${MICROMAMBA_ENV_NAME} && \
if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" == "${MICROMAMBA_ENV_NAME}" ]]
then
    yes | pip install --upgrade --no-cache-dir git+https://github.com/twopirllc/pandas-ta
else
    echo "Could not source activate ${MICROMAMBA_ENV_NAME}..."
fi && \
micromamba deactivate
