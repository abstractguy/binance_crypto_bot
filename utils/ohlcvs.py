#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/data/download/binance/ohlcvs.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from typing import List, Optional
from binance.client import Client
from .ohlcv import download_pair
from tqdm import tqdm
from .timezone import get_timezone_offset_in_seconds
from .ohlcv_cleaning import clean_data
import time
import pandas as pd

# Function definitions.
def named_pairs_to_df(assets: List[str], pairs: List[pd.DataFrame]) -> pd.DataFrame:
    df = pd.DataFrame()
    column_names = pairs[0].columns.tolist()
    for (asset, pair) in tqdm(zip(assets, pairs), unit=' named pair'):
        columns = [(asset, column) for column in column_names]
        pair.columns = pd.MultiIndex.from_tuples(columns, names=['symbol', 'feature'])
        df = pd.concat([df, pair], axis='columns')
    return df

def download_pairs(client: Client, 
                   assets: List[str], 
                   interval: str = '1m', 
                   period: int = 2880, 
                   second_period: Optional[int] = None, 
                   offset_s: float = 0) -> pd.DataFrame:
    def download_pairs_helper(period=2880, offset_s=0):
        pairs = [download_pair(client=client, symbol=symbol, interval=interval, 
                               period=period, offset_s=offset_s) 
                 for symbol in tqdm(assets, unit=' pair')]
        pairs = named_pairs_to_df(assets, pairs)
        pairs = pairs.sort_index(axis='index')
        pairs.columns = pairs.columns.swaplevel(0, 1)
        pairs = pairs[['open', 'high', 'low', 'close', 'base_volume', 'quote_volume']]
        pairs.columns = pairs.columns.swaplevel(0, 1)
        return pairs.sort_index(axis='columns')
    pairs_1 = download_pairs_helper(period=period, offset_s=offset_s)
    if second_period is None:
        pairs = pairs_1
    else:
        pairs_2 = download_pairs_helper(period=second_period, offset_s=offset_s)
        pairs = pd.concat([pairs_1, pairs_2], join='outer', axis='index')
    pairs = pairs[~pairs.index.duplicated(keep='last')]
    #pairs.iloc[:,pairs.columns.get_level_values(1) == 'base_volume'] = \
    #    pairs.xs('base_volume', axis=1, level=1).fillna(0)
    #pairs.iloc[:,pairs.columns.get_level_values(1) == 'quote_volume'] = \
    #    pairs.xs('quote_volume', axis=1, level=1).fillna(0)
    #return pairs.fillna(method='pad')
    pairs = clean_data(pairs)
    return pairs

def download_pairs_bootstrapped(client: Client, assets: List[str], 
                                interval: str = '1m', offset_s: float = 0) \
        -> pd.DataFrame:
    period = 2880 if interval == '1m' else 60
    second_period = 60 if interval == '1m' else None
    return download_pairs(client, assets, interval='1m', period=period, 
                          second_period=second_period, offset_s=offset_s)
