#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/volume_conversion.py
# By:          Samuel Duclos
# For          Myself
# Description: Whole market volume to/from 24h rolling volume conversion.

# Library imports.
#import numba
import numpy as np
import pandas as pd

# Function definitions.
'''
@numba.jit(nopython=True, nogil=True, cache=True)
def add_rolling_volumes_numba(df: np.ndarray) -> np.ndarray:
    df_rolling = df[:,[0, 1]].copy()
    df_rolling[:,0] = np.cumsum(df_rolling[:,0])
    df_rolling[:,1] = np.cumsum(df_rolling[:,1])
    df_rolling = df_rolling[1440:] - df_rolling[:-1440]
    df = np.concatenate((df, df_rolling), axis=1)
    return df

@numba.jit(nopython=True, nogil=True, cache=True)
def recalculate_volumes_numba(df: np.ndarray) -> np.ndarray:
    df[-2:,0] = df[-2:,6] - df[-2:,0] + df[-1442:-2,0]
    df[-2:,1] = df[-2:,7] - df[-2:,1] + df[-1442:-2,1]
    return df
'''

def add_rolling_volumes(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.swaplevel(0, 1)
    df_rolling = df[['base_volume', 'quote_volume']].copy()
    df_rolling.rename(columns={'base_volume': 'rolling_base_volume', 
                               'quote_volume': 'rolling_quote_volume'}, 
                      inplace=True)
    df_rolling = df_rolling.rolling('1440min').agg(np.sum)
    df = pd.concat([df, df_rolling], join='outer', axis='columns')
    df = df[['open', 'high', 'low', 'close', 'base_volume', 'quote_volume', 
             'rolling_base_volume', 'rolling_quote_volume']]
    df.columns = df.columns.swaplevel(0, 1)
    return df

def recalculate_volumes(df: pd.DataFrame) -> pd.DataFrame:
    df.iloc[-2:,df.columns.get_level_values(1) == 'base_volume'] = \
        df.xs('rolling_base_volume', axis=1, level=1).diff(1).tail(2) + \
        df.xs('base_volume', axis=1, level=1).shift(1440).tail(2)
    df.iloc[-2:,df.columns.get_level_values(1) == 'quote_volume'] = \
        df.xs('rolling_quote_volume', axis=1, level=1).diff(1).tail(2) + \
        df.xs('quote_volume', axis=1, level=1).shift(1440).tail(2)
    return df
