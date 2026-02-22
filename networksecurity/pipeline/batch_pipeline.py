import os
import sys
import pandas as pd
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

class BatchPredictionPipeline:
    def __init__(self, input_file_path: str):
        try:
            self.input_file_path = input_file_path
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self):
        try:
            logging.info("Starting batch prediction pipeline")
            
            # Load data
            df = pd.read_csv(self.input_file_path)
            logging.info(f"Loaded data with shape: {df.shape}")

            # Load model and preprocessor
            preprocessor = load_object("file_saved/preprocessor.pkl")
            model = load_object("file_saved/model.pkl")
            network_model = NetworkModel(processor=preprocessor, model=model)

            # Predict
            y_pred = network_model.predict(df)
            df['predicted_column'] = y_pred
            logging.info(f"Predictions done. Phishing count: {(y_pred==1).sum()}")

            # Save output
            os.makedirs("predicted_output", exist_ok=True)
            output_path = "predicted_output/output.csv"
            df.to_csv(output_path, index=False)
            logging.info(f"Predictions saved to {output_path}")

            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)