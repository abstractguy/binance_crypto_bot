#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/bootstrap.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from .conversion_ohlcv import convert_ohlcvs_from_pairs_to_assets
from .ohlcvs import download_pairs
from .resample import resample
from .volume_conversion import add_rolling_volumes
from typing import Dict, List, Tuple, Optional
from binance.client import Client
from tqdm import tqdm
import pandas as pd

# Function definitions.
def bootstrap_loggers(client: Client, 
                      assets: pd.DataFrame, 
                      exchange_info: Dict[str, Dict[str, List[str]]], 
                      download_interval: Optional[str] = '1m', 
                      as_pair: Optional[bool] = False, 
                      pairs: Optional[Dict[str, pd.DataFrame]] = None, 
                      additional_intervals: Optional[List[str]] = None, 
                      upsampled_intervals: Optional[List[str]] = None, 
                      shortest_paths: Optional[Dict[str, Dict[str, Dict[str, 
                          List[Tuple[str, str]]]]]] = None) \
        -> Dict[str, pd.DataFrame]:
    base_interval = download_interval + 'in' \
        if download_interval[-1] == 'm' else download_interval
    pairs[base_interval] = assets
    frequency_1min = pd.tseries.frequencies.to_offset('1min')
    frequency_1d = pd.tseries.frequencies.to_offset('1d')
    frequency = pd.tseries.frequencies.to_offset(base_interval)
    if not as_pair:
        pairs[base_interval] = convert_ohlcvs_from_pairs_to_assets(
            pairs[base_interval], exchange_info, shortest_paths=shortest_paths)
    pairs[base_interval] = add_rolling_volumes(pairs[base_interval])
    if frequency < frequency_1d:
        pairs[base_interval] = \
            pairs[base_interval].loc[
                pairs[base_interval].dropna().first_valid_index():]
    log_file = 'crypto_logs/crypto_output_log_{}.txt'
    if additional_intervals is not None:
        for additional_interval in tqdm(additional_intervals, unit=' pair'):
            pairs[additional_interval] = resample(
                pairs[base_interval].copy(), interval=additional_interval)
            pairs[additional_interval] = pairs[additional_interval].tail(60)
            pairs[additional_interval].to_csv(
                log_file.format(additional_interval))
    truncated_frequency = 60 if frequency > frequency_1min else 1500
    pairs[base_interval] = pairs[base_interval].tail(truncated_frequency)
    pairs[base_interval].to_csv(log_file.format(base_interval))
    if upsampled_intervals is not None:
        for subminute_interval in tqdm(upsampled_intervals, unit=' pair'):
            pairs[subminute_interval] = pairs[base_interval].tail(25)
            pairs[subminute_interval] = \
                pairs[subminute_interval].resample(
                    subminute_interval).agg('max')
            pairs[subminute_interval] = \
                pairs[subminute_interval].fillna(method='pad').tail(60)
            pairs[subminute_interval].to_csv(log_file.format(
                subminute_interval))
    return pairs
