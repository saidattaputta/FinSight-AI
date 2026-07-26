from pathlib import Path
import logging
import pandas as pd
import numpy as np
from src.ingestion.load_data import load_processed_data

# logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# paths

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_PATH = PROJECT_ROOT / 'data' / 'features'
FEATURE_PATH.mkdir(parents=True,exist_ok=True)

# indicator engine

class TechnicalIndicatorEngine:

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_dataframe(self):
        return self.df
    
    def save_features(self, asset_name:str):
        output = FEATURE_PATH / f'{asset_name}_features.csv'
        self.df.to_csv(output)
        logger.info(f'features saved -> {output}')

    # trend indicator
    def add_sma(self):
        logger.info("calculating SMA indicators")
        self.df['SMA_10'] = self.df['Close'].rolling(window=10).mean()
        self.df['SMA_20'] = self.df['Close'].rolling(window=20).mean()
        self.df['SMA_50'] = self.df['Close'].rolling(window=50).mean()
        logger.info("SMA indicators added")

    # trend indicator
    def add_ema(self):
        logger.info('Calculating EMA indicators')
        self.df['EMA_10'] = self.df['Close'].ewm(span=10,adjust=False).mean()
        self.df['EMA_20'] = self.df['Close'].ewm(span=20,adjust=False).mean()
        self.df['EMA_50'] = self.df['Close'].ewm(span=50,adjust=False).mean()
        logger.info('EMA indicators added')

    # momentum indicators
    def add_rsi(self,period:int=14):
        logger.info(f'Calculating RSI ({period})')
        x = self.df['Close'].diff()
        gain = x.where(x>0,0.0)
        loss = -x.where(x<0,0.0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain/avg_loss
        self.df[f'RSI_{period}'] = 100-(100/(1+rs))
        logger.info('RSI added')

    def add_momentum(self,period:int=10):
        logger.info(f'calculating momentum ({period})')
        self.df[f'Momentum_{period}'] = (
            self.df['Close']-self.df['Close'].shift(period)
        )
        logger.info('momentum added')

    # MACD 
    def add_macd(self,
                 fast_period: int = 12,
                 slow_period: int = 26,
                 signal_period: int =9,):
        logger.info("Calculating MACD")
        ema_fast = self.df['Close'].ewm(
            span = fast_period,
            adjust=False
        ).mean()
        ema_slow = self.df['Close'].ewm(
            span = slow_period,
            adjust = False
        ).mean()

        self.df['MACD'] = ema_fast - ema_slow

        self.df['MACD_Signal'] = (
            self.df['MACD']
            .ewm(span=signal_period,adjust=False)
            .mean()
        )
        self.df['MACD_Histogram'] = (
            self.df['MACD'] - self.df['MACD_Signal']
        )

        logger.info("MACD added")

    # volatility indicators
    def add_bollinger_bands(self, period: int = 20, num_std: int = 2):
        logger.info("calculating bollinger bands")
        middle = self.df['Close'].rolling(window=period).mean()
        std = self.df['Close'].rolling(window=period).std()

        self.df['BB_Middle'] = middle
        self.df['BB_Upper'] = middle + (num_std*std)
        self.df['BB_Lower'] = middle - (num_std * std)
        logger.info("Bollinger Bands added")

    def add_atr(self,period: int = 14):
        logger.info("calculating atr")
        high_low = self.df['High'] - self.df['Low']
        high_close = (self.df['High'] - self.df['Close'].shift(1)).abs()
        low_close = (self.df['Low'] - self.df['Close'].shift(1)).abs()
        tr = pd.concat(
            [high_low,high_close,low_close],
            axis=1
        ).max(axis=1)
        self.df[f'ATR_{period}'] = (
            tr.rolling(window=period).mean()
        )
        logger.info("ATR added")

    def add_rolling_std(self,period:int = 20):
        logger.info("Calculating rolling std")
        self.df[f'Rolling_Std_{period}'] = (
            self.df['Close']
            .rolling(window=period)
            .std()
        )
        logger.info("rolling std added")

    #  volume indicator
    def add_obv(self):
        logger.info("calculating obv")
        obv = [0]
        for i in range(1,len(self.df)):
            current_colse = self.df['Close'].iloc[i]
            previous_close = self.df['Close'].iloc[i-1]
            current_volume = self.df['Volume'].iloc[i]

            if current_colse > previous_close:
                obv.append(obv[-1] + current_volume)
            elif current_colse < previous_close:
                obv.append(obv[-1] - current_volume)
            else:
                obv.append(obv[-1])
        self.df['OBV'] = obv
        logger.info("OBV added")

    # Time-Series Features
    def add_lag_features(self,lags=None):
        if lags is None:
            lags = [1,3,5,10]
        logger.info('calculating lag features')
        for lag in lags:
            self.df[f'lag_{lag}'] = self.df['Close'].shift(lag)
        logger.info('Lag features added')

    def add_daily_returns(self):
        logger.info('calculating daily returns')
        self.df['Daily_Return'] = self.df['Close'].pct_change()
        logger.info('Daily returns added')

    def add_log_return(self):
        logger.info('calculating log returns')
        self.df['Log_Return'] = np.log(
            self.df['Close']/self.df['Close'].shift(1)
        )
        logger.info('Log returns added')

    def add_rolling_mean(self,period:int=20):
        logger.info('Calculating rolling mean')
        self.df[f'Rolling_Mean_{period}'] = (
            self.df['Close']
            .rolling(window=period)
            .mean()
        )
        logger.info('Rolling Mean added')

    def add_rolling_volatility(self,period:int=20):
        logger.info("calculating rolling volatility")
        self.df[f'Rolling_Volatility_{period}'] = (
            self.df['Daily_Return']
            .rolling(window=period)
            .std()
        )
        logger.info('rolling volatility added')

    def summary(self):
        print('\n')
        print('Feature dataset summary')
        print(f'rows: {self.df.shape[0]}')
        print(f'columns: {self.df.shape[1]}')
        print('\ncolumn names\n')
        print(sorted(self.df.columns.tolist()))
        print('\nfirst five rows\n')
        print(self.df.head())

# main

if __name__ == '__main__':
    assets = [
        'sp500',
        'nifty50',
        'gold',
        'bitcoin',
    ]
    for asset in assets:
        print('\n')
        print(asset.upper())
        df = load_processed_data(asset)
        engine = TechnicalIndicatorEngine(df)
        engine.add_sma()
        engine.add_ema()
        engine.add_rsi()
        engine.add_momentum()
        engine.add_macd()
        engine.add_bollinger_bands()
        engine.add_atr()
        engine.add_rolling_std()
        engine.add_obv()
        engine.add_lag_features()
        engine.add_daily_returns()
        engine.add_log_return()
        engine.add_rolling_mean()
        engine.add_rolling_volatility()
        engine.summary()
        engine.save_features(asset)