from selenium import common
from joblib import Parallel, delayed
from classes.proxies import proxy_list
import pickle, random,  time, zlib
import pandas as pd
import redis
from classes.SwappedFramesClass import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os

compressed_df = zlib.compress(pickle.dumps(pd.DataFrame()))
used_proxies = []
result_dict = {}
firefox_options = webdriver.FirefoxOptions()

redis_con = redis.Redis(host='redis')


def compress(dataframe: pd.DataFrame) -> compressed_df:
    """
    Function compresses given dataframe for redis-friendly format
    :param dataframe: Dataframe to be compressed
    :return: Compressed dataframe
    """
    return zlib.compress(pickle.dumps(dataframe))


def decompress(dataframe: compressed_df) -> pd.DataFrame:
    """
    Function decompresses given dataframe to make it accesible by user
    :param dataframe: Dataframe pickled and compressed
    :return: Decompressed dataframe
    """
    return pickle.loads(zlib.decompress(dataframe))


def draw_proxy(proxy_list: list) -> str:
    """
    Function draws single proxy from delivered proxy list if proxy isn't
    currently used by other worker
    :param proxy_list: List containing proxy server IP's
    :return: Single string containing one proxy IP
    """
    proxy = proxy_list[random.randint(0, len(proxy_list) - 1)]
    if proxy not in used_proxies:
        used_proxies.append(proxy)
    else:
        while proxy in used_proxies:
            if len(used_proxies) == len(proxy_list):
                logging.critical("All proxied are used right now")
                break
            proxy = proxy_list[random.randint(0, len(proxy_list) - 1)]
    return proxy


