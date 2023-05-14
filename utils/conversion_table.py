#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/conversion_table.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance pair conversion table retrieval and preparation.

# Library imports.
from typing import Dict, List, Tuple, Union, Optional
from binance.client import Client
from .conversion import convert_price
from .conversion import get_base_asset_from_pair, get_quote_asset_from_pair
import datetime
import pandas as pd

# Function definitions.
def get_conversion_table_from_binance(client: Client, 
                                      exchange_info: pd.DataFrame, 
                                      offset_s: float = 0, 
                                      dump_raw: bool = False) -> pd.DataFrame:
    conversion_table = pd.DataFrame(client.get_ticker())
    conversion_table = conversion_table[conversion_table['symbol'].isin(
        exchange_info['symbol'])]

    conversion_table['base_asset'] = conversion_table['symbol'].apply(
        lambda x: get_base_asset_from_pair(x, exchange_info=exchange_info))
    conversion_table['quote_asset'] = conversion_table['symbol'].apply(
        lambda x: get_quote_asset_from_pair(x, exchange_info=exchange_info))

    conversion_table = conversion_table.rename(columns={
        'openPrice': 'open', 'highPrice': 'high', 'lowPrice': 'low', 
        'lastPrice': 'close', 'lastQty': 'last_volume', 
        'volume': 'rolling_base_volume', 
        'quoteVolume': 'rolling_quote_volume', 
        'bidPrice': 'bid_price', 'askPrice': 'ask_price', 
        'bidQty': 'bid_volume', 'askQty': 'ask_volume', 'firstId': 'first_ID', 
        'lastId': 'last_ID', 'openTime': 'open_time', 'closeTime': 'date', 
        'prevClosePrice': 'close_shifted', 
        'weightedAvgPrice': 'weighted_average_price', 
        'priceChange': 'price_change', 
        'priceChangePercent': 'price_change_percent'})

    if dump_raw:
        conversion_table.to_csv('crypto_logs/conversion_table.txt')

    conversion_table[[
        'open', 'high', 'low', 'close', 'close_shifted', 
        'rolling_base_volume', 'rolling_quote_volume', 'bid_price', 
        'ask_price', 'bid_volume', 'ask_volume', 'price_change_percent']] = \
            conversion_table[[
                'open', 'high', 'low', 'close', 'close_shifted', 
                'rolling_base_volume', 'rolling_quote_volume', 'bid_price', 
                'ask_price', 'bid_volume', 'ask_volume', 
                'price_change_percent']].astype(float)

    conversion_table[['date', 'count']] = \
        conversion_table[['date', 'count']].astype(int)
    conversion_table['date'] = (conversion_table['date'] + offset_s * 1000)
    conversion_table['date'] /= 1000
    conversion_table['date'] = conversion_table['date'].apply(
        datetime.datetime.fromtimestamp)
    conversion_table['date'] = pd.DatetimeIndex(conversion_table['date'])
    return conversion_table.sort_values(by='date')

