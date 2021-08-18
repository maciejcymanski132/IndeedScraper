#IndeedScraper

Webscraping tool consisting 3 modules
- Selenium Server container
- Redis Server container
- API container

Application uses selenium to synchronously scrape job offers from 
indeed.com with couple of browsers opened.
Job offers are analysed by ml model and assigned to particular job type like
(software engineer,frontend developer,data scientist etc.)\
For now its recommended to look only for IT-related job offers
because ml model haven't been taught other industries job decsriptions.

Technologies used in project:

- Python
- Selenium
- Joblib
- Docker/Docker-compose
- TravisCI
- Redis
