import sys
import os
import certifi
ca=certifi.where()

from dotenv import load_dotenv
load_dotenv()
MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,UploadFile,Request,File
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

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
async def predict_route(request:Request,file:UploadFile=File(...)):
    try:
        df=pd.read_csv(file.file)
        preprocessor=load_object("file_saved/preprocessor.pkl")
        final_model=load_object("file_saved/model.pkl")
        network_model=NetworkModel(processor=preprocessor,model=final_model)
        print(df.iloc[0])
        y_pred=network_model.predict(df)
        print(y_pred)
        df['predicted_column']=y_pred
        print(df["predicted_column"])
        os.makedirs("predicted_output", exist_ok=True)
        df.to_csv("predicted_output/output.csv")
        table_html=df.to_html(classes='table table-striped')
        return templates.TemplateResponse("tables.html", {"request": request, "table": table_html})    
    except Exception as e:
        raise NetworkSecurityException(e,sys)
 
if __name__=="__main__":
    app_run(app,host="localhost",port=8000)