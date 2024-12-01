import os
import logging
import time
import ccxt
import pandas as pd
import numpy as np
from .core import FinancialAsset, FinancialMarket, TIME_FRAME

LOG = logging.getLogger(__name__)

class CryptoMarket(FinancialMarket):

    def __init__(self, name: str, market_id:str=None, cache_dir:str=None):
        super().__init__(name, FinancialMarket.MARKET_CRYPTO, market_id,
                         cache_dir)

    def get_crypto_asset(self, base, quote):
        """
        Return asset according to crypt naming rule "base/quote"
        """
        return self.get_asset("%s_%s" % (base.lower(), quote.lower()))

class CryptoAsset(FinancialAsset):

    def __init__(self, currency_base:str, currency_quote:str,
                 symbol:str, market:CryptoMarket):
        self._currency_base = currency_base.lower()
        self._currency_quote = currency_quote.lower()
        self._symbol = symbol
        super().__init__("%s_%s" %(currency_base.lower(),
                                   currency_quote.lower()), market)

    @property
    def currency_base(self) -> str:
        return self._currency_base

    @property
    def currency_quote(self) -> str:
        return self.currency_quote

    @property
    def symbol(self) -> str:
        return self._symbol

class BinanceMarket(CryptoMarket):

    MARKET_ID = "b13a4902-ad9d-11ef-a239-00155d3ba217"

    def __init__(self, market_id=MARKET_ID, cache_dir:str=None):
        if cache_dir is not None:
            cache_dir = os.path.join(cache_dir, "Binance")
        super().__init__("Binance", market_id, cache_dir)
        self._ccxt_inst = ccxt.binance({'apiKey': self.api_key,
                                        'secret': self.api_secret})
        self._ready = False

    @property
    def api_key(self):
        return os.getenv("TIA_BINANCE_API_KEY")

    @property
    def api_secret(self):
        return os.getenv("TIA_BINANCE_API_SECRET")

    def init(self):
        if self._ready:
            return False

        LOG.info("Loading Binance Market...")
        retry_num = 0
        success = False
        while retry_num < 5:
            retry_num += 1
            try:
                self._ccxt_inst.load_markets()
            except (ccxt.RequestTimeout, ccxt.NetworkError):
                LOG.critical("Request Timeout... retry[%d/5]", retry_num)
                time.sleep(5)
            except Exception as e:
                LOG.critical(e, exc_info=True)
                LOG.error("Fail to load market... retry[%d/5]", retry_num)
                time.sleep(5)
            else:
                success = True
                break

        if not success:
            return False

        for symbol in self._ccxt_inst.symbols:
            base, quote = symbol.split("/")
            caobj = CryptoAsset(base, quote, symbol, self)
            self.assets[caobj.name] = caobj
        LOG.info("Found %d crypto assets.", len(self.assets))

        self._ready = True
        return True

    def fetch_ohlcv(self, asset:CryptoAsset, timeframe: str, since: int = -1,
                    limit: int = 500):
        LOG.info("Fetch from market: timeframe=%s since=%d, limit=%d",
                 timeframe, since, limit)
        remaining = limit
        delta = TIME_FRAME[timeframe]
        all_ohlcv = []

        if since == -1:
            to_ = int(time.time() / delta - 1) * delta
            since = to_ - (limit - 1) * delta
        else:
            max_limit = int((time.time() - since) / delta)
            limit = min(limit, max_limit)
            to_ = int((since + (limit - 1)* delta) / delta) * delta

        # Continuous to fetching until get all data
        while remaining > 0:
            ohlcv = self._ccxt_inst.fetch_ohlcv(asset.symbol, timeframe,
                                                since * 1000, limit)
            all_ohlcv += ohlcv
            remaining = remaining - len(ohlcv)
            since = to_ - remaining * delta
            time.sleep(0.1)

        df = pd.DataFrame(all_ohlcv, columns =
                          ['time', 'open', 'high', 'low', 'close', 'vol'])
        df.time = (df.time / 1000).astype(np.int64)
        df.set_index('time', inplace=True)
        return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cm = BinanceMarket(cache_dir="./binance/")
    cm.init()
    asset_btcusdt = cm.get_crypto_asset("ETH", "USDT")
    while True:
        ret = asset_btcusdt.fetch_ohlcv("1h", limit=3)
        print(ret)
        time.sleep(30)
