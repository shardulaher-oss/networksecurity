import os
import sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.entity.artifact_entity import DataTransformationArtifact
from networksecurity.entity.artifact_entity import DataValidationArtifact
from networksecurity.constant.training_pipeline import TARGET_COLUMN
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS,PREPROCESSOR_OBJECT_FILE_NAME
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline 
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_object

class DataTransformation:
    def __init__(self,data_validation_artifact:DataValidationArtifact,
                data_transformation_config:DataTransformationConfig):
        try:
            self.data_validation_artifact:DataValidationArtifact=data_validation_artifact
            self.data_transformation_config:DataTransformationConfig=data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)   

    def get_data_transformation_obj(cls)->Pipeline:
        try:
            logging.info("Creating data transformation object")
            imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            processor:Pipeline=Pipeline([("Imputer",imputer)])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys)



    def initiate_data_transformation(self)->DataTransformationArtifact:
        logging.info("Entered initiate method of data transformation")
        try:
            logging.info("Reading training and testing files")
            train_df=DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            ##training dataframe
            input_data_train_df=train_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_data_train_df=train_df[TARGET_COLUMN]
            target_feature_train_df=target_data_train_df.replace(-1,0)
            ##testing dataframe
            input_data_test_df=test_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_data_test_df=test_df[TARGET_COLUMN]
            target_feature_test_df=target_data_test_df.replace(-1,0)
            preprocessor=self.get_data_transformation_obj()
            preprocessor_obj=preprocessor.fit(input_data_train_df)
            transform_feature_train_feature=preprocessor_obj.transform(input_data_train_df)
            transform_feature_test_feature=preprocessor_obj.transform(input_data_test_df)

            train_arr=np.c_[transform_feature_train_feature,np.array(target_feature_train_df)]
            test_arr=np.c_[transform_feature_test_feature,np.array(target_feature_test_df)]

            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,array=test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor_obj)

            #preparing artifact
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)