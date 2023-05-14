#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/trader/ssh.py
# By:          Samuel Duclos
# For          Myself
# Description: SSH client using Paramiko to retrieve logs from server.

# Library imports.
from typing import Optional, Tuple
from os.path import exists
import time
import sys
import pandas as pd
import paramiko

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

# Class definition.
class Ssh:
    input_log = '~/workspace/crypto_logs/crypto_input_log_15s.txt'
    output_log_screened = \
        '~/workspace/crypto_logs/crypto_output_log_1d_screened.txt'

    def __init__(self, 
                 input_log: Optional[str] = None, 
                 output_log_screened: Optional[str] = None, 
                 keys_file: str = 'server_keys.txt') -> None:
        if input_log is not None:
            self.input_log = input_log
        if output_log_screened is not None:
            self.output_log_screened = output_log_screened
        ip_address, password = self.init_credentials(keys_file=keys_file)
        self.ssh = self.init_ssh(ip_address=ip_address, username='sam', 
                                 port=22, password=password)

    def init_credentials(self, keys_file: str = 'server_keys.txt') -> Tuple[str, str]:
        if exists(keys_file):
            with open(keys_file, 'r') as f:
                ip_address, password = \
                    f.readline().replace('\n', '').split(':')
        return ip_address, password

    def init_ssh(self, ip_address: str = '0.0.0.0', username: str = 'sam', 
                 port: int = 22, password: str = '') -> paramiko.SSHClient:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_address, username='sam', port=22, password=password)
        return ssh

    def get_logs_from_server(self, server_log: str = output_log_screened) -> Optional[pd.DataFrame]:
        ssh_stdin, ssh_stdout, ssh_stderr = \
            self.ssh.exec_command('cat {}'.format(server_log))
        df = StringIO(str(ssh_stdout.read().decode('utf-8')))
        try:
            df = pd.read_csv(df)
            if df.shape[0] < 1:
                df = None
        except (IndexError, pd.errors.EmptyDataError):
            df = None
            time.sleep(0.5)
        return df
