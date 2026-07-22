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

    def summary(self):
        print('\n')
        print('Feature dataset summary')
        print(f'rows: {self.df.shape[0]}')
        print(f'columns: {self.df.shape[1]}')
        print('\ncolumn names\n')
        print(self.df.columns.tolist())
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
        engine.summary()
        engine.save_features(asset)