class Scraper:

    def __init__(self, worker_nr: int, search_key: str, location: str):
        self.search_field = search_key
        self.location = location
        self.worker_nr = worker_nr
        self.url = f"https://indeed.com/jobs?q={self.search_field}&l={self.location}&start={self.worker_nr}0"
        self.proxy = draw_proxy(proxy_list)
        self.driver = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                options=firefox_options)
        self.results = {"label": self.search_field, "offers": []}
        logging.basicConfig(
            filename=f"../Logs",
            level=logging.WARNING,
            format="%(asctime)s:%(levelname)s:%(message)s",
        )

    def close_privacy_agreement(self) -> None:
        """
        Function closes privacy agreement element
        after it pops up at first entrance on the website
        :return: Function doesn't have any final outcome in return and if element
                 was not found it will proceed to next stage
        """
        try:
            while self.driver.current_url == "about:blank":
                time.sleep(1)
            privacy_agreement = self.driver.find_element_by_id("onetrust-banner-sdk")
            privacy_agreement_button = privacy_agreement.find_element_by_id(
                "onetrust-accept-btn-handler"
            )
            privacy_agreement_button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass

    def check_for_pop_up(self) -> None:
        """
        Function check website for presence of notification pop-up
        which appears from time to time while scraping website and closes it.
        :return: Function doesn't have any final outcome in return and if element
                 was not found it will proceed to next stage
        """
        try:
            time.sleep(2)
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
            time.sleep(1)
        except selenium.common.exceptions.NoSuchElementException as exception:
            raise Exception(
                f"Function: next_page() havent proceed in worker{self.worker_nr}"
                f"Exception:{exception}"
            )

    def find_offers(self):
        """
        Function gathers job offer hyperlinks to job offers
        :return: Function return job offer hyperlinks as selenium webdriver objects
                 but if searced element was not found it raises exception 'Wrong url'
        """
        results_column = ""
        while not results_column:
            try:
                results_column = self.driver.find_element_by_id("resultsCol")
                results = results_column.find_elements_by_class_name("summary")
                if not results:
                    results = results_column.find_elements_by_class_name(
                        "jobCardShelfContainer"
                    )
                return results
            except selenium.common.exceptions.NoSuchElementException as exception:
                logging.critical(
                    f"Function: find_offers() havent proceed in worker{self.worker_nr}"
                    f"Exception:{exception}"
                )
                self.proxy = draw_proxy(proxy_list)
                self.driver.close()
                self.driver = webdriver.Firefox()
                self.scrape_page(timeout=10)

    def open_offer(self, offer, time_limit: int) -> bool:
        """
        Function attempts to open next offer for given time_limit and if didnt
        proceed logs warning with problematic url and worker_nr for further
        investigation
        :param offer: hyperlink for next job offer
        :param time_limit: Time limit opening new offer (seconds)
        :return: Function doesnt return anything
        """
        current_url = self.driver.current_url
        timeout = time.time() + time_limit
        while current_url == self.driver.current_url:
            offer.click()
            time.sleep(1)
            if time.time() > timeout:
                logging.warning(
                    f"Function: open_offer() havent proceed in worker{self.worker_nr}"
                )
                return False
        return True

    def extract_description(self, time_limit: int):
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
                    logging.warning(
                        f"Function: extract_description() havent proceed in worker{self.worker_nr}"
                        f"Couldnt find description in this offer{self.driver.current_url}"
                    )
                    break
                job_desc = self.driver.find_element_by_id("jobDescriptionText")
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(2)
        return job_desc

    def save_job_description(self, offer, index: int) -> None:
        """
        Functions moves webdriver cursor to inner html containing job offer
        description,extracts job description with open_offer function and
        saves it to self.results parameter
        :param offer: Selenium webdriver clickable object (job offer hyperlink)
        :param index: Number of offer on this page (required for odd behaviour
        of first offer on page)
        :return: Function doesnt return any value only manipulates class object
        self.results
        """
        if index == 0:
            offer.click()
        else:
            if not self.open_offer(offer, time_limit=5):
                logging.error(
                    f"Function: open_offer() havent proceed in worker{self.worker_nr}"
                    f"Skipping to next offer"
                )
                return None
        with SwappedFrame(self.driver, self.worker_nr):
            self.check_for_pop_up()
            job_desc = self.extract_description(time_limit=5)
            time.sleep(1)
            try:
                if job_desc.text and len(job_desc.text) > 10:
                    self.results["offers"].append(job_desc.text)
            except AttributeError:
                self.results["offers"].append(job_desc)

    def scrape_page(self, timeout: int) -> None:
        """
        Function uses class functions to execute scraping single page procedure.
        :param timeout: Time given for page to load (seconds)
        :return:
        """
        self.driver.get(self.url)
        self.driver.set_page_load_timeout(timeout)
        self.check_for_pop_up()
        offer_hrefs = self.find_offers()
        for i in range(0, 2):
            self.save_job_description(offer_hrefs[i], index=i)
            if i % 5 == 0:
                time.sleep(random.randint(5, 8))
            time.sleep(3)
        self.save_results()
        self.driver.close()

    def save_results(self) -> None:
        """
        Functions add results of this worker to pandas dataframe
        assigned to this particular search inside of redis db server.
        :return: Function doesn't have any final outcome in return
        """
        try:
            search_df = decompress(redis_con.get(self.search_field))
            db_docs = [doc for doc in search_df["text"]]
            for doc in self.results["offers"]:
                if doc not in db_docs:
                    search_df = search_df.append(
                        {"label": self.search_field, "text": doc}, ignore_index=True
                    )
            search_df = compress(search_df)
            redis_con.set(self.search_field, search_df)
            while True:
                try:
                    redis_con.bgsave()
                    break
                except redis.exceptions.ResponseError:
                    time.sleep(5)
        except TypeError:
            search_df = decompress(redis_con.get("undefined"))
            for doc in self.results["offers"]:
                search_df = search_df.append(
                    {"label": "undefined", "text": doc}, ignore_index=True
                )
            search_df = compress(search_df)
            redis_con.set("undefined", search_df)
            redis_con.bgsave()


def scrape(page: int, work: str) -> None:
    """
    Function designed to be passed to Parallel module of joblib library
    When passed to Parallel function it creates given number of scraper objects
    and begin scraping procedure
    :param page:Number of page that worker has to scrape
    :param work:Searched job description
    :return:
    """

    scraper = Scraper(worker_nr=page, search_key=work, location="")

    try:
        scraper.scrape_page(timeout=10)
    except selenium.common.exceptions.StaleElementReferenceException:
        logging.critical(
            f"Page lost its content during the work in {scraper.worker_nr}"
        )
    except selenium.common.exceptions.WebDriverException:
        scraper.driver.close()
        scraper.driver = webdriver.Firefox()
        scraper.proxy = draw_proxy(proxy_list)
        scraper.scrape_page(timeout=10)
    else:
        logging.error(f"Scraping took too long in worker {scraper.worker_nr}")


def do_scraping(workers: int, pages: int, work: str):
    """
    Function is responsible for parallel scraping of given number of pages at once.
    :param workers: Number of workers (parallel processes)
    :param pages: Number of pages to be scraped
    :param work: Searched job description
    """

    Parallel(n_jobs=workers, verbose=100, pre_dispatch="2*n_jobs", batch_size="auto")(
        delayed(scrape)(page, work) for page in range(0, pages)
    )


if __name__ == "__main__":
    print(proxy_list)