def process_conversion_table(conversion_table: pd.DataFrame, 
                             exchange_info: pd.DataFrame, 
                             as_pair: bool = False, 
                             minimal: bool = False, 
                             extra_minimal: bool = True, 
                             super_extra_minimal: bool = False, 
                             convert_to_USDT: bool = False, 
                             shortest_paths: Optional[Dict[str, Dict[str, 
                                             Dict[str, List[Tuple[str, 
                                                 str]]]]]] = None) -> \
        pd.DataFrame:
    """
    Fetches and calculates data used for prices, volumes and other stats.
    :param client: \
        object from python-binance useful for calling client.get_ticker().
    :param exchange_info: Pre-calculated exchange information on all tickers.
    :return: pd.DataFrame containing all preprocessed conversion table info.
    :column is_shorted: is the symbol made from inversion.
    :column symbol: concatenated string made from base_asset and quote_asset.
    :column shorted_symbol: symbol with inverted base_asset and quote_asset.
    :column base_asset: asset on the left.
    :column quote_asset: asset on the right.
    :column price_change: (close - open).
    :column price_change_percent: (((close - open) / open) * 100).
    :column USDT_price_change: (USDT_close - USDT_open).
    :column USDT_price_change_percent: \
        (((USDT_close - USDT_open) / USDT_open) * 100).
    :column weighted_average_price: weighted average price.
    :column close_shifted: close price of the previous day.
    :column open: open price of the day.
    :column high: high price of the day.
    :column low: low price of the day.
    :column close: close price of the day.
    :column last_volume: volume of the last price update.
    :column USDT_bid_price: USDT-converted bid price.
    :column USDT_ask_price: USDT-converted ask price.
    :column USDT_bid_volume: USDT-converted bid volume.
    :column USDT_ask_volume: USDT-converted ask volume.
    :column bid_price: price of the bid.
    :column bid_volume: volume of the bid at bid_price.
    :column ask_price: price of the ask.
    :column ask_volume: volume of the ask at ask_price.
    :column rolling_base_volume: rolling_base_volume given by the API.
    :column rolling_quote_volume: rolling_quote_volume given by the API.
    :column open_time: date minus 24 hours.
    :column date: time from epoch in milliseconds of the last price update.
    :column first_ID: transaction ID from 1 day ago.
    :column last_ID: latest transaction ID.
    :column count: value calculated by subtracting first_ID from last_ID.
    :column USDT_open: USDT-converted open price.
    :column USDT_high: USDT-converted high price.
    :column USDT_low: USDT-converted low price.
    :column USDT_price: USDT-converted close price.
    :column rolling_USDT_base_volume: USDT-converted rolling_base_volume.
    :column rolling_USDT_quote_volume: USDT-converted rolling_quote_volume.
    :column rolling_traded_volume: \
        sum by base_asset of all USDT-converted volumes.
    :column importance: \
        rolling_USDT_base_volume divided by rolling_traded_volume.
    :column traded_price: \
        sum by base_asset of all (close prices times importance).
    :column traded_bid_price: \
        sum by base_asset of all (bid prices times importance).
    :column traded_ask_price: \
        sum by base_asset of all (ask prices times importance).
    :column bid_ask_percent_change: \
        ((ask_price - bid_price) / ask_price) * 100).
    :column bid_ask_volume_percent_change: \
        ((bid_volume / (bid_volume + ask_volume)) * 100).
    :column traded_bid_ask_percent_change: \
        ((traded_ask_price - traded_bid_price) / traded_ask_price) * 100).
    :column traded_bid_ask_volume_percent_change: \
        ((traded_bid_volume / (traded_bid_volume + traded_ask_volume)) * 100).
    """
    if super_extra_minimal:
        extra_minimal = True

    if extra_minimal:
        minimal = True

    if as_pair:
        super_extra_minimal = False
    else:
        convert_to_USDT = True

    if minimal:
        conversion_table = conversion_table[[
            'symbol', 'base_asset', 'quote_asset', 'open', 'high', 'low', 
            'close', 'rolling_base_volume', 'rolling_quote_volume', 'count', 
            'bid_price', 'ask_price', 'bid_volume', 'ask_volume', 'date', 
            'price_change_percent']]

    conversion_table = conversion_table.copy()
    conversion_table['rolling_base_quote_volume'] = \
        conversion_table['rolling_quote_volume'] / conversion_table['close']

    if convert_to_USDT:
        if not extra_minimal:
            conversion_table['high_pre_conversion'] = \
                (((conversion_table['high'] - conversion_table['close']) / \
                  conversion_table['close']) + 1)
            conversion_table['low_pre_conversion'] = \
                (((conversion_table['low'] - conversion_table['close']) / \
                  conversion_table['close']) + 1)

        conversion_table['bid_pre_conversion'] = \
            (((conversion_table['bid_price'] - conversion_table['close']) / \
              conversion_table['close']) + 1)
        conversion_table['ask_pre_conversion'] = \
            (((conversion_table['ask_price'] - conversion_table['close']) / \
              conversion_table['close']) + 1)

        if not super_extra_minimal:
            temp_conversion_table = conversion_table[[
                'base_asset', 'open']]
            temp_conversion_table = temp_conversion_table.drop_duplicates(
                subset=['base_asset'], keep='first')
            conversion_table['USDT_open'] = \
                temp_conversion_table.apply(
                    lambda x: convert_price(
                        size=1, from_asset=x['base_asset'], 
                        to_asset='USDT', 
                        conversion_table=conversion_table, 
                        exchange_info=exchange_info, 
                        shortest_path=shortest_paths, 
                        key='open', priority='accuracy'), axis='columns')
            conversion_table['USDT_open'] = conversion_table[[
                'base_asset', 'USDT_open']].groupby(
                    by=['base_asset']).fillna(method='pad')['USDT_open']

        temp_conversion_table = conversion_table[[
            'base_asset', 'close']]
        temp_conversion_table = temp_conversion_table.drop_duplicates(
            subset=['base_asset'], keep='first')
        conversion_table['USDT_price'] = \
            temp_conversion_table.apply(
                lambda x: convert_price(
                    size=1, from_asset=x['base_asset'], 
                    to_asset='USDT', 
                    conversion_table=conversion_table, 
                    exchange_info=exchange_info, 
                    shortest_path=shortest_paths, 
                    key='close', priority='accuracy'), axis='columns')
        conversion_table['USDT_price'] = conversion_table[[
            'base_asset', 'USDT_price']].groupby(
                by=['base_asset']).fillna(method='pad')['USDT_price']

        if not extra_minimal:
            conversion_table['USDT_high'] = \
                conversion_table['USDT_price'].astype(float) * \
                conversion_table['high_pre_conversion']
            conversion_table['USDT_low'] = \
                conversion_table['USDT_price'].astype(float) * \
                conversion_table['low_pre_conversion']

        conversion_table['USDT_bid_price'] = \
            conversion_table['USDT_price'].astype(float) * \
            conversion_table['bid_pre_conversion']
        conversion_table['USDT_ask_price'] = \
            conversion_table['USDT_price'].astype(float) * \
            conversion_table['ask_pre_conversion']
        conversion_table['USDT_bid_volume'] = \
            conversion_table['bid_volume'] * \
            conversion_table['USDT_bid_price'].astype(float)
        conversion_table['USDT_ask_volume'] = \
            conversion_table['ask_volume'] * \
            conversion_table['USDT_ask_price'].astype(float)

        conversion_table['rolling_USDT_base_volume'] = \
            conversion_table['rolling_base_volume'] * \
            conversion_table['USDT_price'].astype(float)
        conversion_table['rolling_USDT_quote_volume'] = \
            conversion_table['rolling_base_quote_volume'] * \
            conversion_table['USDT_price'].astype(float)

        if super_extra_minimal:
            price_change_percent = conversion_table[[
                'base_asset', 'price_change_percent']].groupby(
                    by='base_asset').agg(lambda x: x.iloc[x.abs().argmax()])
            conversion_table['price_change_percent'] = \
                conversion_table.apply(
                    lambda x: price_change_percent.loc[x['base_asset']], 
                    axis='columns')
        else:
            conversion_table['USDT_price_change'] = \
                (conversion_table['USDT_price'].astype(float) - \
                 conversion_table['USDT_open'].astype(float))
            conversion_table['USDT_price_change_percent'] = \
                ((conversion_table['USDT_price_change'] / \
                  conversion_table['USDT_open'].astype(float)) * 100)

        conversion_table['is_shorted'] = False

        conversion_table_swapped = conversion_table.copy()
        conversion_table_swapped = \
            conversion_table_swapped.rename(columns={
                'ask_price': 'bid_price', 
                'bid_price': 'ask_price', 
                'ask_volume': 'bid_volume', 
                'bid_volume': 'ask_volume', 
                'rolling_base_volume': 'rolling_quote_volume', 
                'rolling_quote_volume': 'rolling_base_volume', 
                'base_asset': 'quote_asset', 
                'quote_asset': 'base_asset', 
                'rolling_USDT_base_volume': 
                    'rolling_USDT_quote_volume', 
                'rolling_USDT_quote_volume': 
                    'rolling_USDT_base_volume', 
                'USDT_ask_price': 'USDT_bid_price', 
                'USDT_bid_price': 'USDT_ask_price', 
                'USDT_ask_volume': 'USDT_bid_volume', 
                'USDT_bid_volume': 'USDT_ask_volume'})
        if minimal:
            if super_extra_minimal:
                conversion_table_swapped = conversion_table_swapped[[
                    'symbol', 'price_change_percent', 'close', 
                    'ask_price', 'ask_volume', 'bid_price', 'bid_volume', 
                    'open', 'rolling_quote_volume', 'rolling_base_volume', 
                    'date', 'count', 'quote_asset', 'base_asset', 
                    'USDT_price', 'rolling_USDT_quote_volume', 
                    'rolling_USDT_base_volume', 'is_shorted']]
            else:
                conversion_table_swapped = conversion_table_swapped[[
                    'symbol', 'price_change_percent', 'close', 
                    'ask_price', 'ask_volume', 'bid_price', 'bid_volume', 
                    'open', 'rolling_quote_volume', 'rolling_base_volume', 
                    'date', 'count', 'quote_asset', 'base_asset', 
                    'USDT_open', 'USDT_price', 
                    'rolling_USDT_quote_volume', 
                    'rolling_USDT_base_volume', 'USDT_ask_price', 
                    'USDT_bid_price', 'USDT_ask_volume', 
                    'USDT_bid_volume', 'USDT_price_change_percent', 
                    'is_shorted']]
        else:
            conversion_table_swapped = conversion_table_swapped[[
                'symbol', 'price_change', 'price_change_percent', 
                'weighted_average_price', 'close_shifted', 'close', 
                'last_volume', 'ask_price', 'ask_volume', 'bid_price', 
                'bid_volume', 'open', 'high', 'low', 'rolling_quote_volume', 
                'rolling_base_volume', 'open_time', 'date', 'first_ID', 
                'last_ID', 'count', 'quote_asset', 'base_asset', 'USDT_open', 
                'USDT_high', 'USDT_low', 'USDT_price', 
                'rolling_USDT_quote_volume', 'rolling_USDT_base_volume', 
                'USDT_ask_price', 'USDT_bid_price', 'USDT_ask_volume', 
                'USDT_bid_volume', 'USDT_price_change', 
                'USDT_price_change_percent', 'is_shorted']]

        conversion_table_swapped['symbol'] = \
            conversion_table_swapped['base_asset'] + \
            conversion_table_swapped['quote_asset']

        if minimal:
            if extra_minimal:
                if super_extra_minimal:
                    conversion_table_swapped[[
                        'open', 'close', 'bid_price', 'ask_price', 
                        'USDT_price']] = \
                            1 / conversion_table_swapped[[
                                'open', 'close', 'bid_price', 'ask_price', 
                                'USDT_price']].astype(float)
                else:
                    conversion_table_swapped[[
                        'open', 'close', 'bid_price', 'ask_price', 
                        'USDT_open', 'USDT_price', 
                        'USDT_price_change_percent']] = \
                            1 / conversion_table_swapped[[
                                'open', 'close', 'bid_price', 'ask_price', 
                                'USDT_open', 'USDT_price', 
                                'USDT_price_change_percent']].astype(float)
            else:
                conversion_table_swapped[[
                    'open', 'close', 'bid_price', 'ask_price', 'USDT_open', 
                    'USDT_price', 'USDT_bid_price', 'USDT_ask_price', 
                    'USDT_price_change_percent']] = \
                        1 / conversion_table_swapped[[
                            'open', 'close', 'bid_price', 'ask_price', 
                            'USDT_open', 'USDT_price', 'USDT_bid_price', 
                            'USDT_ask_price', 'USDT_price_change_percent'
                        ]].astype(float)
        else:
            conversion_table_swapped[[
                'open', 'high', 'low', 'close', 'close_shifted', 'bid_price', 
                'ask_price', 'USDT_open', 'USDT_high', 'USDT_low', 
                'USDT_price', 'USDT_bid_price', 'USDT_ask_price', 
                'USDT_price_change', 'USDT_price_change_percent']] = \
                    1 / conversion_table_swapped[[
                        'open', 'high', 'low', 'close', 'close_shifted', 
                        'bid_price', 'ask_price', 'USDT_open', 'USDT_high', 
                        'USDT_low', 'USDT_price', 'USDT_bid_price', 
                        'USDT_ask_price', 'USDT_price_change', 
                        'USDT_price_change_percent']].astype(float)
        conversion_table_swapped['is_shorted'] = True

        conversion_table = \
            pd.concat([conversion_table, conversion_table_swapped], 
                      join='outer', axis='index')

        traded_volume = conversion_table[[
            'base_asset', 'rolling_USDT_base_volume']].groupby(
                by='base_asset').agg('sum')['rolling_USDT_base_volume']
        conversion_table['rolling_traded_volume'] = \
            conversion_table.apply(
                lambda x: traded_volume.loc[x['base_asset']], axis='columns')
        if not extra_minimal:
            traded_bid_volume = conversion_table[[
                'base_asset', 'USDT_bid_volume']].groupby(
                    by='base_asset').agg('sum')['USDT_bid_volume']
            conversion_table['traded_bid_volume'] = \
                conversion_table.apply(
                    lambda x: traded_bid_volume.loc[x['base_asset']], 
                    axis='columns')
            traded_ask_volume = conversion_table[[
                'base_asset', 'USDT_ask_volume']].groupby(
                    by='base_asset').agg('sum')['USDT_ask_volume']
            conversion_table['traded_ask_volume'] = \
                conversion_table.apply(
                    lambda x: traded_ask_volume.loc[x['base_asset']], 
                    axis='columns')

        conversion_table['importance'] = \
            conversion_table['rolling_USDT_base_volume'] / \
            conversion_table['rolling_traded_volume']
        conversion_table['importance_weighted_price'] = \
            conversion_table['USDT_price'].astype(float) * \
            conversion_table['importance']

        if not extra_minimal:
            conversion_table['importance_weighted_bid_price'] = \
                conversion_table['USDT_bid_price'].astype(float) * \
                conversion_table['importance']
            conversion_table['importance_weighted_ask_price'] = \
                conversion_table['USDT_ask_price'].astype(float) * \
                conversion_table['importance']

        importance_weighted_price = conversion_table[[
            'base_asset', 'importance_weighted_price']].groupby(
                by='base_asset').agg('sum')['importance_weighted_price']
        conversion_table['traded_price'] = conversion_table.apply(
            lambda x: importance_weighted_price.loc[x['base_asset']], 
            axis='columns')

        if not extra_minimal:
            importance_weighted_bid_price = conversion_table[[
                'base_asset', 'importance_weighted_bid_price']].groupby(
                    by='base_asset').agg('sum')['importance_weighted_bid_price']
            conversion_table['traded_bid_price'] = conversion_table.apply(
                lambda x: importance_weighted_bid_price.loc[x['base_asset']], 
                axis='columns')
            importance_weighted_ask_price = conversion_table[[
                'base_asset', 'importance_weighted_ask_price']].groupby(
                    by='base_asset').agg('sum')['importance_weighted_ask_price']
            conversion_table['traded_ask_price'] = conversion_table.apply(
                lambda x: importance_weighted_ask_price.loc[x['base_asset']], 
                axis='columns')

            conversion_table['traded_bid_ask_percent_change'] = \
                ((conversion_table['traded_ask_price'] - \
                  conversion_table['traded_bid_price']) / \
                 conversion_table['traded_ask_price'])
            conversion_table['traded_bid_ask_volume_percent_change'] = \
                (conversion_table['traded_bid_volume'] / \
                 (conversion_table['traded_bid_volume'] + \
                  conversion_table['traded_ask_volume']))
            conversion_table[['traded_bid_ask_percent_change', 
                              'traded_bid_ask_volume_percent_change']] *= 100

        conversion_table = conversion_table[~conversion_table['is_shorted']]

    conversion_table['bid_ask_percent_change'] = \
        ((conversion_table['ask_price'] - conversion_table['bid_price']) / \
         conversion_table['ask_price'])
    conversion_table['bid_ask_volume_percent_change'] = \
        (conversion_table['bid_volume'] / (conversion_table['bid_volume'] + \
                                           conversion_table['ask_volume']))
    conversion_table[['bid_ask_percent_change', 
                      'bid_ask_volume_percent_change']] *= 100
    if as_pair and convert_to_USDT:
        if minimal:
            if extra_minimal:
                conversion_table = conversion_table[[
                    'symbol', 'base_asset', 'quote_asset', 
                    'price_change_percent', 'close', 'bid_price', 
                    'bid_volume', 'ask_price', 'ask_volume', 'date', 'count', 
                    'rolling_base_volume', 'rolling_quote_volume', 
                    'USDT_price_change_percent', 'USDT_price', 
                    'rolling_USDT_base_volume', 'rolling_USDT_quote_volume', 
                    'rolling_traded_volume', 'traded_price', 
                    'bid_ask_percent_change', 'bid_ask_volume_percent_change']]
            else:
                conversion_table = conversion_table[[
                    'symbol', 'base_asset', 'quote_asset', 
                    'price_change_percent', 'close', 'bid_price', 
                    'bid_volume', 'ask_price', 'ask_volume', 'date', 'count', 
                    'rolling_base_volume', 'rolling_quote_volume', 
                    'USDT_price_change_percent', 'USDT_price', 
                    'rolling_USDT_base_volume', 'rolling_USDT_quote_volume', 
                    'USDT_bid_price', 'USDT_ask_price', 'USDT_bid_volume', 
                    'USDT_ask_volume', 'rolling_traded_volume', 
                    'traded_bid_volume', 'traded_ask_volume', 'traded_price', 
                    'traded_bid_price', 'traded_ask_price', 
                    'bid_ask_percent_change', 'bid_ask_volume_percent_change', 
                    'traded_bid_ask_percent_change', 
                    'traded_bid_ask_volume_percent_change']]
        else:
            conversion_table = conversion_table[[
                'symbol', 'base_asset', 'quote_asset', 'is_shorted', 
                'price_change_percent', 'weighted_average_price', 'open', 
                'high', 'low', 'close', 'close_shifted', 'last_volume', 
                'bid_price', 'bid_volume', 'ask_price', 'ask_volume', 'date', 
                'last_ID', 'count', 'rolling_base_volume', 
                'rolling_quote_volume', 'importance', 
                'USDT_price_change_percent', 'USDT_open', 'USDT_high', 
                'USDT_low', 'USDT_price', 'rolling_USDT_base_volume', 
                'rolling_USDT_quote_volume', 'USDT_bid_price', 
                'USDT_ask_price', 'USDT_bid_volume', 'USDT_ask_volume', 
                'rolling_traded_volume', 'traded_bid_volume', 
                'traded_ask_volume', 'traded_price', 'traded_bid_price', 
                'traded_ask_price', 'bid_ask_percent_change', 
                'bid_ask_volume_percent_change', 
                'traded_bid_ask_percent_change', 
                'traded_bid_ask_volume_percent_change']]
    else:
        if convert_to_USDT:
            if minimal:
                if extra_minimal:
                    conversion_table = conversion_table[[
                        'base_asset', 'price_change_percent', 'date', 
                        'bid_volume', 'ask_volume', 'bid_price', 'close', 
                        'ask_price', 'count', 'rolling_traded_volume', 
                        'bid_ask_percent_change', 
                        'bid_ask_volume_percent_change', 'traded_price']]
                else:
                    conversion_table = conversion_table[[
                        'base_asset', 'USDT_price_change_percent', 'date', 
                        'count', 'rolling_traded_volume', 'traded_bid_volume', 
                        'traded_ask_volume', 'traded_price', 
                        'traded_bid_price', 'traded_ask_price', 
                        'traded_bid_ask_percent_change', 
                        'traded_bid_ask_volume_percent_change']]
            else:
                conversion_table = conversion_table[[
                    'base_asset', 'USDT_price_change_percent', 'date', 
                    'last_ID', 'count', 'rolling_traded_volume', 
                    'traded_bid_volume', 'traded_ask_volume', 'traded_price', 
                    'traded_bid_price', 'traded_ask_price', 
                    'traded_bid_ask_percent_change', 
                    'traded_bid_ask_volume_percent_change']]
            conversion_table['rolling_quote_volume'] = \
                conversion_table['rolling_traded_volume'].copy()
            if 'close' in conversion_table.columns:
                conversion_table = conversion_table.drop(columns=['close'])
            if extra_minimal:
                conversion_table = conversion_table.rename(columns={
                    'rolling_traded_volume': 'rolling_base_volume', 
                    'traded_price': 'close', 
                    'USDT_price_change_percent': 'price_change_percent'})
            else:
                conversion_table = conversion_table.rename(columns={
                    'USDT_price_change_percent': 'price_change_percent', 
                    'rolling_traded_volume': 'rolling_base_volume', 
                    'traded_bid_volume': 'bid_volume', 
                    'traded_ask_volume': 'ask_volume', 
                    'traded_price': 'close', 
                    'traded_bid_price': 'bid_price', 
                    'traded_ask_price': 'ask_price', 
                    'traded_bid_ask_percent_change': 'bid_ask_percent_change', 
                    'traded_bid_ask_volume_percent_change': 
                        'bid_ask_volume_percent_change'})
        if not as_pair:
            conversion_table['symbol'] = conversion_table['base_asset'].copy()
            conversion_table['quote_asset'] = \
                conversion_table['base_asset'].copy()
            if minimal:
                df = conversion_table[[
                    'base_asset', 'date', 'count']].groupby(by=[
                        'base_asset']).agg({'date': 'max', 'count': 'max'})
                conversion_table[['date', 'count']] = \
                    conversion_table.apply(lambda x: df.loc[x['base_asset']], 
                                           axis='columns')
                if super_extra_minimal:
                    df = conversion_table[[
                        'base_asset', 'bid_ask_percent_change', 
                        'bid_ask_volume_percent_change']].groupby(by=[
                            'base_asset']).agg({
                                'bid_ask_percent_change': 'min', 
                                'bid_ask_volume_percent_change': 'max'})
                    conversion_table.loc[:, [
                        'bid_ask_percent_change', 
                        'bid_ask_volume_percent_change']] = \
                            conversion_table.apply(
                                lambda x: df.loc[x['base_asset']], 
                                axis='columns')
            else:
                df = conversion_table[[
                    'base_asset', 'date', 'last_ID', 'count']].groupby(
                        by=['base_asset']).agg({
                            'date': 'max', 'last_ID': 'sum', 'count': 'sum'})
                conversion_table.loc[:, ['date', 'last_ID', 'count']] = \
                    conversion_table.apply(lambda x: df.loc[x['base_asset']], 
                                           axis='columns')
            conversion_table = conversion_table.drop_duplicates(
                subset=['base_asset'], keep='first')
        conversion_table = conversion_table.reset_index(drop=True)
    #conversion_table = conversion_table.drop(
    #    columns=['base_asset', 'quote_asset'])
    return conversion_table.set_index('date').sort_index(axis='index')

