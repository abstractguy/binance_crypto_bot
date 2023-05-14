#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/trader/wallet.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset trading.

# Library imports.
from typing import Dict, List, Tuple, Optional, Union
from binance.client import Client
from utils.conversion import convert_price
import pandas as pd

# Function definitions.
def select_asset_with_biggest_wallet(
    client: Client, conversion_table: pd.DataFrame, 
    exchange_info: pd.DataFrame, 
    shortest_paths: Optional[Dict[str, Dict[str, Dict[str, List[Tuple[
                    str, str]]]]]] = None) \
        -> Tuple[str, Union[str, float], Union[str, float], str]:
    def get_account_balances() -> pd.DataFrame:
        balances = pd.DataFrame(client.get_account()['balances'])[[
            'asset', 'free']]
        balances = balances.set_index('asset').astype(float)
        balances = balances[balances['free'] > 0]
        return balances.sort_values(by=['free'], ascending=False).T
    account_balances = get_account_balances()
    ls = []
    for (asset, quantity) in account_balances.items():
        quantity = quantity.iat[0]
        converted_quantity = convert_price(
            size=quantity, from_asset=asset, to_asset='USDT', 
            conversion_table=conversion_table, 
            exchange_info=exchange_info, key='close', 
            priority='accuracy', shortest_path=shortest_paths)
        ls.append((asset, converted_quantity, quantity))
    from_asset, converted_quantity, quantity = \
        sorted(ls, key=lambda x: float(x[1]), reverse=True)[0]
    priority = 'fees' if float(converted_quantity) > 10.0 else 'wallet'
    return from_asset, converted_quantity, quantity, priority
