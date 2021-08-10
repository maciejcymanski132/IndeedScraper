import redis
import pandas as pd
from api.classes.ScraperClass import compress


def set_keys(re_con):
    df = pd.DataFrame(columns=['label','text'])
    re_con.set('undefined',compress(df))
    re_con.set('data scientist',compress(df))
    re_con.set('frontend developer',compress(df))
    re_con.set('software engineer',compress(df))
    re_con.set('tester',compress(df))
    re_con.set('dev ops',compress(df))