def get_conversion_table(client: Client, 
                         exchange_info: pd.DataFrame, 
                         offset_s: float = 0, 
                         dump_raw: bool = False, 
                         as_pair: bool = True, 
                         minimal: bool = False, 
                         extra_minimal: bool = False, 
                         super_extra_minimal: bool = False, 
                         convert_to_USDT: bool = False, 
                         shortest_paths: Optional[Dict[str, Dict[str, Dict[str, 
                                         List[Tuple[str, str]]]]]] = None) \
        -> pd.DataFrame:
    conversion_table = get_conversion_table_from_binance(
        client=client, exchange_info=exchange_info, offset_s=offset_s, 
        dump_raw=dump_raw)
    return process_conversion_table(
        conversion_table=conversion_table, exchange_info=exchange_info, 
        as_pair=as_pair, minimal=minimal, extra_minimal=extra_minimal, 
        super_extra_minimal=super_extra_minimal, 
        convert_to_USDT=convert_to_USDT, shortest_paths=shortest_paths)

def get_new_tickers(conversion_table: pd.DataFrame) -> List[str]:
    return conversion_table['symbol'].unique().tolist()

def get_tradable_tickers_info(conversion_table: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    conversion_table = conversion_table[[
        'symbol', 'close', 'price_change_percent', 'bid_price', 'ask_price', 
        'bid_volume', 'ask_volume', 'bid_ask_percent_change', 
        'bid_ask_volume_percent_change', 'rolling_base_volume', 
        'rolling_quote_volume', 'count']].copy()
    conversion_table[[
        'close', 'price_change_percent', 'bid_price', 'ask_price', 
        'bid_volume', 'ask_volume', 'bid_ask_percent_change', 
        'bid_ask_volume_percent_change', 'rolling_base_volume', 
        'rolling_quote_volume', 'count']] = \
        conversion_table[[
            'close', 'price_change_percent', 'bid_price', 'ask_price', 
            'bid_volume', 'ask_volume', 'bid_ask_percent_change', 
            'bid_ask_volume_percent_change', 'rolling_base_volume', 
            'rolling_quote_volume', 'count']].astype(float)
    conversion_table = conversion_table.sort_index(axis='index')
    conversion_table_live_filtered = \
        conversion_table[conversion_table['bid_ask_percent_change'] < 0.3]
    #conversion_table_live_filtered = conversion_table_live_filtered[
    #    conversion_table_live_filtered['bid_ask_volume_percent_change'] > 0.0]
    conversion_table_live_filtered = conversion_table_live_filtered[
        conversion_table_live_filtered['rolling_quote_volume'] > 10000000]
    conversion_table_live_filtered = conversion_table_live_filtered[
        conversion_table_live_filtered['count'] > 1000]
    return conversion_table, get_new_tickers(conversion_table_live_filtered)

def get_new_filtered_tickers(conversion_table: pd.DataFrame) -> List[str]:
    return get_tradable_tickers_info(
        conversion_table=conversion_table)[0]['symbol'].unique().tolist()
