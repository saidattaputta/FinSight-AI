from pathlib import Path
import pandas as pd
import logging

# logging configuration
logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# Paths

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DATA_PATH = PROJECT_ROOT / 'data' / 'processed'

# load raw data

def load_raw_data(asset_name:str) -> pd.DataFrame:
    file_path = RAW_DATA_PATH / f"{asset_name}.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist")
    
    logger.info(f"Loading raw data: {asset_name}")

    df = pd.read_csv(
        file_path,
        parse_dates=['Date'],
        index_col='Date'
    )
    logger.info(f"Loaded {(len(df))} rows")

    return df

#  load processed data

def load_processed_data(asset_name:str)-> pd.DataFrame:

    file_path = PROCESSED_DATA_PATH / f'{asset_name}.csv'
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exists")
    logger.info(f"Loading Processed Data: {asset_name}")

    df = pd.read_csv(
        file_path,
        parse_dates=['Date'],
        index_col='Date'
    )

    logger.info(f"Loaded {len(df)} rows")

    return df

# Main

if __name__ == '__main__':
    assets = [
        'sp500',
        'nifty50',
        'gold',
        'bitcoin'
    ]

    for asset in assets:
        try:
            df = load_raw_data(asset)
            print("\n")
            print(asset.upper())
            print("-"* 30)

            print(df.head())

            print("\nshape:",df.shape)
            print("\ncolumns:")
            print(df.columns.tolist())

        except Exception as e:
            logger.error(e)