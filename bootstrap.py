#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        bootstrap.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from typing import List, Optional
from binance.client import Client
from utils.authentication import Cryptocurrency_authenticator
from utils.exchange import Cryptocurrency_exchange
from utils.conversion import get_timezone_offset_in_seconds
from utils.conversion import precompute_shortest_paths
from utils.conversion_table import get_conversion_table, get_new_tickers
from utils.ohlcvs import download_pairs_bootstrapped
from utils.bootstrap import bootstrap_loggers
import os
import shutil
import threading
import pandas as pd

shortest_paths = None
def precompute_shortest_paths_thread(
    client: Client, assets: List[str], offset_s: Optional[float] = 0) \
        -> List[pd.DataFrame]:
    global shortest_paths
    print('Started precompute_shortest_paths thread.')
    shortest_paths = precompute_shortest_paths(
        exchange_info, priority=None, 
        shortest_paths_file='crypto_logs/shortest_paths.pkl')
    print('Finished precompute_shortest_paths thread.')

#downloaded_pairs_1d = None
#def download_pairs_1d(
#    client: Client, assets: List[str], offset_s: Optional[float] = 0) \
#        -> List[pd.DataFrame]:
#    global downloaded_pairs_1d
#    print('Started downloaded_pairs_1d thread.')
#    downloaded_pairs_1d = download_pairs_bootstrapped(
#        client=client, assets=assets, interval='1d', 
#        offset_s=offset_s)
#    print('Finished downloaded_pairs_1d thread.')

#downloaded_pairs_1h = None
#def download_pairs_1h(
#    client: Client, assets: List[str], offset_s: Optional[float] = 0) \
#        -> List[pd.DataFrame]:
#    global downloaded_pairs_1h
#    print('Started downloaded_pairs_1h thread.')
#    downloaded_pairs_1h = download_pairs_bootstrapped(
#        client=client, assets=assets, interval='1h', 
#        offset_s=offset_s)
#    print('Finished downloaded_pairs_1h thread.')

downloaded_pairs_1min = None
def download_pairs_1min(
    client: Client, assets: List[str], offset_s: Optional[float] = 0) \
        -> List[pd.DataFrame]:
    global downloaded_pairs_1min
    print('Started downloaded_pairs_1min thread.')
    downloaded_pairs_1min = download_pairs_bootstrapped(
        client=client, assets=assets, interval='1m', 
        offset_s=offset_s)
    print('Finished downloaded_pairs_1min thread.')

def main():
    global shortest_paths
    #global downloaded_pairs_1d
    #global downloaded_pairs_1h
    global downloaded_pairs_1min
    as_pair = False
    directory = 'crypto_logs'
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
    client = authenticator.spot_client
    exchange = Cryptocurrency_exchange(client=client, directory=directory)
    exchange_info = exchange.info
    offset_s = get_timezone_offset_in_seconds()
    conversion_table = get_conversion_table(
        client=client, exchange_info=exchange_info, offset_s=offset_s, 
        dump_raw=False, as_pair=True, minimal=False, extra_minimal=False, 
        convert_to_USDT=True, shortest_paths=None)
    assets = get_new_tickers(conversion_table=conversion_table)

    shortest_paths_file = 'crypto_logs/shortest_paths.pkl'
    if os.path.exists(shortest_paths_file):
        shortest_paths_thread_started = False
        shortest_paths = precompute_shortest_paths(
            exchange_info, None, shortest_paths_file)
    else:
        shortest_paths_thread_started = True
        shortest_paths_thread = threading.Thread(
            target=precompute_shortest_paths, 
            args=(exchange_info, None, shortest_paths_file))
        shortest_paths_thread.start()

    #download_1d = threading.Thread(target=download_pairs_1h, 
    #    args=(client, assets, offset_s))
    #download_1d.start()

    #download_1h = threading.Thread(target=download_pairs_1h, 
    #    args=(client, assets, offset_s))
    #download_1h.start()

    download_1min = threading.Thread(target=download_pairs_1min, 
        args=(client, assets, offset_s))
    download_1min.start()

    #download_1d.join()
    #if shortest_paths_thread_started:
    #    shortest_paths_thread.join()
    #pairs_1d = bootstrap_loggers(
    #    client=client, assets=downloaded_pairs_1d, additional_intervals=None, 
    #    upsampled_intervals=None, pairs={}, download_interval='1d', 
    #    exchange_info=exchange_info, as_pair=as_pair, 
    #    shortest_paths=shortest_paths)

    #download_1h.join()
    #if shortest_paths_thread_started:
    #    shortest_paths_thread.join()
    #pairs_1h = bootstrap_loggers(
    #    client=client, assets=downloaded_pairs_1h, additional_intervals=None, 
    #    upsampled_intervals=None, pairs=pairs_1d, download_interval='1d', 
    #    exchange_info=exchange_info, as_pair=as_pair, 
    #    shortest_paths=shortest_paths)

    download_1min.join()
    if shortest_paths_thread_started:
        shortest_paths_thread.join()
    #pairs_1min = bootstrap_loggers(
    #    client=client, assets=downloaded_pairs_1min, 
    #    additional_intervals=['30min'], upsampled_intervals=['5s', '15s'], 
    #    pairs=pairs_1h, download_interval='1m', exchange_info=exchange_info, 
    #    as_pair=as_pair, shortest_paths=shortest_paths)
    pairs_1min = bootstrap_loggers(
        client=client, assets=downloaded_pairs_1min, 
        additional_intervals=['30min'], upsampled_intervals=['5s', '15s'], 
        pairs={}, download_interval='1m', exchange_info=exchange_info, 
        as_pair=as_pair, shortest_paths=shortest_paths)

    print('Bootstrapping done!')

if __name__ == '__main__':
    main()
