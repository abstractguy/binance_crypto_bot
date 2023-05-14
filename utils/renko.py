#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/renko.py
# By:          Samuel Duclos
# For:         Myself
# Description: This file handles the Renko technical indicator and trigger.

# Library imports.
from scipy.stats import iqr
import math
import numpy as np
import pandas as pd
import scipy.optimize as opt
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import talib

# Class definition.
class Renko:
    def __init__(self):
        self.source_prices = []
        self.renko_prices = []
        self.renko_directions = []

    # Setting brick size. Auto mode is preferred, it uses history
    def set_brick_size(self, HLC_history=None, auto=True, brick_size=10.0):
        if auto == True:
            self.brick_size = self.__get_optimal_brick_size(HLC_history.iloc[:, [0, 1, 2]])
        else:
            self.brick_size = brick_size
        return self.brick_size

    def __renko_rule(self, last_price):
        # Get the gap between two prices
        gap_div = int(float(last_price - self.renko_prices[-1]) / self.brick_size)
        is_new_brick = False
        start_brick = 0
        num_new_bars = 0

        # When we have some gap in prices
        if gap_div != 0:
            # Forward any direction (up or down)
            if (gap_div > 0 and (self.renko_directions[-1] > 0 or self.renko_directions[-1] == 0)) or (gap_div < 0 and (self.renko_directions[-1] < 0 or self.renko_directions[-1] == 0)):
                num_new_bars = gap_div
                is_new_brick = True
                start_brick = 0
            # Backward direction (up -> down or down -> up)
            elif np.abs(gap_div) >= 2: # Should be double gap at least
                num_new_bars = gap_div
                num_new_bars -= np.sign(gap_div)
                start_brick = 2
                is_new_brick = True
                self.renko_prices.append(self.renko_prices[-1] + 2 * self.brick_size * np.sign(gap_div))
                self.renko_directions.append(np.sign(gap_div))
            #else:
                #num_new_bars = 0

            if is_new_brick:
                # Add each brick-
                for d in range(start_brick, np.abs(gap_div)):
                    self.renko_prices.append(self.renko_prices[-1] + self.brick_size * np.sign(gap_div))
                    self.renko_directions.append(np.sign(gap_div))

        return num_new_bars

    # Getting renko on history
    def build_history(self, prices):
        if len(prices) > 0:
            # Init by start values
            self.source_prices = prices
            self.timed_renko_prices = []
            self.timed_renko_prices.append(prices.iloc[0])
            self.renko_prices.append(prices.iloc[0])
            self.renko_directions.append(0)

            # For each price in history
            for p in self.source_prices[1:]:
                self.__renko_rule(p)
                self.timed_renko_prices.append(self.renko_prices[-1].copy())

        return len(self.renko_prices)

    # Getting next renko value for last price
    def do_next(self, last_price):
        if len(self.renko_prices) == 0:
            self.source_prices.append(last_price)
            self.renko_prices.append(last_price)
            self.renko_directions.append(0)
            return 1
        else:
            self.source_prices.append(last_price)
            return self.__renko_rule(last_price)

    # Simple method to get optimal brick size based on ATR
    def __get_optimal_brick_size(self, HLC_history, atr_timeperiod=9):
        brick_size = 0.0

        # If we have enough of data
        if HLC_history.shape[0] > atr_timeperiod:
            brick_size = np.median(talib.ATR(high=np.double(HLC_history.iloc[:,0]), 
                                             low=np.double(HLC_history.iloc[:,1]), 
                                             close=np.double(HLC_history.iloc[:,2]), 
                                             timeperiod=atr_timeperiod)[atr_timeperiod:])

        return brick_size

    def evaluate(self, method = 'simple'):
        balance = sign_changes = 0
        price_ratio = len(self.source_prices) / len(self.renko_prices)

        if method == 'simple':
            for i in range(2, len(self.renko_directions)):
                if self.renko_directions[i] == self.renko_directions[i - 1]:
                    balance += 1
                else:
                    balance -= 2
                    sign_changes = sign_changes + 1

            if sign_changes == 0:
                sign_changes = 1

            score = balance / sign_changes
            if score >= 0 and price_ratio >= 1:
                score = np.log(score + 1) * np.log(price_ratio)
            else:
                score = -1.0

            return {'balance': balance, 'sign_changes:': sign_changes, 
                    'price_ratio': price_ratio, 'score': score}

    def get_renko_prices(self):
        return self.renko_prices

    def get_renko_directions(self):
        return self.renko_directions

    def plot_renko(self, col_up='g', col_down='r'):
        fig, ax = plt.subplots(1, figsize=(20, 10))
        ax.set_title('Renko chart')
        ax.set_xlabel('Renko bars')
        ax.set_ylabel('Price')

        # Calculate the limits of axes
        ax.set_xlim(0.0, len(self.renko_prices) + 1.0)
        ax.set_ylim(np.min(self.renko_prices) - 3.0 * self.brick_size, 
                    np.max(self.renko_prices) + 3.0 * self.brick_size)

        # Plot each renko bar
        for i in range(1, len(self.renko_prices)):
            # Set basic params for patch rectangle
            col = col_up if self.renko_directions[i] == 1 else col_down
            x = i
            y = self.renko_prices[i] - self.brick_size if self.renko_directions[i] == 1 else self.renko_prices[i]
            height = self.brick_size

            # Draw bar with params
            ax.add_patch(
                patches.Rectangle(
                    (x, y),   # (x,y)
                    1.0,     # width
                    self.brick_size, # height
                    facecolor = col
                )
            )

        plt.show()

