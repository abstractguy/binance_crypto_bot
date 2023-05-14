#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_output_logger_1min.py
# By:          Samuel Duclos
# For:         Myself
# Description: This file implements the main for the crypto_logger.
#              The crypto_logger is a program that logs the utils market data
#              and outputs the data in different time intervals.
#              The program is designed to be run in the background.
#              The program can be stopped and resumed at any time.
#              The program will check if there is data already logged and will resume
#              logging from the last logged data.

# Optimize this program for speed.
# Use the following command to optimize the program:
# $ python -m cython -a crypto_logger.py
# Use the following command to check the speed of the program:
# $ python -m cProfile -o crypto_logger.prof crypto_logger.py

# Library imports.
from typing import Dict, Union
from utils.crypto_logger_input import Crypto_logger_input
from utils.crypto_logger_output import Crypto_logger_output
import time
import pandas as pd

def init_loggers() -> Dict[str, Union[Crypto_logger_input, Crypto_logger_output]]:
    """Main logger initialization."""
    #crypto_logger_input_5s = Crypto_logger_input(interval='5s', buffer_size=3000, 
    #                                             price_percent=5.0, volume_percent=0.0, 
    #                                             as_pair=False, append=True, roll=10)
    crypto_logger_output_5s = Crypto_logger_output(interval_input='5s', 
                                                   interval='5s', 
                                                   buffer_size=60, 
                                                   input_log_name='input', 
                                                   append=False, 
                                                   roll=1000)
    crypto_logger_output_1min = Crypto_logger_output(interval_input='5s', 
                                                     interval='1min', 
                                                     buffer_size=1500, 
                                                     input_log_name='output', 
                                                     append=False, 
                                                     roll=1000)
    #crypto_logger_output_30min = Crypto_logger_output(interval_input='1min', 
    #                                                  interval='30min', 
    #                                                  buffer_size=60, 
    #                                                  input_log_name='output', 
    #                                                  append=False, 
    #                                                  roll=1000)
    #crypto_logger_output_1h = Crypto_logger_output(interval_input='30min', 
    #                                               interval='1h', 
    #                                               buffer_size=60, 
    #                                               input_log_name='output', 
    #                                               append=False, 
    #                                               roll=1000)
    #crypto_logger_output_1h = Crypto_logger_output(interval_input='1min', 
    #                                               interval='1h', 
    #                                               buffer_size=60, 
    #                                               input_log_name='output', 
    #                                               append=False, 
    #                                               roll=1000)
    #crypto_logger_output_1d = Crypto_logger_output(interval_input='1h', 
    #                                               interval='1d', 
    #                                               buffer_size=60, 
    #                                               input_log_name='output', 
    #                                               append=False, 
    #                                               roll=1000)
    crypto_loggers = {
        #'input_5s': crypto_logger_input_5s, 
        'output_5s': crypto_logger_output_5s, 
        'output_1min': crypto_logger_output_1min, 
        #'output_30min': crypto_logger_output_30min, 
        #'output_1h': crypto_logger_output_1h, 
        #'output_1d': crypto_logger_output_1d
    }
    return crypto_loggers

