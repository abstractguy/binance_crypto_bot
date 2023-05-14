#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File:        utils/exchange.py
# By:          Samuel Duclos
# For:         Myself
# Description: This file handles python-binance global exchange info.

# Library imports.
from typing import Optional
from binance.client import Client
from os import mkdir
from os.path import exists, join
import pandas as pd

# Class definition.
class Cryptocurrency_exchange:
    def __init__(self, 
                 client: Optional[Client] = None, 
                 directory: str = 'crypto_logs'):
        self.client = client
        self.info_path = join('crypto_logs', 'crypto_exchange_info.txt')
        if not exists(directory):
            mkdir(directory)
        if exists(self.info_path):
            self.info = pd.read_csv(self.info_path, index_col=0)
        else:
            self.get_exchange_info()
            self.info.to_csv(self.info_path)

    def get_exchange_info(self) -> None:
        def build_filters(symbols_info: pd.DataFrame, index: int) -> pd.DataFrame:
            symbol = symbols_info['symbol'].iat[index]
            df = pd.DataFrame(symbols_info['filters'].iat[index])
            min_price = df[df['filterType'] == 'PRICE_FILTER']['minPrice'].iat[0]
            max_price = df[df['filterType'] == 'PRICE_FILTER']['maxPrice'].iat[0]
            tick_size = df[df['filterType'] == 'PRICE_FILTER']['tickSize'].iat[0]
            step_size = df[df['filterType'] == 'LOT_SIZE']['stepSize'].iat[0]
            multiplier_up = df[df['filterType'] == 'PERCENT_PRICE_BY_SIDE']['avgPriceMins'].iat[0]
            return pd.DataFrame([[symbol, min_price, max_price, tick_size, step_size, multiplier_up]], 
                                columns=['symbol', 'min_price', 'max_price', 'tick_size', 'step_size', 
                                         'multiplier_up'])
        symbols_info = self.client.get_exchange_info()
        symbols_info = pd.DataFrame(pd.DataFrame([symbols_info])['symbols'].iat[0])
        symbols_info = symbols_info[symbols_info['status'] == 'TRADING']
        symbols_info = symbols_info[symbols_info['isSpotTradingAllowed']]
        symbols_info = symbols_info[symbols_info['quoteOrderQtyMarketAllowed']]
        symbols_info = symbols_info.drop(columns=['status', 'isSpotTradingAllowed', 'isMarginTradingAllowed', 
                                                  'permissions', 'icebergAllowed', 'ocoAllowed', 
                                                  'quoteOrderQtyMarketAllowed', 'orderTypes'])
        symbols_info = symbols_info.set_index('symbol', drop=False)
        filters = [build_filters(symbols_info, i) for i in range(symbols_info.shape[0])]
        filters = [x for x in filters if x is not None]
        df = pd.DataFrame()
        for x in filters:
            df = pd.concat([df, x], axis='index')
        df = df.set_index('symbol')
        symbols_info = pd.concat([symbols_info, df], axis='columns')
        self.info = symbols_info.drop(columns=['symbol', 'filters']).reset_index('symbol')
        self.info = self.info.rename(columns={'baseAsset': 'base_asset', 
                                              'baseAssetPrecision': 'base_asset_precision', 
                                              'quoteAsset': 'quote_asset', 
                                              'quotePrecision': 'quote_precision', 
                                              'quoteAssetPrecision': 'quote_asset_precision', 
                                              'baseCommissionPrecision': 'base_asset_commission', 
                                              'quoteCommissionPrecision': 'quote_commission_precision', 
                                              'allowTrailingStop': 'allow_trailing_stop', 
                                              'cancelReplaceAllowed': 'cancel_replace_allowed'})
