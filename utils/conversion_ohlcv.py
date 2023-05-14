#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/data/download/binance/conversion_ohlcv.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset conversion.

# Library imports.
from .conversion import get_assets_from_pair, get_base_asset_from_pair
from .conversion import get_quote_asset_from_pair, get_shortest_pair_path_between_assets
from .ohlcvs import named_pairs_to_df
from .ohlcv_cleaning import clean_data
from tqdm import tqdm
import pandas as pd

# Function definitions.
'''

def convert_ohlcv(from_asset: str, to_asset: str, conversion_table: pd.DataFrame, frame: pd.DataFrame):
    if not isinstance(conversion_table, pd.DataFrame):
        raise ValueError("'conversion_table' must be a pd.DataFrame.")
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("'frame' must be a pd.DataFrame.")

    if not isinstance(from_asset, str) or not isinstance(to_asset, str):
        raise ValueError("'from_asset' and 'to_asset' must be of type str.")

    if not isinstance(conversion_table.index, pd.DatetimeIndex):
        raise ValueError("'conversion_table.index' must be a pd.DatetimeIndex.")

    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError("'frame.index' must be a pd.DatetimeIndex.")

    if not isinstance(conversion_table.columns, pd.MultiIndex):
        raise ValueError("'conversion_table.columns' must be a pd.MultiIndex.")

    if not isinstance(frame.columns, pd.MultiIndex):
        raise ValueError("'frame.columns' must be a pd.MultiIndex.")

    # Ensure that conversion_table is a 2-level MultiIndex.
    if len(conversion_table.columns.levels) != 2:
        raise ValueError("'conversion_table' must be a 2-level MultiIndex.")

    # Ensure that frame is a 2-level MultiIndex.
    if len(frame.columns.levels) != 2:
        raise ValueError("'frame' must be a 2-level MultiIndex.")

    # Ensure that conversion_table.columns.codes[0] is not a duplicate.
    if len(set(conversion_table.columns.codes[0])) != len(conversion_table.columns.codes[0]):
        raise ValueError("'conversion_table' must not have duplicate columns.")
    
    # Ensure that frame.columns.codes[0] is not a duplicate.
    if len(set(frame.columns.codes[0])) != len(frame.columns.codes[0]):
        raise ValueError("'frame' must not have duplicate columns.")

    # Ensure that conversion_table.columns.codes[1] is not a duplicate.
    if len(set(conversion_table.columns.codes[1])) != len(conversion_table.columns.codes[1]):
        raise ValueError("'conversion_table' must not have duplicate columns.")

    # Ensure that frame.columns.codes[1] is not a duplicate.
    if len(set(frame.columns.codes[1])) != len(frame.columns.codes[1]):
        raise ValueError("'frame' must not have duplicate columns.")

    # Ensure that conversion_table.index.codes[0] is not a duplicate.
    if len(set(conversion_table.index.codes[0])) != len(conversion_table.index.codes[0]):
        raise ValueError("'conversion_table' must not have duplicate indices.")

    # Ensure that frame.index.codes[0] is not a duplicate.
    if len(set(frame.index.codes[0])) != len(frame.index.codes[0]):
        raise ValueError("'frame' must not have duplicate indices.")

    # Ensure that conversion_table.index.codes[1] is not a duplicate.
    if len(set(conversion_table.index.codes[1])) != len(conversion_table.index.codes[1]):
        raise ValueError("'conversion_table' must not have duplicate indices.")

    # Ensure that conversion_table.columns.codes[0] is not a duplicate.
    if len(set(frame.index.codes[1])) != len(frame.index.codes[1]):
        raise ValueError("'frame' must not have duplicate indices.")

    # Create the converter and save it in the table.
    converter = lambda x: convert_ohlcv_prices(
        from_asset=from_asset, to_asset=to_asset, conversion_table=conversion_table, frame = x)
    return frame.groupby(level=0).apply(converter)
def convert_ohlcv(from_asset, to_asset, conversion_table, exchange_info, shortest_paths=None):
    if shortest_paths is None:
        shortest_path = \
            get_shortest_pair_path_between_assets(
                from_asset, to_asset, exchange_info=exchange_info, 
                priority=priority)
    else:
        shortest_path = shortest_paths[priority][from_asset][to_asset]
    base_asset, quote_asset = shortest_path[0]
    to_asset = quote_asset if from_asset == base_asset else base_asset
    pair = base_asset + quote_asset
    size = conversion_table[pair].copy()
    size['quote_volume'] = size['quote_volume'] / size['close']
    for (base_asset, quote_asset) in shortest_path[1:]:
        to_asset = quote_asset if from_asset == base_asset else base_asset
        pair = base_asset + quote_asset
        connection = conversion_table[pair]
        if base_asset == from_asset:
            size['open'] = size['open'] * connection['open']
            size['high'] = size['close'] * connection['high']
            size['low'] = size['close'] * connection['low']
            size['close'] = size['close'] * connection['close']
        else:
            size['open'] = size['open'] / connection['open']
            size['high'] = size['close'] / connection['high']
            size['low'] = size['close'] / connection['low']
            size['close'] = size['close'] / connection['close']
        from_asset = to_asset
    size['base_volume'] = size['close'] * size['base_volume']
    size['quote_volume'] = size['close'] * size['quote_volume']
    size.replace([float('inf'), float('-inf')], float('nan'), inplace=True)
    size.loc[:, ['base_volume', 'quote_volume']] = \
        size.loc[:, ['base_volume', 'quote_volume']].fillna(0)
    return size.fillna(method='pad')
'''

