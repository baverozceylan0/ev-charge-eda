import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type

import pandas as pd
import requests
import zipfile
from io import BytesIO

import os
from src.utils import RAW_DATAPATH, FORMATTED_DATAPATH

logger = logging.getLogger(__name__)

class DataLoader(ABC):
    """Abstract base class for dataset loading and validation."""

    def __init__(self, dataset_id: str, force_download: bool = False):
        os.makedirs(RAW_DATAPATH, exist_ok=True)
        os.makedirs(FORMATTED_DATAPATH, exist_ok=True)

        self.dataset_id = dataset_id
        self.force_download = force_download
        self.final_file_path = FORMATTED_DATAPATH / f"{self.dataset_id.lower()}.csv"
        self.raw_file_path = RAW_DATAPATH / f"{self.dataset_id.lower()}.csv"

    def load(self) -> pd.DataFrame:
        """Loads the dataset and validates structure and types."""        

        if self.final_file_path.exists() and not self.force_download:
            logger.info(f"The dataset '{self.dataset_id}' already exists in '{FORMATTED_DATAPATH}' and will not be re-downloaded.")
            df = pd.read_csv(self.final_file_path)
        else:
            logger.info(f"Preparing to download: {self.dataset_id}")
            df = self._load()

        return self.validate_ev_charging_dataframe(df)

    @abstractmethod
    def _load(self) -> pd.DataFrame:
        pass

    @staticmethod
    def validate_ev_charging_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate that the dataframe has all required columns and correct data types
        for EV charging session data.

        Args:
            df (pd.DataFrame): The input DataFrame to validate.

        Returns:
            pd.DataFrame: A validated and type-corrected copy of the input DataFrame.

        Raises:
            ValueError: If required columns are missing.
            TypeError: If column data types are incorrect.
        """
        required_columns = ["EV_id_x", "start_datetime", "end_datetime", "total_energy"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Convert to correct datetime types
        df["start_datetime"] = pd.to_datetime(df["start_datetime"])
        df["end_datetime"] = pd.to_datetime(df["end_datetime"])

        # Validate types
        if not pd.api.types.is_float_dtype(df["total_energy"]):
            raise TypeError("Column 'total_energy' must be of float type.")
        if not pd.api.types.is_string_dtype(df["EV_id_x"]):
            raise TypeError("Column 'EV_id_x' must be of string type.")

        return df

    @staticmethod
    def _download_and_extract(url: str, target_file_in_zip: str, output_file: Path) -> None:      
        """Download a ZIP file and extract the target to the output path."""
        logger.info(f"Downloading dataset from: {url}")

        # Download
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to download file (status code: {response.status_code})")

        # Extract
        with zipfile.ZipFile(BytesIO(response.content)) as zf:
            if target_file_in_zip not in zf.namelist():
                raise FileNotFoundError(f"'{target_file_in_zip}' not found in ZIP archive.")
            zf.extract(target_file_in_zip, path=RAW_DATAPATH)
            extracted_path = RAW_DATAPATH / target_file_in_zip
            extracted_path.rename(output_file)
            logger.info(f"Extracted and renamed '{target_file_in_zip}' → '{output_file.name}'")


class ACNDataLoader(DataLoader):
    """Loader for the ACN dataset."""

    def _download_acn_data(self, site_id: str) -> None: 

        TOKEN_FILE = ".acn_api_token"
        TOKEN_PLACEHOLDER = "<your_token_here>"
        TOKEN_INSTRUCTIONS = (
            "API_TOKEN is missing or placeholder.\n"
            "Please open '.acn_api_token' and replace <your_token_here> with your actual token.\n"
            "You can obtain a token at: https://ev.caltech.edu/register"
        )

        # Ensure the token file exists
        if not os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "w") as f:
                f.write(TOKEN_PLACEHOLDER)
            raise RuntimeError(f"{TOKEN_INSTRUCTIONS}\nA placeholder file has been created at '{TOKEN_FILE}'.")

        # Read the token
        with open(TOKEN_FILE, "r") as f:
            API_TOKEN = f.read().strip()

        # Validate the token
        if API_TOKEN == TOKEN_PLACEHOLDER or not API_TOKEN:
            raise RuntimeError(TOKEN_INSTRUCTIONS)

        headers = {
            "Authorization": f"Bearer {API_TOKEN}"
        }
        
        initial_connection_time = 'Mon, 1 Jan 2018 00:00:00 GMT'
        target_file = f'acn_{site_id}.csv'
        if os.path.exists(os.path.join(RAW_DATAPATH, target_file)):
            last_connection_time = pd.read_csv(os.path.join(RAW_DATAPATH, target_file)).tail(1)['connectionTime'].values[0]
        else:
            last_connection_time = initial_connection_time

        while True:
            url = f'https://ev.caltech.edu/api/v1/sessions/{site_id}?where=connectionTime>"{last_connection_time}"&max_results=500&sort=connectionTime'
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()  
            else:
                raise RuntimeError(f"Error {response.status_code}: {response.text}")

            _df = pd.json_normalize(data['_items'])
            if _df.empty:
                logger.debug("No more data.")
                break
            logger.info(f"Data downloaded from the ACN database from {last_connection_time} until {_df.tail(1)['connectionTime'].values[0]}")
            last_connection_time = _df.tail(1)['connectionTime'].values[0]
            if os.path.exists(os.path.join(RAW_DATAPATH, target_file)):
                _df_prev = pd.read_csv(os.path.join(RAW_DATAPATH, target_file)) 
                all_cols = set(_df_prev.columns) | set(_df.columns)
                _df_prev = _df_prev.reindex(columns=all_cols)
                _df = _df.reindex(columns=all_cols)
                _df = _df.fillna(value=pd.NaT)
                _df_prev = _df_prev.fillna(value=pd.NaT)
                _df = pd.concat([_df_prev, _df], ignore_index=True) 
            _df.to_csv(os.path.join(RAW_DATAPATH, target_file), mode='w', index=False)

    def _format_acn_data(self, site_id: str):
        target_file = f'acn_{site_id}.csv'

        combined_df = pd.read_csv(os.path.join(RAW_DATAPATH, target_file))

        formatted_df = combined_df.loc[:,['_id', 'connectionTime', 'disconnectTime', 'kWhDelivered', 'userID', 'timezone']]

        formatted_df["connectionTime"] = pd.to_datetime(formatted_df["connectionTime"], format="%a, %d %b %Y %H:%M:%S GMT", utc=True)
        formatted_df["disconnectTime"] = pd.to_datetime(formatted_df["disconnectTime"], format="%a, %d %b %Y %H:%M:%S GMT", utc=True)

        tz = formatted_df['timezone'].unique()
        if len(tz) != 1:
            raise ValueError(f"Expected a single timezone, but found multiple: {tz}")
        tz = tz[0]
        formatted_df['connectionTime'] = formatted_df['connectionTime'].dt.tz_convert(tz).dt.tz_localize(None)
        formatted_df['disconnectTime'] = formatted_df['disconnectTime'].dt.tz_convert(tz).dt.tz_localize(None)

        formatted_df['userID'] = formatted_df['userID'].astype('object')

        # Find NaNs and assign sequential placeholders
        mask = formatted_df['userID'].isna()
        formatted_df.loc[mask, 'userID'] = ['missing_' + str(i) for i in range(mask.sum())]

        # Factorize to assign EV0, EV1, EV2... based on order of appearance
        formatted_df['EV_id_x'] = 'EV' + pd.Series(pd.factorize(formatted_df['userID'])[0]).astype(str)

        formatted_df = formatted_df.rename(columns={'connectionTime': 'start_datetime', 'disconnectTime': 'end_datetime', 'kWhDelivered': 'total_energy'})
        formatted_df = formatted_df.drop(columns=['_id', 'userID'])
        formatted_df = formatted_df.loc[:,['EV_id_x', 'start_datetime', 'end_datetime', 'total_energy']]

        formatted_df.to_csv(os.path.join(FORMATTED_DATAPATH, target_file) , index=False)

    def _load(self) -> pd.DataFrame:
        site_id = self.dataset_id.split("_")[1].lower()
        
        self._download_acn_data(site_id)
        self._format_acn_data(site_id)

        df = pd.read_csv(self.final_file_path)  

        return df


class ASRDataLoader(DataLoader): 
    """Loader for the ASR dataset."""

    def _load(self) -> pd.DataFrame:
        # URL pointing to the zipped dataset hosted on 4TU repository
        url = "https://data.4tu.nl/ndownloader/items/80ef3824-3f5d-4e45-8794-3b8791efbd13/versions/1"        
        target_file_in_zip = "202410DatasetEVOfficeParking_v0.csv"
        formatted_path = FORMATTED_DATAPATH / f"{self.dataset_id.lower()}.csv"
        raw_path = RAW_DATAPATH / f"{self.dataset_id.lower()}.csv"

        if raw_path.exists() and not self.force_download:
            logger.info(f"The dataset '{self.dataset_id}' already exists in '{RAW_DATAPATH}' and will not be re-downloaded.")
        else:
            logger.info(f"Preparing to download: {self.dataset_id}")
            
            self._download_and_extract(url, target_file_in_zip, raw_path)

        # Select only the required columns, and save them to the final CSV
        df = pd.read_csv(raw_path, delimiter=";")
        df[["EV_id_x", "start_datetime", "end_datetime", "total_energy"]].to_csv(formatted_path, index=False)            
        logger.info(f"The dataset '{self.dataset_id}' is saved as: {formatted_path.name}")

        df = pd.read_csv(formatted_path)
        df["EV_id_x"] = df["EV_id_x"].astype("string")
        df["start_datetime"] = pd.to_datetime(df["start_datetime"])
        df["end_datetime"] = pd.to_datetime(df["end_datetime"])
        df["total_energy"] = df["total_energy"].astype("float")                   

        return df    


class DataLoaderFactory:
    """Factory for instantiating dataset-specific DataLoader objects."""

    @staticmethod
    def get_loader(dataset_id: str, force_download: bool = False) -> DataLoader:
        loaders: dict[str, Type[DataLoader]] = {
            "ASR": ASRDataLoader,
            "ACN_Caltech": ACNDataLoader,
            "ACN_JPL": ACNDataLoader,
            "ACN_Office001": ACNDataLoader
        }

        if dataset_id not in loaders:
            raise ValueError(f"No DataLoader defined for dataset: {dataset_id}")

        return loaders[dataset_id](dataset_id, force_download=force_download)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    loader = DataLoaderFactory.get_loader("ASR", force_download=True)
    df = loader.load()
    print(df.info())