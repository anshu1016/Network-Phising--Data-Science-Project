# from networksecurity.entity.artifact_entity import DataIngestionArtifact

from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp
import pandas as pd 
import os  
import sys

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except NetworkSecurityException as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        



        
    def validate_number_of_cols(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_cols = len(self._schema_config['columns'])
            logging.info(f'Required number of columns: {number_of_cols}')
            logging.info(f'DataFrame has columns: {len(dataframe.columns)}')

            if len(dataframe.columns) == number_of_cols:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)

        


    def is_numerical_exists(self, dataframe: pd.DataFrame) -> bool:
        try:
            numerical_cols = self._schema_config['numerical_columns']
            missing_numerical_cols = [col for col in numerical_cols if col not in dataframe.columns]

            if missing_numerical_cols:
                logging.warning(f"Missing numerical columns: {missing_numerical_cols}")
                return False

            logging.info("All numerical columns are present in the dataframe.")
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def detect_dataset_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_sample_dist = ks_2samp(d1, d2)
                is_found = is_sample_dist.pvalue < threshold
                if is_found:
                    status = False
                report[column] = {
                    "p_value": float(is_sample_dist.pvalue),
                    "drift_status": is_found
                }
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys)




        
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_dataframe = self.read_data(train_file_path)
            test_dataframe = self.read_data(test_file_path)

            error_message = ""

            if not self.validate_number_of_cols(train_dataframe):
                error_message += "Train dataframe does not have required columns.\n"
            if not self.validate_number_of_cols(test_dataframe):
                error_message += "Test dataframe does not have required columns.\n"
            if not self.is_numerical_exists(train_dataframe):
                error_message += "Train dataframe is missing numerical columns.\n"
            if not self.is_numerical_exists(test_dataframe):
                error_message += "Test dataframe is missing numerical columns.\n"

            if error_message:
                raise Exception(error_message)

            status = self.detect_dataset_drift(train_dataframe, test_dataframe)

            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)

            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


