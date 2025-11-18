from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_DATA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yml_file,write_yml_file
from scipy.stats import ks_2samp
import pandas as pd
import os
import sys

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_validation_config:DataValidationConfig):
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self.schema_config=read_yml_file(SCHEMA_DATA_FILE_PATH)

        except Exception as e:
            raise NetworkSecurityException(e,sys)

    @staticmethod    
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def no_of_columns(self,dataframe:pd.DataFrame)->bool:
        number_of_columns=len(self.schema_config["columns"])
        logging.info(f"Required no of columns are {number_of_columns}")
        logging.info(f"Datframe has {len(dataframe.columns)}")

        if len(dataframe.columns)==number_of_columns:
            return True
        else:
            return False
        
    def is_numeric_col_exist(self, dataframe: pd.DataFrame) -> bool:
        numeric_cols = dataframe.select_dtypes(include=['int64', 'float64'])
        return len(numeric_cols.columns) > 0

    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            status=True
            report={}
            for columns in base_df.columns:
                d1=base_df[columns]
                d2=current_df[columns]
                is_same_dist=ks_2samp(d1,d2)
                if threshold<=is_same_dist.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=False
                report.update({columns:{
                    "p-value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                }})

            drift_report_file_path=self.data_validation_config.drift_report_file_path

            #create directory
            dir_path=os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yml_file(drift_report_file_path,content=report)

        except Exception as e:
            raise NetworkSecurityException(e,sys)  
    def initiate_data_validate(self)->DataValidationArtifact:
        try:
            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)

            static=self.no_of_columns(dataframe=train_dataframe)
            if not static:
                error_message=f"Train Dataframe does not contain all columns"

            static=self.no_of_columns(dataframe=test_dataframe)
            if not static:
                error_message=f"Test Dataframe does not contain all columns"

            static=self.is_numeric_col_exist(dataframe=train_dataframe)
            if not static:
                error_message=f"Train Dataframe does not contain numerical data"

            static=self.is_numeric_col_exist(dataframe=test_dataframe)
            if not static:
                error_message=f"Test Dataframe does not contain numerical data"

            #check data drift
            status=self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)
            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path,index=False,header=True
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path,index=False,header=True
            )
            data_validation_artifact=DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )
            return data_validation_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
