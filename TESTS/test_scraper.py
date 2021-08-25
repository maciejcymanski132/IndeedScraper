from api.classes.ScraperClass import Scraper,decompress,compress,draw_proxy
from api.classes.proxies import proxy_list
import redis
import unittest
from selenium import webdriver
import selenium
import time


firefox_options = webdriver.FirefoxOptions()
firefox_options.headless = False
firefox_options.add_argument(f'--proxy-server={draw_proxy(proxy_list)}')


def setup_scraper():

    scraper = Scraper(search_key="test", worker_nr=0, location="")
    scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
    scraper.driver.get('https://indeed.com/jobs?q=test')
    return scraper


class TestScraper(unittest.TestCase):

    def test_next_page(self):
        """
        Test if scraper swaps to next page after using next_page by observing
        if url changes
        """
        scraper = setup_scraper()
        scraper.check_for_pop_up()
        scraper.close_privacy_agreement()
        scraper.next_page(time_limit=10)
        self.assertEqual('https://www.indeed.com/jobs?q=test&start=10',
                         scraper.driver.current_url[0:43])
        scraper.driver.close()

    def test_check_for_pop(self):
        """
        Test which closes screen popup after swapping to next page
        """
        scraper = setup_scraper()
        scraper.close_privacy_agreement()
        scraper.next_page(time_limit=10)
        time.sleep(3)
        scraper.check_for_pop_up()
        close_pop_up = scraper.driver.find_elements_by_id("popover-x")
        try:
            self.assertFalse(close_pop_up[0].is_displayed())
        except IndexError:
            raise Exception("Pop up havent appeared at all")
        scraper.driver.close()

    def test_close_privacy_agreement(self):
        """
        Test checking if privacy agreement still appears after closing it with
        check_for_pop_up() function
        """
        scraper = setup_scraper()
        scraper.check_for_pop_up()
        agreement = scraper.driver.find_elements_by_id("onetrust-banner-sdk")
        self.assertFalse(agreement)
        scraper.driver.close()
    #
    def test_find_offers(self):
        """
        Test checking if scraper can properly find resultCol with job offers
        """
        scraper = setup_scraper()
        results_column = scraper.driver.find_elements_by_id("resultsCol")
        results = results_column[0].find_elements_by_class_name("summary")
        if not results:
            results = results_column[0].find_elements_by_class_name(
                "jobCardShelfContainer"
            )
        self.assertTrue(results)
        scraper.driver.close()

    def test_open_offer(self):
        """
        Test if scraper open offers after using open_offer by observing
        if url changes
        """
        scraper = setup_scraper()
        offers = scraper.find_offers()
        url = scraper.driver.current_url
        offers.pop().click()
        self.assertFalse(url == scraper.driver.current_url)
        scraper.driver.close()

    def test_extract_description(self):
        """
        Test checks if scraper properly extract job description from opened offer
        """
        scraper = setup_scraper()
        offers = scraper.find_offers()
        offer = offers.pop(5)
        offer.click()
        try:
            job_desc = scraper.extract_description(time_limit=5)
            self.assertTrue(job_desc)
        except selenium.common.exceptions.NoSuchElementException:
            scraper.driver.close()
            raise Exception("Scraper failed at extracting job")
        scraper.driver.close()

    def test_save_job_description(self):
        """
        Test checks if save_job_description proceed properly and saves result
        to database
        """
        scraper = setup_scraper()
        offers = scraper.find_offers()
        offer = offers.pop()
        scraper.save_job_description(offer=offer,index=0)
        if not scraper.results["offers"]:
            scraper.save_job_description(offer=offers.pop(),index=1)
        self.assertTrue(scraper.results["offers"])
        scraper.driver.close()

    def test_scrape_page(self,timeout=10):
        """
        Test checking if scraping worked out and if results are saved in
        redis db
        """
        scraper = Scraper(search_key="test", worker_nr=0, location="")
        scraper.setup_driver(webdriver.Firefox(firefox_options=firefox_options))
        scraper.url = 'https://indeed.com/jobs?q=test'
        r = redis.Redis(host="127.0.0.1",port=6379)
        scraper.scrape_page(timeout=timeout, redis_connection=r)
        self.assertFalse(decompress(redis_con1.get("test")).empty)
        redis_con1.delete("test")
        scraper.driver.close()


if __name__ == '__main__':
    unittest.main()
