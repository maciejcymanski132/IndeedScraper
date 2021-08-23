from fastapi import FastAPI,Request
from os import environ
import uvicorn
from classes.ScraperClass import *
from scripts.setdb import set_keys
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="templates"), name="static")
redis_con=redis.Redis()
set_keys(redis_con)

learning_jobs = ["software engineer","data scientist","frontend developer",
                 "dev ops","tester"]


@app.get("/",response_class=HTMLResponse)
def read_root(request:Request):
    return templates.TemplateResponse('index.html',context={"request": request})


@app.get("/jobs")
async def jobs(workers: int = 1,pages: int=1,work: str=""):
    do_scraping(workers=workers,pages=pages,work=work)
    response={"job_offers": {job:{} for job in learning_jobs}}
    with open('ml_models/text_classifier', 'rb') as training_model:
        model = pickle.load(training_model)
    with open('ml_models/vectorizer', 'rb') as vectorizer:
        vectorizer = pickle.load(vectorizer)
    if work not in learning_jobs:
        result = decompress(redis_con.get('undefined'))
    else:
        result = decompress(redis_con.get(work))
    for index,row in result.iterrows():
        row.label = model.predict(vectorizer.transform([row.text]))
        response["job_offers"][row.label[0]].update({index:row.text})
    redis_con.delete('undefined')
    redis_con.set('undefined',compress(pd.DataFrame(columns=['label','text'])))
    try:
        redis_con.bgsave()
    except redis.exceptions.ResponseError:
        time.sleep(5)
        redis_con.bgsave()
    return response


if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=environ.get('PORT', 5000))