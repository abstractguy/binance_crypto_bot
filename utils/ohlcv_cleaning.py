#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/ohlcv_cleaning.py
# By:          Samuel Duclos
# For          Myself
# Description: Provides whole market OHLCV data cleaning.

# Library imports.
import pandas as pd

# Function definitions.
def clean_data(data):
    def clean_ticker(data, main_ticker, volume_columns=None, 
                     rolling_volume_columns=None):
        df = data[main_ticker].copy()
        data = data.sort_index(axis='columns')
        data = data.drop(columns=[main_ticker])
        if volume_columns is not None and len(volume_columns) > 0:
            df[volume_columns] = df[volume_columns].fillna(value=0.0)
        if rolling_volume_columns is not None and \
                len(rolling_volume_columns) > 0:
            df[rolling_volume_columns] = \
                df[rolling_volume_columns].fillna(method='pad').fillna(method='backfill')

        s = pd.concat([df['open'], df['close']])
        s = s.sort_index(kind='merge')
        s = s.fillna(method='pad')
        s = s.fillna(method='backfill')
        df['open'] = s.iloc[0::2]
        df['close'] = s.iloc[1::2]
        df.loc[df['high'].isna(),'high'] = \
            df.loc[df['high'].isna(),['open', 'high', 'low', 'close']].max(axis='columns')
        df.loc[df['low'].isna(),'low'] = \
            df.loc[df['low'].isna(),['open', 'high', 'low', 'close']].min(axis='columns')

        column_names = df.columns.tolist()
        columns = [(main_ticker, column) for column in column_names]
        df.columns = pd.MultiIndex.from_tuples(columns)
        df.columns = df.columns.set_names(['symbol', 'feature'])
        data = pd.concat([data, df], axis='columns')
        return data
    data.columns = data.columns.set_names(['symbol', 'feature'])
    columns = data.columns.tolist()
    tickers_list = data.columns.get_level_values('symbol').unique().tolist()
    features_list = data.columns.get_level_values('feature').unique().tolist()
    volume_columns = [feature for feature in features_list if feature.endswith('volume')]
    rolling_volume_columns = [feature for feature in volume_columns if feature.startswith('rolling_')]
    volume_columns = [feature for feature in volume_columns if not feature.startswith('rolling_')]
    for main_ticker in tickers_list:
        data = clean_ticker(data, main_ticker, volume_columns=volume_columns, 
                            rolling_volume_columns=rolling_volume_columns)
    #data = data.fillna(method='pad').fillna(method='backfill')
    data = data[columns]
    return data
