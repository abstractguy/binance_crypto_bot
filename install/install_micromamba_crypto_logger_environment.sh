##!/usr/bin/env bash

# File:        install/install_micromamba_crypto_logger_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       source install/install_micromamba_crypto_logger_environment.sh
# Description: Installs all packages required for the crypto_logger.

MICROMAMBA_ENV_NAME="crypto_logger"
micromamba create --yes --name ${MICROMAMBA_ENV_NAME} gcc \
                                                      gxx_linux-64 \
                                                      cython \
                                                      bottleneck \
                                                      numexpr \
                                                      numpy \
                                                      numba \
                                                      pandas \
                                                      matplotlib \
                                                      scipy \
                                                      ta \
                                                      ta-lib \
                                                      tqdm \
                                                      python-binance \
                                                      typing_extensions \
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
