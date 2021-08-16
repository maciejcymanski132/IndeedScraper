from api.classes.ScraperClass import Scraper
import redis
import unittest
from selenium import webdriver
import selenium
import time

firefox_options = webdriver.FirefoxOptions()
redis_con = redis.Redis()

class TestScraper(unittest.TestCase):

    def test_next_page(self):
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(executor='http://127.0.0.1:4444/wd/hub' )
        scraper.driver.get('https://pl.indeed.com/jobs?q=test')
        time.sleep(5)
        scraper.check_for_pop_up()
        scraper.close_privacy_agreement()
        time.sleep(5)
        scraper.next_page()
        time.sleep(5)
        self.assertEqual(scraper.driver.current_url,
                         'https://pl.indeed.com/jobs?q=test&start=10')
        scraper.driver.close()

    # def test_check_for_pop(self):
    #     scraper = Scraper(search_key="test",worker_nr=0,location="")
    #     scraper.driver.get('https://pl.indeed.com/jobs?q=test')
    #     scraper.next_page()
    #     time.sleep(10)
    #     scraper.check_for_pop_up()
    #     try:
    #         close_pop_up = scraper.driver.find_element_by_id("popover-x")
    #         return 0
    #     except selenium.common.exceptions.NoSuchElementException:
    #         return 1


if __name__ == '__main__':
    print('ee')