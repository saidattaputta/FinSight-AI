from pathlib import Path
import logging
import pandas as pd
from src.ingestion.load_data import load_raw_data

# Logging configuration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# Paths

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_PATH = PROJECT_ROOT / 'data' / 'processed'
PROCESSED_DATA_PATH.mkdir(parents=True,exist_ok=True)

# Data Preprocessing

class DataPreprocessor:

    def __init__(self, df:pd.DataFrame):
        self.df = df.copy()

    def remove_duplicate_rows(self):
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        after = len(self.df)

        logger.info(
            f"removed {before-after} duplicate rows"
        )

    def sort_by_date(self):
        self.df.sort_index(inplace=True)
        logger.info("sorted according to date")

    def handle_missing_values(self):
        missing_before = self.df.isnull().sum().sum()
        self.df.ffill(inplace=True)
        self.df.bfill(inplace=True)
        missing_after = self.df.isnull().sum().sum()
        logger.info(
            f"missing values: {missing_before} -> {missing_after}"
        )
    
    def remove_invalid_rows(self):
        before = len(self.df)
        self.df = self.df[
            (self.df['Open']>0)
            & (self.df['High']>0)
            & (self.df['Low']>0)
            & (self.df['Close']>0)
            & (self.df['Volume']>=0)
            & (self.df['High']>= self.df['Low'])
        ]
        after = len(self.df)

        logger.info(
            f"removed {before-after} invalid rows"
        )

    def standardize_column_names(self):
        self.df.columns = [
            col.strip().replace(" ","_")
            for col in self.df.columns
        ]
        logger.info("columns names standaridized")

    def save(self,asset_name):
        output=PROCESSED_DATA_PATH / f"{asset_name}.csv"
        self.df.to_csv(output)
        logger.info(f"saved -> {output}")

    def preprocess(self,asset_name):
        logger.info(f"preprocessing {asset_name}")
        self.remove_duplicate_rows()
        self.sort_by_date()
        self.handle_missing_values()
        self.remove_invalid_rows()
        self.standardize_column_names()
        self.save(asset_name)
        logger.info(f"{asset_name} preprocessing completed")
        return self.df
    
# main

if __name__ == '__main__':
    assets=[
        'sp500',
        'nifty50',
        'gold',
        'bitcoin',
    ]

    for asset in assets:
        print(asset.upper())
        df = load_raw_data(asset)
        processor = DataPreprocessor(df)
        processed_df = processor.preprocess(asset)
        print(processed_df.head())