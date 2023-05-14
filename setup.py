#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:              setup.py
# By:                Samuel Duclos
# For:               Myself
# Description:       Compile to C before running.
# Optimize:          python setup.py build_ext --inplace
# Optimize manually: 
#                    python -m cython -3 -a crypto_logger.py
#                    gcc -shared -pthread -fPIC -fwrapv -Wall -O3 -fno-strict-aliasing -mtune=native -I/opt/conda/envs/crypto_bot/include/python3.9/ -o crypto_logger.so crypto_logger.c

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import sys
import numpy

env = "crypto_bot"
version_info = sys.version_info
include_path = "/opt/conda/envs/{}/include/python{}.{}/"
include_path = [include_path.format(env, 
                                    version_info.major, 
                                    version_info.minor)]
extra_compile_args = ["-Os", 
                      "-fno-strict-aliasing", 
                      "-mtune=native", 
                      "-march=native", 
                      "-fPIC", 
                      "-fwrapv", 
                      "-Wall", 
                      "-pthread", 
                      "-shared", 
                      "-Wno-unused-function", 
                      "-Wno-maybe-uninitialized", 
                      "-Wno-unused-variable", 
                      "-Wno-unused-but-set-variable", 
                      "-Wno-unused-result"]

setup(
    name="crypto_bot", 
    cmdclass={'build_ext': build_ext}, 
    include_dirs = [numpy.get_include()], 
    ext_modules=cythonize(
        [
            Extension(
                name="crypto_logger_5s", 
                sources=["crypto_logger_5s.py"], 
                extra_compile_args=extra_compile_args, 
                language="c++", 
            ), 
        [
            Extension(
                name="crypto_output_logger_1min", 
                sources=["crypto_output_logger_1min.py"], 
                extra_compile_args=extra_compile_args, 
                language="c++", 
            ), 
            Extension(
                name="crypto_trader", 
                sources=["crypto_trader.py"], 
                extra_compile_args=extra_compile_args, 
                language="c++", 
            ), 
            Extension(
                name="crypto_mqtt_pub", 
                sources=["crypto_mqtt_pub.py"], 
                extra_compile_args=extra_compile_args, 
                language="c++", 
            ), 
            Extension(
                name="crypto_mqtt_sub", 
                sources=["crypto_mqtt_sub.py"], 
                extra_compile_args=extra_compile_args, 
                language="c++", 
            ), 
        ], 
        include_path=include_path, 
        language_level=3, 
    ), 
)
