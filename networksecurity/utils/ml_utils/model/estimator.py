from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR,MODEL_FILE_NAME
import sys

class NetworkModel:
    def __init__(self,processor,model):
        try:
            self.processor=processor
            self.model=model
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def predict(self,x):
        try:
            x_transform=self.processor.transform(x)
            y_hat=self.model.predict(x_transform)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e,sys)