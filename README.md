# GenTrade

The python GenTrade package provide the core functions, model and data to support
GenAI based algorithms trading.


![](./docs/overview.png)

For a quick testing, please

- Install the python package

  ```
  pip install gentrade
  ```

- Then try:

  - [Demos](./demo/): command line based app to show market OHLCV data
  - [Tests](./tests/): test cases for the API and utilities
  - [Apps](./apps/): the application or microservices based on gentrade.


## App and Services

### OHLCV Data Service

- Start Server

  ```shell
  # Pull image
  docker pull registry.cn-hangzhou.aliyuncs.com/kenplusplus/gentrade_data_serv

  # Create .env file from .env_template

  # Run OHLCV datahub service
  docker run -p 8000:8000 \
      --env-file=.env -v <data folder>:/app/cache \
      registry.cn-hangzhou.aliyuncs.com/kenplusplus/gentrade_data_serv
  ```

- Client Test

  ```shell

  # Get all supported markets
  curl -X 'GET' \
    'http://127.0.0.1:8000/markets/?market_type=all' \
    -H 'accept: application/json'

  # Get all available assets from a specific market
  curl -X 'GET' \
    'http://127.0.0.1:8000/assets/?market_id=b13a4902-ad9d-11ef-a239-00155d3ba217&start=0&max_count=1000' \
    -H 'accept: application/json'

  # Get OHLCV for a specific asset
  curl -X 'GET' \
    'http://127.0.0.1:8000/asset/get_ohlcv?market_id=b13a4902-ad9d-11ef-a239-00155d3ba217&asset=BTC_USDT&timeframe=1m&since=-1&limit=10' \
    -H 'accept: application/json'

  # Start OHLCV collector threading in the background
  curl -X 'POST' \
    'http://127.0.0.1:8000/asset/start_collect?market_id=b13a4902-ad9d-11ef-a239-00155d3ba217&asset=DOGE_USDT&timeframe=1h&since=1732809600' \
    -H 'accept: application/json' \
    -d ''
  ```

The cached data can be found at [this directory](./cache/)
