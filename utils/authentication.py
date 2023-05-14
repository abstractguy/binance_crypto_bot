#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/authentication.py
# By:          Samuel Duclos
# For:         Myself
# Description: This file handles python-binance authentication.

# Library imports.
from typing import Tuple
from os.path import exists
from binance.client import Client

# Class definition.
class Cryptocurrency_authenticator:
    # Constructor.
    def __init__(self, use_keys: bool = False, testnet: bool = False, keys_path: str = 'keys.txt'):
        self.keys_path = keys_path
        api_key, secret_key = self.get_API_keys(use_keys=use_keys)
        self.spot_client = Client(api_key=api_key, api_secret=secret_key, testnet=False)

    def get_API_keys(self, use_keys: bool = True) -> Tuple[str, str]:
        if use_keys and exists(self.keys_path):
            with open(self.keys_path, 'r') as f:
                return f.readline().replace('\n', '').split(':')
        else:
            return ('', '')
