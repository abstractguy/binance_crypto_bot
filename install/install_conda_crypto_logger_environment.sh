#!/usr/bin/env bash

# File:        install/install_conda_crypto_logger_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       bash install/install_conda_crypto_logger_environment.sh
# Description: Installs all packages required for the crypto_logger.

CONDA_ENV_NAME="crypto_logger"

# Automagic.
/opt/conda/bin/conda create --yes --name ${CONDA_ENV_NAME} --channel conda-forge gcc \
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
/opt/conda/bin/conda init bash && \
source /opt/conda/bin/activate ${CONDA_ENV_NAME} && \
if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" == "${CONDA_ENV_NAME}" ]]
then
    #yes | pip install --upgrade --no-cache-dir numpy git+https://github.com/twopirllc/pandas-ta
    yes | pip install --upgrade --no-cache-dir git+https://github.com/twopirllc/pandas-ta
else
    echo "Could not source activate ${CONDA_ENV_NAME}..."
fi
