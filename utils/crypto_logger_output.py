#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/crypto_logger_output.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for arbitrary intervals.

# Library imports.
from typing import List, Tuple, Union
from .crypto_logger_base import Crypto_logger_base
from .indicators import filter_in_market, screen_one
import pandas as pd

# Class definition.
class Crypto_logger_output(Crypto_logger_base):
    def __init__(self, 
                 interval_input: str = '15s', 
                 interval: str = '15s', 
                 buffer_size: int = 60, 
                 input_log_name: str = 'input', 
                 append: bool = True, 
                 roll: int = 60):
        """
        :param interval_input: OHLCV interval from input log. Default is 15 seconds.
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param buffer_size: buffer size to avoid crashing on memory accesses.
        :param input_log_name: either input or output (this ends up in the log file name).
        :param append: whether to append the latest screened data to the log dumps or not.
        :param roll: buffer size to cut oldest data (0 means don't cut).
        """
        super().__init__(interval=interval, interval_input=interval_input, buffer_size=buffer_size, 
                         directory='crypto_logs', log_name='crypto_output_log_' + interval, 
                         input_log_name=input_log_name, raw=False, append=append, roll=roll)

    def screen(self, 
               dataset: Union[pd.DataFrame, None], 
               dataset_screened: Union[pd.DataFrame, None], 
               live_filtered: Union[List[str], None] = None) -> Tuple[Union[pd.DataFrame, None], Union[List[str], None]]:
        if dataset is not None:
            if dataset_screened is not None:
                input_filter = set(dataset_screened['symbol'].tolist())
                old_columns = set(dataset.columns.get_level_values(0).tolist())
                new_columns = (input_filter & old_columns)
                if live_filtered is not None:
                    new_columns = (new_columns & set(live_filtered))
                assets = filter_in_market(screen_one, dataset[list(new_columns)])
                dataset_screened = dataset_screened[dataset_screened['symbol'].isin(assets)]
        return dataset_screened, None

    def resample_from_raw(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[['symbol', 'close', 'rolling_base_volume', 'rolling_quote_volume']].copy()
        df['base_volume'] = df['rolling_base_volume'].copy()
        df['quote_volume'] = df['rolling_quote_volume'].copy()
        values = ['close', 'rolling_base_volume', 'rolling_quote_volume', 'base_volume', 'quote_volume']
        aggfunc = {'close': [('open', 'first'), ('high', 'max'), ('low', 'min'), ('close', 'last')], 
                   'base_volume': [('base_volume', 'max')], 'quote_volume': [('quote_volume', 'max')], 
                   'rolling_base_volume': [('rolling_base_volume', 'max')], 
                   'rolling_quote_volume': [('rolling_quote_volume', 'max')]}
        df = df.pivot_table(index=['date'], columns=['symbol'], values=values, aggfunc=aggfunc)
        df.columns = df.columns.droplevel(0)
        df = df.sort_index(axis='index').iloc[1:]
        df.columns.names = ['feature', 'symbol']
        df['base_volume'] = df['base_volume'].fillna(0)
        df['quote_volume'] = df['quote_volume'].fillna(0)
        df = df.fillna(method='pad').fillna(method='backfill') # Last resort.
        df.columns = df.columns.swaplevel('feature', 'symbol')
        return df

    def get(self, dataset: Union[pd.DataFrame, None] = None) -> Union[pd.DataFrame, None]:
        if dataset is not None:
            if self.connected_to_raw:
                dataset = self.resample_from_raw(dataset)
            dataset = dataset.tail(2)
        return dataset
