#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/trader/trade.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset trading.

# Library imports.
from typing import Dict, List, Optional, Tuple
from binance.client import Client
from ..conversion import make_tradable_quantity, convert_price
from ..conversion import get_shortest_pair_path_between_assets
from ..conversion import select_pair_with_highest_quote_volume_from_base_asset
from ..conversion_table import get_conversion_table
from .order_book import get_order_book_trigger
from .wallet import select_asset_with_biggest_wallet
from binance.exceptions import BinanceAPIException
from time import sleep
import paramiko
import pandas as pd

# Function definitions.
def trade_assets(client: Client, 
                 quantity: float, 
                 from_asset: str, 
                 to_asset: str, 
                 base_asset: str, 
                 quote_asset: str, 
                 conversion_table: pd.DataFrame, 
                 exchange_info: pd.DataFrame, 
                 priority: str = 'accuracy', 
                 verbose: bool = False, 
                 shortest_paths: Optional[Dict[str, Dict[str, Dict[str, List[Tuple[
                                 str, str]]]]]] = None) -> Dict[str, float]:
    pair = base_asset + quote_asset
    side = 'BUY' if from_asset != base_asset else 'SELL'
    if side == 'SELL':
        quantity = convert_price(float(quantity), from_asset=from_asset, to_asset=to_asset, 
                                 conversion_table=conversion_table, exchange_info=exchange_info, 
                                 key='close', priority=priority, shortest_path=shortest_paths)
    ticks = 0
    while True:
        try:
            if verbose:
                print(quantity)
            while True:
                quantity = make_tradable_quantity(pair, float(quantity), 
                                                  subtract=ticks, exchange_info=exchange_info)
                qty = float(quantity)
                if qty <= 0:
                    ticks = (qty // 2) + (qty // 4)
                else:
                    break
            if verbose:
                print(quantity)

            request = client.create_order(symbol=pair, side=side, type='MARKET', 
                                          quoteOrderQty=quantity, recvWindow=2000)
            break
        except BinanceAPIException as e:
            request = None
            if str(e) == 'APIError(code=-2010): Account has insufficient balance for requested action.':
                ticks = ticks * 2 if ticks != 0 else 1
            else:
                break
    if verbose:
        print('ticks:', ticks)
    return request

def trade(client: Client, 
          to_asset: str, 
          conversion_table: pd.DataFrame, 
          exchange_info: pd.DataFrame, 
          priority: str = 'accuracy', 
          verbose: bool = True, 
          shortest_paths: Optional[Dict[str, Dict[str, Dict[str, List[Tuple[
                          str, str]]]]]] = None) -> Dict[str, float]:
    from_asset, converted_quantity, quantity, priority = \
        select_asset_with_biggest_wallet(
            client=client, conversion_table=conversion_table, 
            exchange_info=exchange_info, shortest_paths=shortest_paths)
    if shortest_paths is None:
        shortest_path = \
            get_shortest_pair_path_between_assets(
                from_asset, to_asset, exchange_info=exchange_info, 
                priority=priority)
    else:
        shortest_path = shortest_paths[priority][from_asset][to_asset]
    if verbose:
        print(shortest_path)
    if from_asset == to_asset:
        print("Error: Can't trade asset with itself!\nIgnoring...")
    elif len(shortest_path) < 1:
        print("Error: A path from from_asset to to_asset does not exist!\nIgnoring...")
    else:
        for (base_asset, quote_asset) in shortest_path:
            if from_asset == base_asset:
                from_asset = base_asset
                to_asset = quote_asset
            else:
                from_asset = quote_asset
                to_asset = base_asset
            request = trade_assets(
                client=client, quantity=quantity, from_asset=from_asset, 
                to_asset=to_asset, base_asset=base_asset, 
                quote_asset=quote_asset, conversion_table=conversion_table, 
                exchange_info=exchange_info, priority=priority, verbose=False, 
                shortest_paths=shortest_paths)
            if request is None:
                return trade(client=client, to_asset=to_asset, 
                             conversion_table=conversion_table, 
                             exchange_info=exchange_info)
            quantity = request['cummulativeQuoteQty']
            from_asset = to_asset
            sleep(0.01)
        return request

def make_empty_blacklist() -> pd.DataFrame:
    return pd.DataFrame(columns=['symbol', 'base_asset', 'close', 'take_profit_count', 
                                 'stop_loss_count', 'profit_count', 'loss_count'])

def add_entry_to_blacklist(blacklist: pd.DataFrame, 
                           pair: str, 
                           conversion_table: pd.DataFrame, 
                           exchange_info: pd.DataFrame, 
                           reason: str = 'stop_loss') -> pd.DataFrame:
    base_asset_from_pair = exchange_info[exchange_info['symbol'] == pair]['base_asset'].iat[0]
    if base_asset_from_pair not in blacklist['base_asset'].tolist():
        new_blacklist_entry = conversion_table[conversion_table['symbol'] == pair][['symbol', 'close']].copy()
        new_blacklist_entry['base_asset'] = base_asset_from_pair
        new_blacklist_entry['take_profit_count'] = 0
        new_blacklist_entry['stop_loss_count'] = 0
        new_blacklist_entry['profit_count'] = 0
        new_blacklist_entry['loss_count'] = 0
        new_blacklist_entry = new_blacklist_entry[['symbol', 'base_asset', 'close', 'take_profit_count', 
                                                   'stop_loss_count', 'profit_count', 'loss_count']]
        blacklist = pd.concat([blacklist, new_blacklist_entry], axis='index')
    else:
        pair = blacklist[blacklist['base_asset'] == base_asset_from_pair]['symbol'].iat[0]
        new_blacklist_entry = conversion_table[conversion_table['symbol'] == pair][['symbol', 'close']].copy()
        new_blacklist_entry['base_asset'] = base_asset_from_pair
        new_blacklist_entry['take_profit_count'] = \
            blacklist[blacklist['base_asset'] == base_asset_from_pair]['take_profit_count'].iat[0]
        new_blacklist_entry['stop_loss_count'] = \
            blacklist[blacklist['base_asset'] == base_asset_from_pair]['stop_loss_count'].iat[0]
        new_blacklist_entry['profit_count'] = \
            blacklist[blacklist['base_asset'] == base_asset_from_pair]['profit_count'].iat[0]
        new_blacklist_entry['loss_count'] = \
            blacklist[blacklist['base_asset'] == base_asset_from_pair]['loss_count'].iat[0]
        new_blacklist_entry = new_blacklist_entry[['symbol', 'base_asset', 'close', 'take_profit_count', 
                                                   'stop_loss_count', 'profit_count', 'loss_count']]
        blacklist = pd.concat([blacklist, new_blacklist_entry], axis='index')
        blacklist = blacklist.drop_duplicates(subset=['base_asset'], keep='last')
    pair = blacklist[blacklist['base_asset'] == base_asset_from_pair]['symbol'].iat[0]
    if reason == 'take_profit':
        blacklist.loc[blacklist['symbol'] == pair,'take_profit_count'] += 1
    if reason == 'stop_loss':
        blacklist.loc[blacklist['symbol'] == pair,'stop_loss_count'] += 1
    if reason == 'profit':
        blacklist.loc[blacklist['symbol'] == pair,'profit_count'] += 1
    if reason == 'loss':
        blacklist.loc[blacklist['symbol'] == pair,'loss_count'] += 1
    return blacklist

def check_if_asset_from_pair_is_buyable(blacklist: pd.DataFrame, 
                                        pair: str, 
                                        exchange_info: pd.DataFrame, 
                                        take_profit: Optional[float] = None, 
                                        stop_loss: Optional[float] = None, 
                                        profit: Optional[float] = None, 
                                        loss: Optional[float] = None, 
                                        take_profit_count: int = 2, 
                                        stop_loss_count: int = 1, 
                                        profit_count: int = 2, 
                                        loss_count: int = 1) -> bool:
    base_asset_from_pair = exchange_info[exchange_info['symbol'] == pair]['base_asset'].iat[0]
    is_buyable = True
    if base_asset_from_pair in blacklist['base_asset'].tolist():
        pair = blacklist[blacklist['base_asset'] == base_asset_from_pair]['symbol'].iat[0]
        if take_profit is not None:
            if blacklist.loc[blacklist['symbol'] == pair,'take_profit_count'].iat[0] >= take_profit_count:
                is_buyable = False
        if stop_loss is not None:
            if blacklist.loc[blacklist['symbol'] == pair,'stop_loss_count'].iat[0] >= stop_loss_count:
                is_buyable = False
        if profit is not None:
            if blacklist.loc[blacklist['symbol'] == pair,'profit_count'].iat[0] >= profit_count:
                is_buyable = False
        if loss is not None:
            if blacklist.loc[blacklist['symbol'] == pair,'loss_count'].iat[0] >= loss_count:
                is_buyable = False
    return is_buyable

def check_take_profit_and_stop_loss(blacklist: pd.DataFrame, 
                                    from_asset: str, 
                                    to_asset: str, 
                                    conversion_table: pd.DataFrame, 
                                    exchange_info: pd.DataFrame, 
                                    latest_asset: str, 
                                    take_profit: Optional[float] = None, 
                                    stop_loss: Optional[float] = None) -> Tuple[pd.DataFrame, str]:
    if from_asset in blacklist['base_asset'].tolist():
        pair = blacklist[blacklist['base_asset'] == from_asset]['symbol'].iat[0]
        purchased_price = blacklist[blacklist['base_asset'] == from_asset]['close'].iat[0]
        price_now = conversion_table[conversion_table['symbol'] == pair]['close'].iat[0]
        percent_gain = ((price_now - purchased_price) / purchased_price) * 100.0
        if take_profit is not None:
            if percent_gain >= take_profit:
                to_asset = latest_asset
                blacklist = add_entry_to_blacklist(
                    blacklist, pair, conversion_table, exchange_info, reason='take_profit')
        if stop_loss is not None:
            if percent_gain <= -stop_loss:
                to_asset = latest_asset
                blacklist = add_entry_to_blacklist(
                    blacklist, pair, conversion_table, exchange_info, reason='stop_loss')
    return blacklist, to_asset

def check_profit_and_loss(blacklist: pd.DataFrame, 
                          from_asset: str, 
                          to_asset: str, 
                          conversion_table: pd.DataFrame, 
                          exchange_info: pd.DataFrame, 
                          latest_asset: str, 
                          profit: Optional[float] = None, 
                          loss: Optional[float] = None) -> Tuple[pd.DataFrame, str]:
    if from_asset in blacklist['base_asset'].tolist():
        pair = blacklist[blacklist['base_asset'] == from_asset]['symbol'].iat[0]
        purchased_price = blacklist[blacklist['base_asset'] == from_asset]['close'].iat[0]
        price_now = conversion_table[conversion_table['symbol'] == pair]['close'].iat[0]
        is_gain = price_now > purchased_price
        if profit is not None:
            if is_gain:
                to_asset = latest_asset
                blacklist = add_entry_to_blacklist(
                    blacklist, pair, conversion_table, exchange_info, reason='profit')
        if loss is not None:
            if not is_gain:
                to_asset = latest_asset
                blacklist = add_entry_to_blacklist(
                    blacklist, pair, conversion_table, exchange_info, reason='loss')
    return blacklist, to_asset

def remove_older_entries_in_blacklist(blacklist: pd.DataFrame, frequency: str = '15min') -> pd.DataFrame:
    frequency = pd.tseries.frequencies.to_offset(frequency)
    return blacklist.loc[(pd.Timestamp.utcnow().tz_localize(None) - blacklist.index) < frequency]

def choose_to_asset(ssh: paramiko.SSHClient, 
                    blacklist: pd.DataFrame, 
                    sell_asset: str, 
                    from_asset: str, 
                    to_asset: str, 
                    latest_asset: str, 
                    take_profit: Optional[float], 
                    stop_loss: Optional[float], 
                    profit: Optional[float], 
                    loss: Optional[float], 
                    take_profit_count: int, 
                    stop_loss_count: int, 
                    profit_count: int, 
                    loss_count: int, 
                    conversion_table: pd.DataFrame, 
                    exchange_info: pd.DataFrame, 
                    output_log_screened: str = 'output_log_screened.txt') -> Tuple[str, str]:
    tradable_pairs = ssh.get_logs_from_server(
        server_log=ssh.output_log_screened)
    if tradable_pairs is None:
        to_asset = sell_asset
    else:
        print('.', end='')
        tradable_pairs = tradable_pairs.sort_values(
            by='last_price_move', ascending=False)
        tradable_assets = list(set(tradable_pairs['symbol'].tolist()))
        if from_asset in tradable_assets:
            to_asset = latest_asset = from_asset
        else:
            is_buyable = False
            for test_asset in tradable_assets:
                test_pair = \
                    select_pair_with_highest_quote_volume_from_base_asset(
                        base_asset=test_asset, 
                        conversion_table=conversion_table, 
                        exchange_info=exchange_info)
                sleep(0.1)
                if check_if_asset_from_pair_is_buyable(
                    blacklist, test_pair, exchange_info, take_profit, 
                    stop_loss, profit, loss, take_profit_count, 
                    stop_loss_count, profit_count, loss_count):
                    #if get_order_book_trigger(
                    #    client=client, symbol=test_pair, threshold=10000):
                    latest_asset = test_asset
                    is_buyable = True
                    break
            to_asset = latest_asset if is_buyable else sell_asset
    return latest_asset, to_asset

def trade_conditionally(ssh: paramiko.SSHClient, 
                        blacklist: pd.DataFrame, 
                        client: Client, 
                        exchange_info: pd.DataFrame, 
                        to_asset: str, 
                        latest_asset: str, 
                        sell_asset: str, 
                        profit: Optional[float], 
                        loss: Optional[float], 
                        offset_s: float, 
                        shortest_paths: Optional[Dict[str, Dict[str, Dict[
                                        str, List[Tuple[str, str]]]]]] = None):
    #conversion_table = ssh.get_logs_from_server(server_log=ssh.input_log)
    conversion_table = get_conversion_table(
        client=client, exchange_info=exchange_info, offset_s=offset_s, 
        dump_raw=False, as_pair=True, minimal=False, extra_minimal=False, 
        super_extra_minimal=False, convert_to_USDT=False, 
        shortest_paths=shortest_paths)
    from_asset, converted_quantity, quantity, priority = \
        select_asset_with_biggest_wallet(
            client=client, conversion_table=conversion_table, 
            exchange_info=exchange_info, shortest_paths=shortest_paths)
    request = trade(
        client=client, to_asset=to_asset, conversion_table=conversion_table, 
        exchange_info=exchange_info, priority=priority)
    if request is not None:
        if to_asset != sell_asset:
            pair = select_pair_with_highest_quote_volume_from_base_asset(
                to_asset, conversion_table, exchange_info)
            blacklist = add_entry_to_blacklist(
                blacklist, pair, conversion_table, exchange_info, reason=None)
            base_asset_from_pair = exchange_info[
                exchange_info['symbol'] == pair]['base_asset'].iat[0]
            pair = blacklist[blacklist['base_asset'] == base_asset_from_pair][
                'symbol'].iat[0]
            blacklist.loc[blacklist['symbol'] == pair,'symbol'] = \
                request['symbol']
            blacklist.loc[blacklist['symbol'] == pair,'close'] = \
                float(request['fills'][0]['price'])
            blacklist, to_asset, check_profit_and_loss(
                blacklist, from_asset, to_asset, conversion_table, 
                exchange_info, latest_asset, profit=profit, loss=loss)
        from_asset = to_asset
    return blacklist, from_asset, to_asset