def loop_loggers(crypto_loggers: Dict[str, Union[Crypto_logger_input, Crypto_logger_output]]) -> None:
    """Main logger loop."""
    print('Starting crypto loggers.')
    #input_5s = crypto_loggers['input_5s'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    output_5s = crypto_loggers['output_5s'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    output_1min = crypto_loggers['output_1min'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    #output_30min = crypto_loggers['output_30min'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    #output_1h = crypto_loggers['output_1h'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    #output_1d = crypto_loggers['output_1d'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    #input_5s_screened = crypto_loggers['input_5s'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    output_5s_screened = crypto_loggers['output_5s'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    output_1min_screened = crypto_loggers['output_1min'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    #output_30min_screened = crypto_loggers['output_30min'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    #output_1h_screened = crypto_loggers['output_1h'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    #output_1d_screened = crypto_loggers['output_1d'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    try:
        t2 = time.time()
        while True:
            t1 = t2
            t2 = time.time()
            print('Time spent for one loop:', t2 - t1)
            #input_5s = crypto_loggers['input_5s'].get_and_put_next(old_dataset=input_5s, dataset=None)
            #output_5s = crypto_loggers['output_5s'].get_and_put_next(old_dataset=output_5s, dataset=input_5s)
            output_5s = crypto_loggers['output_5s'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
            output_1min = crypto_loggers['output_1min'].get_and_put_next(old_dataset=output_1min, dataset=output_5s)
            #output_30min = crypto_loggers['output_30min'].get_and_put_next(old_dataset=output_30min, dataset=output_1min)
            #output_1h = crypto_loggers['output_1h'].get_and_put_next(old_dataset=output_1h, dataset=output_30min)
            #output_1h = crypto_loggers['output_1h'].get_and_put_next(old_dataset=output_1h, dataset=output_1min)
            #output_1d = crypto_loggers['output_1d'].get_and_put_next(old_dataset=output_1d, dataset=output_1h)
            #input_5s = crypto_loggers['input_5s'].get_and_put_next(old_dataset=input_5s, dataset=None)
            #input_5s_screened, live_filtered = \
            #    crypto_loggers['input_5s'].screen_next(old_dataset_screened=input_5s_screened, dataset_screened=None, 
            #                                           dataset=input_5s, live_filtered=None)
            #output_5s_screened, _ = \
            #    crypto_loggers['output_5s'].screen_next(old_dataset_screened=output_5s_screened, 
            #                                            dataset_screened=input_5s_screened, 
            #                                            dataset=output_5s, live_filtered=live_filtered)
            output_5s_screened = crypto_loggers['output_5s'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
            output_1min_screened, _ = \
                crypto_loggers['output_1min'].screen_next(old_dataset_screened=output_1min_screened, 
                                                          dataset_screened=output_5s_screened, 
                                                          dataset=output_1min, live_filtered=None)
            #output_30min_screened, _ = \
            #    crypto_loggers['output_30min'].screen_next(old_dataset_screened=output_30min_screened, 
            #                                               dataset_screened=output_1min_screened, 
            #                                               dataset=output_30min, live_filtered=None)
            #output_1h_screened, _ = \
            #    crypto_loggers['output_1h'].screen_next(old_dataset_screened=output_1h_screened, 
            #                                            dataset_screened=output_30min_screened, 
            #                                            dataset=output_1h, live_filtered=None)
            #output_1h_screened, _ = \
            #    crypto_loggers['output_1h'].screen_next(old_dataset_screened=output_1h_screened, 
            #                                            dataset_screened=output_1min_screened, 
            #                                            dataset=output_1h, live_filtered=None)
            #output_1d_screened, _ = \
            #    crypto_loggers['output_1d'].screen_next(old_dataset_screened=output_1d_screened, 
            #                                            dataset_screened=output_1h_screened, 
            #                                            dataset=output_1d, live_filtered=None)
            #crypto_loggers['input_5s'].log_next(dataset=input_5s, dataset_screened=input_5s_screened)
            #crypto_loggers['output_5s'].log_next(dataset=None, dataset_screened=output_5s_screened)
            #crypto_loggers['output_1min'].log_next(dataset=None, dataset_screened=output_1min_screened)
            crypto_loggers['output_1min'].log_next(dataset=output_1min, dataset_screened=output_1min_screened)
            #crypto_loggers['output_30min'].log_next(dataset=None, dataset_screened=output_30min_screened)
            #crypto_loggers['output_1h'].log_next(dataset=None, dataset_screened=output_1h_screened)
            #crypto_loggers['output_1d'].log_next(dataset=None, dataset_screened=output_1d_screened)
    except (KeyboardInterrupt, SystemExit):
        print('Saving latest complete dataset...')
        #input_5s = crypto_loggers['input_5s'].get_and_put_next(old_dataset=input_5s, dataset=None)
        #output_5s = crypto_loggers['output_5s'].get_and_put_next(old_dataset=output_5s, dataset=input_5s)
        output_1min = crypto_loggers['output_1min'].get_and_put_next(old_dataset=output_1min, dataset=output_5s)
        #output_30min = crypto_loggers['output_30min'].get_and_put_next(old_dataset=output_30min, dataset=output_1min)
        #output_1h = crypto_loggers['output_1h'].get_and_put_next(old_dataset=output_1h, dataset=output_30min)
        #output_1h = crypto_loggers['output_1h'].get_and_put_next(old_dataset=output_1h, dataset=output_1min)
        #output_1d = crypto_loggers['output_1d'].get_and_put_next(old_dataset=output_1d, dataset=output_1h)
        #crypto_loggers['input_5s'].log_next(dataset=input_5s, dataset_screened=None)
        #crypto_loggers['output_5s'].log_next(dataset=output_5s, dataset_screened=None)
        crypto_loggers['output_1min'].log_next(dataset=output_1min, dataset_screened=None)
        #crypto_loggers['output_30min'].log_next(dataset=output_30min, dataset_screened=None)
        #crypto_loggers['output_1h'].log_next(dataset=output_1h, dataset_screened=None)
        #crypto_loggers['output_1d'].log_next(dataset=output_1d, dataset_screened=None)
        #input_5s_screened, live_filtered = \
        #    crypto_loggers['input_5s'].screen_next(old_dataset_screened=input_5s_screened, dataset_screened=None, 
        #                                           dataset=input_5s, live_filtered=None)
        #output_5s_screened, _ = \
        #    crypto_loggers['output_5s'].screen_next(old_dataset_screened=output_5s_screened, 
        #                                            dataset_screened=input_5s_screened, 
        #                                            dataset=output_5s, live_filtered=live_filtered)
        output_1min_screened, _ = \
            crypto_loggers['output_1min'].screen_next(old_dataset_screened=output_1min_screened, 
                                                      dataset_screened=output_5s_screened, 
                                                      dataset=output_1min, live_filtered=None)
        #output_30min_screened, _ = \
        #    crypto_loggers['output_30min'].screen_next(old_dataset_screened=output_30min_screened, 
        #                                               dataset_screened=output_1min_screened, 
        #                                               dataset=output_30min, live_filtered=None)
        #output_1h_screened, _ = \
        #    crypto_loggers['output_1h'].screen_next(old_dataset_screened=output_1h_screened, 
        #                                            dataset_screened=output_30min_screened, 
        #                                            dataset=output_1h, live_filtered=None)
        #output_1h_screened, _ = \
        #    crypto_loggers['output_1h'].screen_next(old_dataset_screened=output_1h_screened, 
        #                                            dataset_screened=output_1min_screened, 
        #                                            dataset=output_1h, live_filtered=None)
        #output_1d_screened, _ = \
        #    crypto_loggers['output_1d'].screen_next(old_dataset_screened=output_1d_screened, 
        #                                            dataset_screened=output_1h_screened, 
        #                                            dataset=output_1d, live_filtered=None)
        #crypto_loggers['input_5s'].log_next(dataset=None, dataset_screened=input_5s_screened)
        #crypto_loggers['output_5s'].log_next(dataset=None, dataset_screened=output_5s_screened)
        crypto_loggers['output_1min'].log_next(dataset=None, dataset_screened=output_1min_screened)
        #crypto_loggers['output_30min'].log_next(dataset=None, dataset_screened=output_30min_screened)
        #crypto_loggers['output_1h'].log_next(dataset=None, dataset_screened=output_1h_screened)
        #crypto_loggers['output_1d'].log_next(dataset=None, dataset_screened=output_1d_screened)
        print('User terminated crypto logger process.')
    except Exception as e:
        print(e)
    finally:
        # Release resources.
        print('Crypto logger processes done.')

def main() -> None:
    """crypto_logger main."""
    crypto_loggers = init_loggers()
    loop_loggers(crypto_loggers)

if __name__ == '__main__':
    main()
