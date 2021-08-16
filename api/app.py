from fastapi import FastAPI
from classes.ScraperClass import *
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scripts.setdb import set_keys

app = FastAPI()
set_keys(redis_con)

learning_jobs = ["software engineer","data scientist","frontend developer",
                 "dev ops","tester"]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/jobs")
async def jobs(workers: int = 1,pages: int=1,work: str=""):
    do_scraping(workers=workers,pages=pages,work=work)
    my_d={"job_offers": {job:{} for job in learning_jobs}}
    with open('ml_models/text_classifier', 'rb') as training_model:
        model = pickle.load(training_model)
    with open('ml_models/vectorizer', 'rb') as vectorizer:
        vectorizer = pickle.load(vectorizer)

    if work not in learning_jobs:
        result = decompress(redis_con.get('undefined'))
    else:
        result = decompress(redis_con.get(work))

    for index,row in result.iterrows():
        print(model.predict(vectorizer.transform([row.text])))
        row.label = model.predict(vectorizer.transform([row.text]))
        my_d["job_offers"][row.label[0]].update({index:row.text})

    redis_con.delete('undefined')
    redis_con.set('undefined',compress(pd.DataFrame(columns=['label','text'])))
    try:
        redis_con.bgsave()
    except redis.exceptions.ResponseError:
        time.sleep(5)
        redis_con.bgsave()
    return my_d


@app.get('/test')
def read_d():
    print(redis_con.ping())
    print('dziala')
    return {"Hello": "World"}
