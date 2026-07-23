from pathlib import Path
import logging
import pandas as pd
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
        loss = x.where(x<0,0.0)
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
        engine.add_momentum()
        engine.add_rsi()
        engine.add_sma()
        engine.add_ema()
        engine.summary()
        engine.save_features(asset)