# Function definitions.
def get_renko_trigger(data, compress=False, direction_type='long', trigger_type='simple', method='brent', plot=False, return_raw=False):
    def identity(x):
        return x

    def evaluate_renko(brick, history, column_name):
        renko_obj = Renko()
        renko_obj.set_brick_size(brick_size=brick, auto=False)
        renko_obj.build_history(prices = history)
        return renko_obj.evaluate()[column_name]

    data.reset_index(drop=True)
    if compress:
        tr = data.ta.true_range(talib=True).dropna().reset_index(drop=True)
        if tr.size == 0:
            optimal_bin_width = 0
        else:
            optimal_bin_width = 2 * iqr(tr) / tr.size ** (1.0 / 3)
        if optimal_bin_width == 0:
            optimal_bin_count = 1
        else:
            optimal_bin_count = math.ceil((tr.max() - tr.min()) / optimal_bin_width)
        new_bin_count = math.floor(tr.size / optimal_bin_count)
        if new_bin_count == 0:
            new_bin_count = 1
        if plot:
            print('new_bin_count:', new_bin_count)

        data = data.resample(str(new_bin_count) + 'T')
        data = data.agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        data = data.fillna(method='pad')

    if method == 'brent':
        # Get ATR values (it needs to get boundaries)
        # Drop NaNs
        atr = talib.ATR(high=np.double(data.high),
                        low=np.double(data.low),
                        close=np.double(data.close),
                        timeperiod=25)
        atr = atr[np.isnan(atr) == False]
        if atr.shape[0] == 0:
            return False

        # Get optimal brick size as maximum of score function by Brent's (or similar) method
        # First and Last ATR values are used as the boundaries
        optimal_brick_sfo = opt.fminbound(lambda x: -evaluate_renko(brick=x, 
                                                                    history=data.close, column_name='score'), 
                                          np.min(atr), np.max(atr), disp=0)

    elif method == 'atr':
        # Get ATR values (it needs to get boundaries)
        # Drop NaNs
        atr = talib.ATR(high=np.double(data.high),
                        low=np.double(data.low),
                        close=np.double(data.close),
                        timeperiod=25)
        atr = atr[np.isnan(atr) == False]
        if atr.shape[0] == 0:
            return False

        optimal_brick_sfo = Renko().set_brick_size(auto=False, HLC_history=data[['high', 'low', 'close']], brick_size=atr[-1])

    elif method == 'auto_atr':
        optimal_brick_sfo = Renko().set_brick_size(auto=True, HLC_history=data[['high', 'low', 'close']])

    # Build Renko chart
    renko_obj_sfo = Renko()
    opt_brick_size = renko_obj_sfo.set_brick_size(auto=False, brick_size=optimal_brick_sfo)
    if plot:
        print('Set brick size to optimal: ', opt_brick_size)
    #renko_obj_sfo.build_history(prices=data['close'])
    hlc3 = (data['high'] + data['low'] + data['close']) / 3
    renko_obj_sfo.build_history(prices=hlc3)
    prices = renko_obj_sfo.get_renko_prices()
    directions = renko_obj_sfo.get_renko_directions()
    evaluation = renko_obj_sfo.evaluate()
    if plot:
        print('Renko bar prices: ', prices)
        print('Renko bar directions: ', directions)
        print('Renko bar evaluation: ', evaluation)

    if plot and len(renko_obj_sfo.get_renko_prices()) > 1:
        renko_obj_sfo.plot_renko()

    if direction_type == 'long':
        if trigger_type == 'exit':
            trigger = directions[-1] == -1 and directions[-2] == 1
        else:
            trigger = directions[-1] == 1
            if trigger_type == 'entry':
                trigger = trigger and directions[-2] == -1
    elif direction_type == 'short':
        if trigger_type == 'exit':
            trigger = directions[-1] == 1 and directions[-2] == -1
        else:
            trigger = directions[-1] == -1
            if trigger_type == 'entry':
                trigger = trigger and directions[-2] == 1

    return pd.Series(renko_obj_sfo.timed_renko_prices) if return_raw else trigger
