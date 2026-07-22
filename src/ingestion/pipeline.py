import logging

from src.ingestion.download_market_data import download_all_assets
from src.ingestion.load_data import load_raw_data
from src.validation.validation import DataValidator
from src.preprocessing.preprocess import DataPreprocessor

# logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

ASSETS = [
    'sp500',
    'nifty50',
    'gold',
    'bitcoin',
]

# pipeline

def run_pipeline():

    logger.info('starting finsight ai ETL pipeline')
    logger.info('Download market data')
    download_all_assets()

    for asset in ASSETS:
        logger.info(f'processing {asset}')
        df = load_raw_data(asset)
        validator = DataValidator(df)
        if validator.validate():
            logger.info(f'{asset} validation completed')
        else:
            logger.error(f'{asset} validation failed')
            continue
        
        processor = DataPreprocessor(df)
        processor.preprocess(asset)
        logger.info(f'{asset} preprocessing completed')

    logger.info('pipeline completed')

# main

if __name__ == '__main__':
    run_pipeline()