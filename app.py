import sys
import os
import certifi
ca=certifi.where()

from dotenv import load_dotenv
load_dotenv()
MONGO_DB_URL=os.getenv("MONGO_DB_URL")
import pymongo
from fastapi import Form
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.batch_pipeline import BatchPredictionPipeline
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,UploadFile,Request,File
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.feature_extractor import FeatureExtractor

from networksecurity.utils.main_utils.utils import save_object,load_object

client=pymongo.MongoClient(MONGO_DB_URL,tlsCAFile=ca)
from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME,DATA_INGESTION_DATABASE_NAME

database=client[DATA_INGESTION_DATABASE_NAME]
collection=database[DATA_INGESTION_COLLECTION_NAME]

app=FastAPI()
origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates=Jinja2Templates(directory="./templates")


@app.get("/",tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train",tags=["train"])
async def train_route():
    try:
        training_pipeline=TrainingPipeline()
        training_pipeline.run_pipeline()
        return Response("Training successful!!")
    except Exception as e:
        raise NetworkSecurityException(e,sys)

@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        os.makedirs("predicted_output", exist_ok=True)
        temp_path = "predicted_output/temp_input.csv"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Validate columns
        df_check = pd.read_csv(temp_path)
        required_cols = ['having_IP_Address', 'URL_Length', 'Shortining_Service',
                         'having_At_Symbol', 'double_slash_redirecting', 'Prefix_Suffix',
                         'having_Sub_Domain', 'SSLfinal_State', 'Domain_registeration_length',
                         'Favicon', 'port', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor',
                         'Links_in_tags', 'SFH', 'Submitting_to_email', 'Abnormal_URL',
                         'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe',
                         'age_of_domain', 'DNSRecord', 'web_traffic', 'Page_Rank',
                         'Google_Index', 'Links_pointing_to_page', 'Statistical_report']
        missing_cols = [col for col in required_cols if col not in df_check.columns]
        if missing_cols:
            return Response(f"Invalid CSV! Missing columns: {missing_cols}", status_code=400)

        # Run batch pipeline
        pipeline = BatchPredictionPipeline(input_file_path=temp_path)
        df = pipeline.run_pipeline()

        # Prepare response
        table_html = df.to_html(classes='table table-striped table-bordered')
        phishing_count = int((df['predicted_column'] == 1.0).sum())
        legit_count = int((df['predicted_column'] != 1.0).sum())
        total_count = len(df)

        return templates.TemplateResponse("tables.html", {
            "request": request,
            "table": table_html,
            "phishing_count": phishing_count,
            "legit_count": legit_count,
            "total_count": total_count
        })

    except Exception as e:
        raise NetworkSecurityException(e, sys)

@app.post("/predict_url")
async def predict_url(request: Request, url: str):
    try:
        # Extract features from URL
        extractor = FeatureExtractor(url)
        features = extractor.extract_all_features()

        # Convert to dataframe
        df = pd.DataFrame([features])

        # Predict
        preprocessor = load_object("file_saved/preprocessor.pkl")
        model = load_object("file_saved/model.pkl")
        network_model = NetworkModel(processor=preprocessor, model=model)
        prediction = network_model.predict(df)[0]

        preprocessor = load_object("file_saved/preprocessor.pkl")
        model = load_object("file_saved/model.pkl")
        network_model = NetworkModel(processor=preprocessor, model=model)

        # Get probability instead of just prediction
        x_transformed = preprocessor.transform(df)
        probability = model.predict_proba(x_transformed)[0]
        phishing_prob = round(probability[1] * 100, 2)

        prediction = network_model.predict(df)[0]
        result = "🚨 PHISHING" if prediction == 1.0 else "✅ LEGITIMATE"

        return {
            "url": url,
            "prediction": result,
            "phishing_probability": f"{phishing_prob}%",
            "features_extracted": features
        }

    except Exception as e:
        raise NetworkSecurityException(e, sys)

 
if __name__=="__main__":
    app_run(app,host="localhost",port=8000)

