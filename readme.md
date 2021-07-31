Selenium based webscraper api which takes in search key,number of offer pages to scrape and number of parallel workers to work on and return gathered work offers text for each worker as json.
Project is extended with small machine learning module which can tell what kind of industry given job is associated with.
Used technologies:
Python 3.9 (core)
Selenium 3.141 (gathering text data from site html)
Joblib 1.0.1 (responsible for parallel scraping of couple pages at once)
Redis 3.5.3 (saving gathered text data for machine learning purposes)
Scikit-learn 0.24.2 (machine learning prediction model)
