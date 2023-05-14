#!/usr/bin/env bash

# File:        install/install_conda_crypto_bot_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       bash install/install_conda_crypto_bot_environment.sh
# Description: Installs all packages required for the crypto_bot.

CONDA_ENV_NAME="crypto_bot"

# Automagic.
/opt/conda/bin/conda create --yes --name ${CONDA_ENV_NAME} --channel conda-forge gcc \
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
/opt/conda/bin/conda init bash && \
source /opt/conda/bin/activate ${CONDA_ENV_NAME} && \
if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" == "${CONDA_ENV_NAME}" ]]
then
    #yes | pip install --upgrade --no-cache-dir numpy git+https://github.com/twopirllc/pandas-ta
    yes | pip install --upgrade --no-cache-dir git+https://github.com/twopirllc/pandas-ta
else
    echo "Could not source activate ${CONDA_ENV_NAME}..."
fi
