from pathlib import Path
from datetime import datetime
import logging

import pandas as pd
import yfinance as yf
import yaml

# Logging Configuration

logging.basicConfig(
    level= logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# Paths

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT/'configs'/'config.yaml'
RAW_DATA_PATH = PROJECT_ROOT/'data'/'raw'
RAW_DATA_PATH.mkdir(parents=True,exist_ok=True)

# Load Config

def load_config() -> dict:
    with open(CONFIG_PATH,'r') as file:
        return yaml.safe_load(file)
    
# Download Single Asset

def download_asset_data(
        asset_name: str,
        ticker: str,
        start_date: str,
        end_date: str | None = None,
) -> pd.DataFrame:
    
    logger.info(f"Downloading {asset_name} ({ticker})...")
    
    try:
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False,
        )
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        if df.empty:
            raise ValueError(f"No data found for {ticker}")
        output_path = RAW_DATA_PATH / f"{asset_name}.csv"
        df.to_csv(output_path,index=False)

        logger.info(f"saved -> {output_path}")
        return df
    
    except Exception as e:
        logger.error(f"Failed downloading {asset_name}")
        logger.exception(e)
        return pd.DataFrame()
    
# Download All Assets

def download_all_assets():

    config = load_config()
    assets = config['assets']
    start_date = config['data']['start_date']
    end_date = config['data']['end_date']
    logger.info("Starting Market Data Download")

    for asset_name,ticker in assets.items():
        download_asset_data(
            asset_name=asset_name,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
        )
    
    logger.info("Download Completed")

# Main

if __name__ == '__main__':
    download_all_assets()

