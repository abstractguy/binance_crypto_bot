#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/crypto_logger_input.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger circular buffered for N time precision.

# Library imports.
from typing import List, Tuple, Union
from .crypto_logger_base import Crypto_logger_base
from .authentication import Cryptocurrency_authenticator
from .exchange import Cryptocurrency_exchange
from .conversion import get_timezone_offset_in_seconds
from .conversion import precompute_shortest_paths
from .conversion_table import get_conversion_table, get_tradable_tickers_info
import pandas as pd

# Class definition.
class Crypto_logger_input(Crypto_logger_base):
    def __init__(self, 
                 interval: str = '15s', 
                 buffer_size: int = 3000, 
                 price_percent: float = 5.0, 
                 volume_percent: float = 0.0, 
                 as_pair: bool = False, 
                 append: bool = False, 
                 roll: int = 1000):
        """
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param buffer_size: buffer size to avoid crashing on memory accesses.
        :param price_percent: price move percent.
        :param volume_percent: volume move percent.
        """
        self.price_percent = price_percent
        self.volume_percent = volume_percent
        self.as_pair = as_pair
        super().__init__(interval=interval, interval_input='', buffer_size=buffer_size, 
                         directory='crypto_logs', log_name='crypto_input_log_' + interval, 
                         input_log_name='', raw=True, append=append, roll=roll)

        authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
        self.client = authenticator.spot_client

        exchange = Cryptocurrency_exchange(client=self.client, directory=self.directory)
        self.exchange_info = exchange.info

        self.shortest_paths = precompute_shortest_paths(self.exchange_info, 
                                                priority=None, 
                                                shortest_paths_file='crypto_logs/shortest_paths.pkl')

        self.offset_s = get_timezone_offset_in_seconds()

    def filter_movers(self, 
                      dataset: pd.DataFrame, 
                      count: int = 1000, 
                      price_percent: float = 5.0, 
                      volume_percent: float = 0.0) -> pd.DataFrame:
        dataset = dataset.reset_index()
        dataset[['price_change_percent', 'rolling_base_volume']] = \
            dataset[['price_change_percent', 'rolling_base_volume']].astype(float)
        dataset['last_price_move'] = dataset['price_change_percent'].copy()
        dataset['last_volume_move'] = dataset['rolling_base_volume'].copy()
        movers = dataset.groupby(['symbol'])
        dataset = dataset.drop(columns=['last_price_move', 'last_volume_move'])
        price_movers = movers['last_price_move']
        volume_movers = movers['last_volume_move']
        price_movers = price_movers.agg(lambda x: x.diff(1).abs().iloc[-1])
        volume_movers = volume_movers.agg(lambda x: (100 * x.pct_change(1)).iloc[-1])
        price_movers = price_movers.sort_values(ascending=False)
        volume_movers = volume_movers.sort_values(ascending=False)
        price_movers = price_movers[price_movers > 0.0]
        price_movers = price_movers.to_frame(name='last_price_move')
        volume_movers = volume_movers.to_frame(name='last_volume_move')
        movers = pd.concat([price_movers, volume_movers], axis='columns')
        movers = movers.reset_index()
        price_movers_mask = movers['last_price_move'] > price_percent
        volume_movers_mask = movers['last_volume_move'] > volume_percent
        movers = movers[price_movers_mask & volume_movers_mask]
        movers = movers.sort_values(by=['last_volume_move', 'last_price_move'], ascending=False)
        movers = movers.tail(count)
        movers = movers.reset_index(drop=True)
        #dataset = dataset.set_index('symbol')
        #movers = movers.set_index('symbol')
        #dataset = dataset.merge(right=movers, how='right', left_index=True, right_index=True)
        dataset = dataset.merge(right=movers, how='right', on=['symbol'])
        dataset = dataset.set_index('date')
        return dataset.drop_duplicates(subset=['symbol', 'count'], keep='last')

    def screen(self, 
               dataset: pd.DataFrame, 
               dataset_screened: Union[pd.DataFrame, None] = None, 
               live_filtered: Union[pd.DataFrame, None] = None) -> Tuple[pd.DataFrame, List[str]]:
        if dataset is None:
            live_filtered = []
        else:
            dataset, live_filtered = get_tradable_tickers_info(dataset)
            dataset_screened = self.filter_movers(dataset, count=1000, 
                                                  price_percent=self.price_percent, 
                                                  volume_percent=self.volume_percent)
        return dataset_screened, live_filtered

    def get(self, dataset: Union[pd.DataFrame, None] = None) -> pd.DataFrame:
        """Get all pairs data from Binance API."""
        dataset = get_conversion_table(client=self.client, exchange_info=self.exchange_info, 
                                       offset_s=self.offset_s, dump_raw=False, as_pair=self.as_pair, 
                                       minimal=False, extra_minimal=True, super_extra_minimal=False, 
                                       convert_to_USDT=False, shortest_paths=self.shortest_paths)
        dataset.index = dataset.index.round(self.interval)
        return dataset
