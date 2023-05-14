#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/resample.py
# By:          Samuel Duclos
# For          Myself
# Description: Provides whole market downsampling.

# Library imports.
from .volume_conversion import recalculate_volumes
#from .ohlcv_cleaning import clean_data
import pandas as pd

# Function definitions.
def resample(df: pd.DataFrame, interval: str = '1min') -> pd.DataFrame:
    df.index = pd.DatetimeIndex(df.index).round(interval)
    df = df.stack(level=0).reset_index(level=1)
    frequency = (df.index[1:] - df.index[:-1]).min()
    frequency = pd.tseries.frequencies.to_offset(frequency)
    frequency_interval = pd.tseries.frequencies.to_offset(interval)
    frequency_1min = pd.tseries.frequencies.to_offset('1min')
    frequency_1d = pd.tseries.frequencies.to_offset('1d')
    volume_operation = 'sum' if frequency_interval >= frequency_1min else 'last'
    rolling_volume_operation = 'sum' if frequency_interval >= frequency_1d else 'last'
    values = ['open', 'high', 'low', 'close', 'base_volume', 'quote_volume', 
              'rolling_base_volume', 'rolling_quote_volume']
    aggfunc = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 
               'base_volume': volume_operation, 'quote_volume': volume_operation, 
               'rolling_base_volume': rolling_volume_operation, 
               'rolling_quote_volume': rolling_volume_operation}
    df = df.pivot_table(index=['date'], columns=['symbol'], values=values, aggfunc=aggfunc)
    df['base_volume'] = df['base_volume'].fillna(0)
    df['quote_volume'] = df['quote_volume'].fillna(0)
    df = df.fillna(method='pad').fillna(method='backfill') # Last resort.
    #df = clean_data(df)
    df.columns = df.columns.swaplevel(0, 1)
    df.sort_index(axis='index', inplace=True)
    df.sort_index(axis='columns', inplace=True)
    if interval == '1min':
        df = recalculate_volumes(df)
    return df
