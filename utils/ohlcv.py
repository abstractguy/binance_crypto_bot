#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/ohlcv.py
# By:          Samuel Duclos
# For          Myself
# Description: Download OHLCV precomputed DataFrame from the Binance API.

# Library imports.
from binance.client import Client
from datetime import datetime
import pandas as pd

# Function definitions.
def fix_DST_bug(df: pd.DataFrame) -> pd.DataFrame:
    timeseries_size = df.shape[0]
    if timeseries_size > 4:
        mid_series = timeseries_size // 2
        frequency_1 = pd.tseries.frequencies.to_offset((df.index[-(mid_series)+1:] - df.index[-(mid_series):-1]).min())
        frequency_2 = pd.tseries.frequencies.to_offset((df.index[1:mid_series] - df.index[:(mid_series)-1]).min())
        frequency_1d = pd.tseries.frequencies.to_offset('1d')
        frequency = frequency_2 if frequency_1 < frequency_2 else frequency_1
        if frequency_1 != frequency_2:
            if (frequency_1d > frequency_1) and (frequency_1d > frequency_2):
                df.index = pd.date_range(end=df.index[-1], periods=timeseries_size, freq=frequency, name='date')
    return df

def download_pair(client: Client, 
                  symbol: str, 
                  interval: str = '1m', 
                  period: int = 60, 
                  offset_s: float = 0) -> pd.DataFrame:
    def get_n_periods_from_time(period: int = 60) -> str:
        interval_digits = int(''.join(filter(str.isdigit, interval)))
        interval_string = str(''.join(filter(str.isalpha, interval)))
        return str(interval_digits * period) + interval_string

    start_str = get_n_periods_from_time(period=period)
    data = client.get_historical_klines(symbol=symbol, interval=interval, start_str=start_str)
    data = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 
                                       'base_volume', 'close_time', 'quote_volume', 
                                       'n_trades', 'taker_buy_base_volume', 
                                       'taker_buy_quote_volume', 'ignore'])
    data['date'] = data['date'].apply(lambda timestamp: \
                                      datetime.fromtimestamp((timestamp / 1000) + int(offset_s)))

    data = data.drop(columns=['close_time', 'ignore']).set_index('date')
    data[['open', 'high', 'low', 'close', 'base_volume', 'quote_volume', 
          'taker_buy_base_volume', 'taker_buy_quote_volume']] = \
        data[['open', 'high', 'low', 'close', 'base_volume', 'quote_volume', 
              'taker_buy_base_volume', 'taker_buy_quote_volume']].applymap(
            lambda entry: entry.rstrip('0').rstrip('.'))
    data = data.astype(float)
    data['n_trades'] = data['n_trades'].astype(int)
    return fix_DST_bug(data)
