from datetime import datetime
import logging
import pandas as pd
from src.ingestion.load_data import load_raw_data

# logging configuration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# required columns

REQUIRED_COLUMNS = [
    'Open',
    'High',
    'Low',
    'Close',
    'Adj Close',
    'Volume',
]

# Validator class

class DataValidator:
    def __init__(self, df:pd.DataFrame):
        self.df = df.copy()
        self.error = []
        self.warnings = []

    def check_required_columns(self):
        missing = [
            col 
            for col in REQUIRED_COLUMNS
            if col not in self.df.columns
        ]

        if missing:
            self.error.append(
                f"missing columns: {missing}"
            )

    def check_missing_values(self):
        missing = self.df.isnull().sum()
        missing = missing[missing>0]
        if not missing.empty:
            self.warnings.append(
                f"missing values:\n{missing}"
            )

    def check_duplicate_rows(self):
        duplicates = self.df.duplicated().sum()
        if duplicates >0:
            self.warnings.append(
                f"{duplicates} duplicate rows found"
            )

    def check_duplicate_dates(self):
        duplicates = self.df.index.duplicated().sum()
        if duplicates>0:
            self.warnings.append(
                f"{duplicates} duplicate dates found"
            )

    def check_future_dates(self):
        future = self.df.index > pd.Timestamp.today()
        if future.any():
            self.error.append(
                "future dates appeared"
            )

    def check_negative_volume(self):
        if (self.df['Volume']<0).any():
            self.error.append(
                "Negative colume appeared"
            )

    def check_invalid_prices(self):
        if (self.df['Open'] <=0).any():
            self.error.append("Invalid open price")
        if (self.df['High'] <=0).any():
            self.error.append("Invalid High price")
        if (self.df['Low'] <=0).any():
            self.error.append("Invalid Low price")
        if (self.df['Close'] <=0).any():
            self.error.append("Invalid Close price")

        invalid = self.df['High'] < self.df['Low']
        if invalid.any():
            self.error.append(
                "High price lower than low price"
            )

    def check_data_types(self):
        numeric = [
            'Open',
            'Low',
            'High',
            'Close',
            'Adj Close',
            'Volume'
        ]

        for col in numeric:
            if not pd.api.types.is_numeric_dtype(
                self.df[col]
            ):
                self.error.append(
                    f"{col} is not numeric"
                )

    def generate_report(self):
        print("\n")
        print("Validation Report")
        if self.error:
            print("\nErrors")
            for i in self.error:
                print(f"{i}")
        else:
            print("No Errors")

        if self.warnings:
            print("\nWarnings")
            for i in self.warnings:
                print(f"{i}")
        else:
            print("No Warnings")

        print("\nRows:",len(self.df))
        print("\nColumns:",len(self.df.columns))

    def validate(self):
        self.check_required_columns()
        self.check_missing_values()
        self.check_duplicate_rows()
        self.check_duplicate_dates()
        self.check_future_dates()
        self.check_negative_volume()
        self.check_invalid_prices()
        self.check_data_types()
        self.generate_report()

        return len(self.error) == 0
    
# Main

if __name__ == '__main__':
    assets = [
        'sp500',
        'nifty50',
        'gold',
        'bitcoin',
    ]

    for asset in assets:
        print(asset.upper())
        df = load_raw_data(asset)
        validator = DataValidator(df)
        validator.validate()
