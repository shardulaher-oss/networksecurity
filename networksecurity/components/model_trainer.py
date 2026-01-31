import os
import sys
import mlflow
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.logging.logger import logging
from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact

from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import  load_numpy_array_data,evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import classification_metric
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.ensemble import (RandomForestClassifier,AdaBoostClassifier,GradientBoostingClassifier)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,Data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=Data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def track_mlflow(self,best_model,classificationmetric):
        with mlflow.start_run():
            f1_score=classificationmetric.f1_score
            precision_score=classificationmetric.precision_score
            recall_score=classificationmetric.recall_score

            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision_score",precision_score)
            mlflow.log_metric("recall_score",recall_score)
            mlflow.sklearn.log_model("best_model",best_model)

    def train_model(self,X_train,y_train,X_test,y_test):
        models={
            "LogisticRegression":LogisticRegression(),
            "RandomForestClassfier":RandomForestClassifier(),
            "AdaBoostClassifier":AdaBoostClassifier(),
            "GradientBoostingClassifier":GradientBoostingClassifier(),
            "KNeighborsClassifier":KNeighborsClassifier(),  
            "DecisionTreeClassifier":DecisionTreeClassifier()
        }
        params={
            "DecisionTreeClassifier":{
                'criterion':['gini','entropy'],
                'max_depth':[3,5,10,15,20,25,30],
                'min_samples_split':[2,3,5,10]
            },
            "RandomForestClassfier":{
                'n_estimators':[50,100,200],
                'criterion':['gini','entropy'],
                'max_depth':[3,5,10,15],
            },
            "LogisticRegression":{},
            "KNeighborsClassifier":{
                'n_neighbors':[3,5,7,9,11],
                'weights':['uniform','distance'],
                'metric':['euclidean','manhattan','minkowski']
            },
            "GradientBoostingClassifier":{
                'learning_rate':[0.01,0.1,0.2,0.3],
                'n_estimators':[50,100,200],
                'subsample':[0.6,0.7,0.8,0.9,1.0]
            },
            "AdaBoostClassifier":{
                'n_estimators':[50,100,200],
                'learning_rate':[0.01,0.1,0.2,0.3,0.5,1.0]
            }
        }
        model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=X_test,y_test=y_test,models=models,params=params)

        best_model_score=max(model_report.values())

        best_model_name=list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model=models[best_model_name]
        y_train_pred=best_model.predict(X_train)

        classification_train_metric=classification_metric(y_true=y_train,y_pred=y_train_pred)

        y_test_pred=best_model.predict(X_test)

        classification_test_metric=classification_metric(y_true=y_test,y_pred=y_test_pred)

        self.track_mlflow(best_model,classification_train_metric)
        self.track_mlflow(best_model,classification_test_metric)
        processor=load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
        model_dir_path=os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        Network_Model=NetworkModel(processor=processor,model=best_model)

        save_object(file_path=self.model_trainer_config.trained_model_file_path,obj=Network_Model)

        modeltrainerartifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric)
        
        logging.info(f"Model Trainer artifact:{modeltrainerartifact}")
        return modeltrainerartifact
        

    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path=self.data_transformation_artifact.transformed_train_file_path
            test_file_path=self.data_transformation_artifact.transformed_test_file_path

            train_arr=load_numpy_array_data(train_file_path)
            test_arr=load_numpy_array_data(test_file_path)

            X_train,y_train,X_test,y_test=(
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1]
            )
        
            model=self.train_model(X_train,y_train,X_test,y_test)
            return model
        except Exception as e:
            raise NetworkSecurityException(e,sys)
