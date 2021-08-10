import redis
import pandas as pd
from api.classes.ScraperClass import compress


re_con = redis.Redis()

df = pd.DataFrame(columns=['label','text'])
re_con.set('undefined',compress(df))
re_con.set('data scientist',compress(df))
re_con.set('frontend developer',compress(df))
re_con.set('software engineer',compress(df))
re_con.set('tester',compress(df))
re_con.set('dev ops',compress(df))