def convert_ohlcvs(to_asset, conversion_table, exchange_info, shortest_paths=None):
    def convert_ohlcv_prices(from_asset, to_asset, conversion_table, exchange_info, shortest_paths=None):
        if shortest_paths is None:
            shortest_path = get_shortest_pair_path_between_assets(from_asset=from_asset, 
                                                                  to_asset=to_asset, 
                                                                  exchange_info=exchange_info, 
                                                                  priority='accuracy')
        else:
            shortest_path = shortest_paths['accuracy'][from_asset][to_asset]
        base_asset, quote_asset = shortest_path[0]
        to_asset = quote_asset if from_asset == base_asset else base_asset
        symbol = base_asset + quote_asset
        size = conversion_table[symbol].copy()
        for (base_asset, quote_asset) in shortest_path[1:]:
            to_asset = quote_asset if from_asset == base_asset else base_asset
            symbol = base_asset + quote_asset
            connection = conversion_table[symbol]
            if base_asset == from_asset:
                size['open'] = size['open'] * connection['open']
                size['high'] = size['close'] * connection['high']
                size['low'] = size['close'] * connection['low']
                size['close'] = size['close'] * connection['close']
            else:
                size['open'] = size['open'] / connection['open']
                size['high'] = size['close'] / connection['high']
                size['low'] = size['close'] / connection['low']
                size['close'] = size['close'] / connection['close']
            from_asset = to_asset
        return size
    def convert_ohlcv_volumes(symbol, price_conversion_table, 
                              volume_conversion_table, exchange_info):
        from_asset = get_base_asset_from_pair(symbol, exchange_info)
        price_size = price_conversion_table[symbol].copy()
        volume_size = volume_conversion_table[symbol].copy()
        volume_size['quote_volume'] = volume_size['quote_volume'] / volume_size['close']
        price_size['base_volume'] = price_size['close'] * volume_size['base_volume']
        price_size['quote_volume'] = price_size['close'] * volume_size['quote_volume']
        price_size.replace([float('inf'), float('-inf')], float('nan'), inplace=True)
        #price_size.loc[:, ['base_volume', 'quote_volume']] = \
        #    price_size.loc[:, ['base_volume', 'quote_volume']].fillna(0)
        #return price_size.fillna(method='pad')
        return price_size
    def convert_ohlcv_prices_helper(symbol, size, shortest_paths=None):
        from_asset = get_base_asset_from_pair(symbol, exchange_info)
        if from_asset == to_asset:
            size = size[symbol].copy()
        else:
            size = convert_ohlcv_prices(
                from_asset, to_asset, size, exchange_info, shortest_paths=shortest_paths)
        return size
    volume_conversion_table = conversion_table.astype(float).copy()
    price_conversion_table = conversion_table.astype(float).copy()
    symbols = volume_conversion_table.columns.get_level_values(0).unique().tolist()
    price_conversion_table = [convert_ohlcv_prices_helper(symbol, 
                                                          price_conversion_table, 
                                                          shortest_paths=shortest_paths) 
                              for symbol in tqdm(symbols, unit=' pair conversion')]
    price_conversion_table = named_pairs_to_df(symbols, price_conversion_table)
    volume_conversion_table = [convert_ohlcv_volumes(symbol, 
                                                     price_conversion_table, 
                                                     volume_conversion_table, 
                                                     exchange_info) 
                               for symbol in tqdm(symbols, unit=' pair conversion')]
    volume_conversion_table = named_pairs_to_df(symbols, volume_conversion_table)
    volume_conversion_table = clean_data(volume_conversion_table)
    return volume_conversion_table

