import os 
import sys
import numpy as np
import pandas as pd

"""
Defining common constant variables  for training pipeline
"""
TARGET_COLUMN="Result"
PIPELINE_NAME:str="NetworkSecurity"  ##Name of your ML pipeline project.
ARTIFACT_DIR:str="Artifacts"  ##Folder where all ML pipeline outputs will be stored
FILE_NAME:str="phisingData.csv"

TRAIN_FILE_NAME:str="train.csv"
TEST_FILE_NAME:str="test.csv"
SCHEMA_DATA_FILE_PATH:str=os.path.join("data_schema","schema.yaml")

"""
Data Ingestion related constant start with Data_Ingestion VAR Name
"""
DATA_INGESTION_COLLECTION_NAME:str="NetworkData"
DATA_INGESTION_DATABASE_NAME:str="Shardul"
DATA_INGESTION_DIR_NAME:str="data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR:str="feature_store"
DATA_INGESTION_INGESTED_DIR:str="ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO:float=0.2

DATA_VALIDATION_DIR_NAME:str="data_validation"
DATA_VALIDATION_VALID_DIR:str="validated"
DATA_VALIDATION_INVALID_DIR:str="invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR:str="drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME:str="report.yaml"

DATA_TRANSFORMATION_DIR_NAME:str="data_transformation"
DATA_TRANSFORMATION_DIR:str="transformed"
TRANSFORMED_OBJECT_FILE_NAME:str="transformed_object"
PREPROCESSOR_OBJECT_FILE_NAME:str="preprocessor.pkl"

##KNN IMPUTER FOR replacing NAN VALUES
DATA_TRANSFORMATION_IMPUTER_PARAMS:dict={
    "missing_values":np.nan,
    "n_neighbors":3,
    "weights":"uniform",
}
