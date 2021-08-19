from api.classes.ScraperClass import Scraper,decompress,compress

import redis
import unittest
from selenium import webdriver
import selenium
import time

firefox_options = webdriver.FirefoxOptions()
firefox_options.headless = True
redis_con1 = redis.Redis(port=6379)

class TestScraper(unittest.TestCase):

    def test_next_page(self):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.driver.get('https://indeed.com/jobs?q=test')
        scraper.check_for_pop_up()
        scraper.close_privacy_agreement()
        scraper.next_page(time_limit=10)
        self.assertEqual('https://www.indeed.com/jobs?q=test&start=10',
                         scraper.driver.current_url[0:43],"nice")
        scraper.driver.close()

    def test_check_for_pop(self):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.driver.get('https://indeed.com/jobs?q=test')
        scraper.close_privacy_agreement()
        scraper.next_page(time_limit=10)
        time.sleep(5)
        scraper.check_for_pop_up()
        try:
            close_pop_up = scraper.driver.find_element_by_id("popover-x")
            scraper.driver.close()
            return 0
        except selenium.common.exceptions.NoSuchElementException:
            scraper.driver.close()
            return 1

    def test_close_privacy_agreement(self):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.driver.get('https://indeed.com/jobs?q=test')
        scraper.check_for_pop_up()
        try:
            agreement = scraper.driver.find_element_by_id("onetrust-banner-sdk")
            scraper.driver.close()
            return 0
        except selenium.common.exceptions.NoSuchElementException:
            scraper.driver.close()
            return 1

    def test_find_offers(self):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.driver.get('https://indeed.com/jobs?q=test')
        try:
            results_column = scraper.driver.find_element_by_id("resultsCol")
            results = results_column.find_elements_by_class_name("summary")
            if not results:
                results = results_column.find_elements_by_class_name(
                    "jobCardShelfContainer"
                )
            scraper.driver.close()
            return 1
        except selenium.common.exceptions.NoSuchElementException as exception:
            scraper.driver.close()
            return 0

    def test_open_offer(self):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.driver.get('https://indeed.com/jobs?q=test')
        offers = scraper.find_offers()
        url = scraper.driver.current_url
        offers.pop().click()
        self.assertFalse(url==scraper.driver.current_url)

    def test_extract_description(self):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.driver.get('https://indeed.com/jobs?q=test')
        offers = scraper.find_offers()
        offer = offers.pop()
        offer.click()
        try:
            job_desc = scraper.extract_description(time_limit=5)
            scraper.driver.close()
            return 1
        except selenium.common.exceptions.NoSuchElementException:
            scraper.driver.close()
            return 0

    def test_save_job_description(self):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.driver.get('https://indeed.com/jobs?q=test')
        offers = scraper.find_offers()
        offer = offers.pop()
        scraper.save_job_description(offer=offer,index=0)
        if not scraper.results["offers"]:
            scraper.save_job_description(offer=offers.pop(),index=1)
        if not scraper.results["offers"]:
            return False
        return True

    def test_scrape_page(self,timeout=10):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.url = 'https://indeed.com/jobs?q=test'
        scraper.scrape_page(timeout= timeout,redis_con =redis_con1)
        if decompress(redis_con1.get('undefined')).empty:
            return 1
        return 0

if __name__ == '__main__':
    unittest.main()