from fastapi import FastAPI
from ScraperClass import *
import pandas as pd

app = FastAPI()


learning_jobs = ["software engineer","data scientist","frontend developer",
                 "dev ops","tester"]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/jobs")
async def jobs(workers: int = 1,pages: int=1,work: str=""):
    do_scraping(workers=workers,pages=pages,work=work)
    my_d={"job_offers": {job:{} for job in learning_jobs}}
    print(my_d)
    with open('text_classifier', 'rb') as training_model:
        model = pickle.load(training_model)
    with open('vectorizer', 'rb') as vectorizer:
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
    except:
        redis_con.bgsave()
    return my_d


if __name__ == '__main__':
    pass