import time
from selenium.webdriver.support.ui import WebDriverWait
import selenium
from selenium import common
from seleniumwire import webdriver
from joblib import Parallel,delayed
import os
import random
import logging
from proxies import proxy_list


used_proxies = []


class SwappedFrame:

    def __init__(self, driver, worker_nr):
        """
        Context manager moving driver to inner html containing job description
        and exiting when wanted action is done
        :param driver: Selenium WebDriver
        :param worker_nr: Number of Worker (log purposes)
        """
        self.driver = driver
        self.worker_nr = worker_nr

    def __enter__(self):
        try:
            job_desc_frame = self.driver.find_element_by_tag_name('iframe')
            self.driver.switch_to.frame(job_desc_frame)
        except selenium.common.exceptions.NoSuchElementException:
            logging.critical(f'Cannot find opened job offer in {self.worker_nr}')

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.driver.switch_to.default_content()
        except selenium.common.exceptions.NoSuchWindowException:
            logging.critical("Cannot return to default content")


class Scraper:

    def __init__(self, worker_nr):
        self.search_field = 'python'
        self.location = ''
        # self.search_field = input('Name of job youre looking for:\n')
        # self.location = input('Where do you live?\n')
        self.url = f'https://indeed.com/jobs?q={self.search_field}&l={self.location}&start={worker_nr}0'
        self.worker_nr = worker_nr
        self.proxy = proxy_list[random.randint(0,len(proxy_list)-1)]
        self.driver = webdriver.Firefox(seleniumwire_options=self.proxy)
        if self.proxy not in used_proxies:
            used_proxies.append(self.proxy)
        else:
            while self.proxy in used_proxies:
                    self.proxy = proxy_list[random.randint(0, len(proxy_list)-1)]

        logging.basicConfig(filename=f'LOG-{self.worker_nr}',
                            level=logging.WARNING
                            , format='%(asctime)s:%(levelname)s:%(message)s')

    def close_privacy_agreement(self):
        """
        Function closes privacy agreement element
        after it pops up at first entrance on the website
        :return: Function doesn't have any final outcome in return and if element
                 was not found it will proceed to next stage
        """
        try:
            while self.driver.current_url == 'about:blank':
                time.sleep(1)
            privacy_agreement = self.driver.find_element_by_id("onetrust-banner-sdk")
            privacy_agreement_button = privacy_agreement.find_element_by_id(
                                                "onetrust-accept-btn-handler")
            privacy_agreement_button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass

    def check_for_pop_up(self):
        """
        Function check website for presence of notification pop-up
        which appears from time to time while scraping website and closes it.
        :return: Function doesn't have any final outcome in return and if element
                 was not found it will proceed to next stage
        """
        try:
            time.sleep(3)
            close_pop_up = self.driver.find_element_by_id("popover-x")
            close_button = close_pop_up.find_element_by_tag_name("button")
            close_button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass

    def next_page(self):
        """
        Function finds navigation element responsible for switching cards in
        result column and then clicks button 'next_page'
        :return: Function doesn't have any final outcome in return and if element
                 was not found it will raise exception 'Wrong url'
        """
        try:
            navigation = self.driver.find_element_by_class_name("pagination-list")
            page_list = navigation.find_elements_by_tag_name("a")
            page_list[-1].click()
            time.sleep(3)
        except selenium.common.exceptions.NoSuchElementException:
            raise Exception('Wrong url or you have been blocked')

    def find_offers(self):
        """
        Function gathers job offer hyperlinks to job offers
        :return: Function return job offer hyperlinks as selenium webdriver objects
                 but if searced element was not found it raises exception 'Wrong url'
        """
        try:
            results_column = self.driver.find_element_by_id("resultsCol")
            results = results_column.find_elements_by_class_name("title")
            if not results:
                results = results_column.find_elements_by_class_name("resultContent")
            return results
        except selenium.common.exceptions.NoSuchElementException:
            logging.critical("Couldnt find results column")
            raise Exception('Wrong url or you have been blocked')

    def open_offer(self, offer, time_limit):
        """
        Function attempts to open next offer for given time_limit and if didnt
        proceed logs warning with problematic url and worker_nr for further
        investigation
        :param offer: hyperlink for next job offer
        :param time_limit: Time limit opening new offer (seconds)
        :return: Function doesnt return anything
        """
        current_url = self.driver.current_url
        timeout = time.time()+time_limit
        while current_url == self.driver.current_url:
            offer.click()
            time.sleep(1)
            if time.time() > timeout:
                logging.warning(
                    f"Cannot open offer in worker_nr{self.worker_nr}\n"
                    f"Problematic url:{self.driver.current_url}")
                return False
        return True

    def extract_description(self,time_limit):
        """
        Function extracts description from offer.
        Attempts to extract offer description for given time limit, after that
        logs warning into worker's log file (contains problematic url
        for further investigation) and break loop.
        :param time_limit: Time limit for extracting description (seconds)
        :return: Function returns webdriver element containing offer
        description or empty string if operation didnt succeed
        """
        job_desc = ""
        timeout = time.time() + time_limit
        while not job_desc:
            try:
                if time.time() > timeout:
                    logging.warning(f"Couldnt find description in this offer{self.driver.current_url}")
                    job_desc = f"Couldnt find description in this offer{self.driver.current_url}"
                    break
                job_desc = self.driver.find_element_by_id("jobDescriptionText")
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(2)
        return job_desc

    def save_job_description(self, offer,worker_result):
        """
        Functions moves webdriver to inner html containing job offer
        description and then gets offer description with open offer and
        extract description functions.t
        :param offer: Selenium webdriver clickable object (job offer hyperlink)
        :param worker_result: Handle to worker's txt file
        :return: Returns webdriver element containing offer description
        """
        if not self.open_offer(offer,time_limit=5):
            logging.error("Couldnt open new offer. Skipping to next one")
            return 0
        with SwappedFrame(self.driver,self.worker_nr):
            self.check_for_pop_up()
            job_desc = self.extract_description(time_limit=5)
            time.sleep(1)
            worker_result.write('\n\n' + '----------------------------' * 3 + '\n\n')
            try:
                if job_desc.text:
                    worker_result.write(job_desc.text)
                    worker_result.write('\n')
            except AttributeError:
                worker_result.write(job_desc)

    def scrape_page(self):
        self.driver.get(self.url)
        self.check_for_pop_up()
        offer_hrefs = self.find_offers()
        with open(f'result{self.worker_nr}.txt', mode='w', encoding='utf8') as worker_result:
            for i in range(0, len(offer_hrefs)):
                self.save_job_description(offer_hrefs[i],worker_result)
                if i % 5 == 0:
                    time.sleep(random.randint(5, 10))
                time.sleep(2)
        self.driver.close()

    def merge_results(self):
        """
        Function append worker's results to main result text file
        :return: Function doesn't have any final outcome in return
        """
        with open(f"result{self.worker_nr}.txt",mode='r', encoding='utf8') as worker_result:
            with open("results.txt",mode='a', encoding='utf8') as global_result:
                worker_results = worker_result.read()
                global_result.write(worker_results)
        os.remove(f'result{self.worker_nr}.txt')


def scrap_parallelly(i):
    scraper = Scraper(i)
    scraper.scrape_page()
    scraper.merge_results()


if __name__ == '__main__':
    Parallel(n_jobs=5, verbose=100,pre_dispatch='2*n_jobs',batch_size='auto')(delayed(scrap_parallelly)(i) for i in range(0,5))
