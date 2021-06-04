import time
import selenium
from selenium import webdriver, common
from selenium.webdriver.common.by import By


class Scraper():

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.search_field = 'python'
        self.location = ''
        self.pages_scraped = 1
        # self.search_field = input('Name of job youre looking for:\n')
        # self.location = input('Where do you live?\n')
        # self.pages_scraped = int(input('How many pages of indeed you want to scrape?\n'))
        self.url = f'https://indeed.com/jobs?q={self.search_field}&l={self.location}'

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
            time.sleep(3)
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
            close_pop_up = self.driver.find_element_by_id("popover-x")
            close_button = close_pop_up.find_element_by_tag_name("button")
            close_button.click()
            time.sleep(2)
        except selenium.common.exceptions.NoSuchElementException:
            pass

    def find_offers(self):
        """
        Function gathers job offer hyperlinks to job offers
        :return: Function return job offer hyperlinks as selenium webdriver objects
                 but if searced element was not found it raises exception 'Wrong url'
        """
        try:
            results_column = self.driver.find_element_by_id("resultsCol")
            results = results_column.find_elements_by_class_name("title")
            return results
        except selenium.common.exceptions.NoSuchElementException:
            raise Exception('Wrong url')

    def get_offer_content(self, offer):
        """
        Function checks if after clicking new offer hyperlink url changes
        and then extract job description
        :param offer: Selenium webdriver clickable object (job offer hyperlink)
        :return: Element or list of elements (dependent on structure of job offer)
                 containing job description
        """
        current_url = self.driver.current_url
        new_url = current_url
        while current_url == new_url:
            offer.click()
            time.sleep(2)
            new_url = self.driver.current_url
        time.sleep(2)
        job_desc_frame = self.driver.find_element_by_tag_name('iframe')
        self.driver.switch_to.frame(job_desc_frame)
        job_desc = self.driver.find_elements_by_xpath('//div[@id="jobDescriptionText"]/*/*')
        return job_desc

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
            time.sleep(1)
            page_list[-1].click()
            time.sleep(2)
        except selenium.common.exceptions.NoSuchElementException:
            raise Exception('Wrong url')

    def scrape_page(self, handle):
        time.sleep(2)
        self.check_for_pop_up()
        offer_hrefs = self.find_offers()
        for offer in offer_hrefs:
            job_desc = self.get_offer_content(offer)
            time.sleep(2)
            handle.write('\n\n'+'----------------------------'*3+'\n\n')
            for element in job_desc:
                if element.text:
                    handle.write(element.text)
                    handle.write('\n')
            self.driver.switch_to.default_content()


    def scrape_website(self):
        """
        Function open up desired website with given webdriver, insert parameters
        job_searched and location into url that will be retrieved by driver.get()
        and then opens up file where result of scraping will be saved
        to begin scraping
        :return: Function doesn't have particular return value
        """
        self.driver.get(self.url)
        self.close_privacy_agreement()
        with open('results.txt', mode='w', encoding='utf8') as handle:
            for _ in range(0, self.pages_scraped):
                self.scrape_page(handle)
                self.next_page()


if __name__ == '__main__':

    scraper = Scraper()
    scraper.scrape_website()
    scraper.driver.close()