def convert_ohlcvs_from_pairs_to_assets(conversion_table, exchange_info, shortest_paths=None):
    # Statically-typed python function.
    def add_base_asset_level_to_pairs(df, exchange_info):
        # Statically-typed python function.
        def named_pairs_to_5dim_df(symbols, pairs):
            df = pd.DataFrame()
            column_names = pairs[0].columns.tolist()
            for (symbol, pair) in tqdm(zip(symbols, pairs), unit=' named pair'):
                columns = [('not_inverted', get_base_asset_from_pair(symbol, exchange_info), 
                            symbol, column) for column in column_names]
                pair.columns = pd.MultiIndex.from_tuples(
                    columns, names=['is_inverted', 'asset', 'symbol', 'feature']
                )
                df = pd.concat([df, pair], axis='columns')
            return df
        df = df.astype(float).copy()
        symbols = df.columns.get_level_values(0).unique().tolist()
        df = [df[symbol] for symbol in tqdm(symbols, unit=' pair')]
        return named_pairs_to_5dim_df(symbols, df)
    # Statically-typed python.
    def add_quote_asset_level_to_pairs_and_reverse(df, exchange_info):
        # Statically-typed python.
        def invert_symbol(symbol, exchange_info):
            base_asset, quote_asset = get_assets_from_pair(symbol, exchange_info)
            return quote_asset + base_asset
        # Statically-typed python.
        def named_pairs_to_5dim_df(symbols, pairs):
            df = pd.DataFrame()
            column_names = pairs[0].columns.tolist()
            for (symbol, pair) in tqdm(zip(symbols, pairs), unit=' named pair'):
                columns = [('inverted', get_quote_asset_from_pair(symbol, exchange_info), 
                            invert_symbol(symbol, exchange_info), column) 
                           for column in column_names]
                pair.columns = pd.MultiIndex.from_tuples(
                    columns, names=['is_inverted', 'asset', 'symbol', 'feature']
                )
                df = pd.concat([df, pair], axis='columns')
            return df
        df = df.astype(float).copy()
        symbols = df.columns.get_level_values(0).unique().tolist()
        df = [df[symbol] for symbol in tqdm(symbols, unit=' pair')]
        return named_pairs_to_5dim_df(symbols, df)
    # Statically-typed python.
    def invert_pairs(conversion_table, exchange_info):
        # Statically-typed python.
        def invert_symbol(symbol, exchange_info):
            base_asset, quote_asset = get_assets_from_pair(symbol, exchange_info)
            return quote_asset + base_asset
        conversion_table_swapped = conversion_table.copy()
        conversion_table_swapped.columns = \
            conversion_table_swapped.columns.swaplevel(0, 1)
        conversion_table_swapped.loc[:, ['open', 'high', 'low', 'close', 
                                         'base_volume', 'quote_volume']] = \
            conversion_table_swapped.loc[:, ['open', 'high', 'low', 'close', 
                                             'quote_volume', 'base_volume']].values
        conversion_table_swapped.loc[:, ['open', 'high', 'low', 'close']] = \
            1 / conversion_table_swapped.loc[:, ['open', 'high', 'low', 'close']]
        conversion_table_swapped.columns = \
            conversion_table_swapped.columns.swaplevel(0, 1)
        conversion_table_swapped = conversion_table_swapped.astype(float).copy()
        symbols = conversion_table_swapped.columns.get_level_values(0).unique().tolist()
        return add_quote_asset_level_to_pairs_and_reverse(conversion_table_swapped, 
                                                          exchange_info)
    to_asset = 'USDT'
    conversion_table = convert_ohlcvs(
        to_asset, conversion_table, exchange_info, shortest_paths=shortest_paths)
    conversion_table_swapped = invert_pairs(conversion_table, exchange_info)
    conversion_table = add_base_asset_level_to_pairs(conversion_table, exchange_info)
    conversion_table_mixed = pd.concat([conversion_table, conversion_table_swapped], 
                                       join='outer', axis='columns')
    conversion_table_mixed = conversion_table_mixed.sort_index(axis='columns')
    conversion_table_mixed.columns = conversion_table_mixed.columns.swaplevel(0, 3)
    conversion_table_mixed = conversion_table_mixed[['open', 'high', 'low', 'close', 
                                                     'base_volume', 'quote_volume']]
    conversion_table_mixed.columns = conversion_table_mixed.columns.swaplevel(0, 3)
    conversion_table_mixed = conversion_table_mixed[['not_inverted', 'inverted']]
    conversion_table_mixed.columns = conversion_table_mixed.columns.swaplevel(0, 3)
    conversion_table_mixed.columns = conversion_table_mixed.columns.swaplevel(0, 1)
    conversion_table_mixed.columns = conversion_table_mixed.columns.swaplevel(1, 2)
    assets = conversion_table_mixed.columns.get_level_values(0).unique().tolist()
    new_columns = []
    for asset in tqdm(assets, unit=' asset'):
        symbols = conversion_table_mixed[asset].columns.get_level_values(0)
        trading_base_volume = \
            conversion_table_mixed.loc[:, (asset, slice(None), 'base_volume')].sum(axis='columns')
        trading_quote_volume = \
            conversion_table_mixed.loc[:, (asset, slice(None), 'quote_volume')].sum(axis='columns')
        new_columns.append(symbols[0])
        for symbol in symbols:
            # Fix this warning (PerformanceWarning: indexing past lexsort depth may impact performance).
            conversion_table_mixed.loc[:, (asset, symbol, 'base_volume')] = trading_base_volume
            conversion_table_mixed.loc[:, (asset, symbol, 'quote_volume')] = trading_quote_volume
    conversion_table_mixed.columns = conversion_table_mixed.columns.swaplevel(0, 1)
    conversion_table_mixed = conversion_table_mixed[new_columns]
    conversion_table_mixed.columns = conversion_table_mixed.columns.swaplevel(0, 3)
    conversion_table_mixed.columns = conversion_table_mixed.columns.droplevel(3)
    conversion_table_mixed = conversion_table_mixed['not_inverted']
    conversion_table_mixed.columns.names = ['symbol', 'feature']
    return conversion_table_mixed
