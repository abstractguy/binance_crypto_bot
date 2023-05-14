#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/trader/order_book.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from typing import Dict, Tuple
from binance.client import Client
import pandas as pd

# Function definitions.
def get_order_book_depth(client: Client, symbol: str) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    depth = client.get_order_book(symbol=symbol, limit=5000)
    frames = {side: pd.DataFrame(data=depth[side], columns=['price', 'quantity'], dtype=float) 
              for side in ['bids', 'asks']}
    frames_list = [frames[side].assign(side=side) for side in frames]
    return frames, pd.concat(frames_list, axis='index', ignore_index=True, sort=True)

def get_order_book_trigger(client: Client, symbol: str, threshold: int = 10000) -> bool:
    frames, data = get_order_book_depth(client, symbol)
    min_prices = data.groupby('side').price.min()
    max_prices = data.groupby('side').price.max()
    #min_quantities = data.groupby('side').quantity.min()
    #max_quantities = data.groupby('side').quantity.max()
    min_bid_price = min_prices.loc['bids']
    max_bid_price = max_prices.loc['bids']
    min_ask_price = min_prices.loc['asks']
    max_ask_price = max_prices.loc['asks']
    #min_bid_quantity = min_quantities.loc['bids']
    #max_bid_quantity = max_quantities.loc['bids']
    #min_ask_quantity = min_quantities.loc['asks']
    #max_ask_quantity = max_quantities.loc['asks']
    spread = ((min_ask_price - max_bid_price) / min_ask_price) * 100
    #bid_range = ((max_bid_price - min_bid_price) / min_bid_price) * 100
    #ask_range = ((max_ask_price - min_ask_price) / min_ask_price) * 100
    bid_ask_range = ((max_ask_price - min_bid_price) / min_bid_price) * 100
    spread_trigger = spread < 0.8
    #width_trigger = ask_range > threshold
    #height_trigger = max_ask_quantity < max_bid_quantity
    bid_ask_range_trigger = bid_ask_range > threshold
    #return width_trigger and height_trigger and spread_trigger
    return spread_trigger and bid_ask_range_trigger
