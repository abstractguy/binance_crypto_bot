# binance_crypto_bot

## Summary.

- Should run on different machines (it circumvents API limits by IP).

### Instructions.

#### crypto_logger.

- Logger/screener (doesn't need a Binance account).
- If using a VPS or a server of any kind, make sure it is up and running. You can disable VNC if running and review firewall rules if any are set up in a web app config panel, for instance (mosh needs some UDP ports, but install scripts will set up the firewall for you).
- Run [install/install_on_remote_server_part_1.sh](https://github.com/abstractguy/crypto_bot/blob/main/install/install_on_remote_server_part_1.sh) locally and follow instructions. It will set up the remote server.
- Run [install/install_on_remote_server_part_2.sh](https://github.com/abstractguy/crypto_bot/blob/main/install/install_on_remote_server_part_2.sh) locally and follow instructions. It will set up the remote server.
- Connect to it using mosh (which was installed). It is prefered over using ssh directly, to prevent sporadic TCP connection resets between the screener and the trader.
- Once installed, you only need to use [bootstrap.sh](https://github.com/abstractguy/crypto_bot/blob/main/bootstrap.sh) on the remote server, everytime you want to restart the logger/screener (say you made a mistake and want to restart it).
- Reminder: ensure your keys.txt file is not on the remote (logger/screener) server! You want to bypass API rate limits by using another server; otherwise, it would defeat the purpose of using a remote server in the first place.

#### crypto_bot.

- Wallet/trader (needs a Binance account, and crypto_logger already set up and running).
- Only on the trading machine: provide your API key and secret in a single line in a file named keys.txt, separated by a colon character (:).
- View comments in [install/install_conda.sh](https://github.com/abstractguy/crypto_bot/blob/main/install/install_conda.sh) and run it.
- View comments in [install/install_conda_crypto_bot_environment.sh](https://github.com/abstractguy/crypto_bot/blob/main/install/install_conda_crypto_bot_environment.sh) and run it.
- View variable definitions at the top of [crypto_trader.py](https://github.com/abstractguy/crypto_bot/blob/main/crypto_trader.py) and run it when ready.

#### tests.

- The notebook [crypto_logger_test.ipynb](https://github.com/abstractguy/crypto_bot/blob/main/crypto_logger_test.ipynb) is for component tests, if you want to modify the code and validate that it still works.
- [custom.tps](https://github.com/abstractguy/crypto_bot/blob/main/custom.tps) is an indicator backtest I ran on [TradingView](https://www.tradingview.com). The in-painted version gives tighter results, but does not represent reality. The current version does not do in-painting, so represents reality.

#### Disclaimers.

- Warning: You are responsible for your own trading losses!
- This was not intended to be public, but Binance is ceasing operations in my country.
- I do not intend to upgrade or document, but I remain available for questions.
- I knew nothing about finance before starting this project on my own.
- I do know about some adjustments that should be made, but am now focusing on machine learning in my other secret repositories.
- Targetting a single cryptocurrency exchange was a mistake, but it does not mean that redesigning for hundreds of exchanges will take as long.
- If you are wondering: this is just one of many secret projects I have been working on in the past months.

