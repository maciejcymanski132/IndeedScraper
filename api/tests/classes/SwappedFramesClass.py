from selenium import webdriver
from selenium import common
import selenium,logging


class SwappedFrame:
    def __init__(self, driver: webdriver, worker_nr: int):
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
            job_desc_frame = self.driver.find_element_by_tag_name("iframe")
            self.driver.switch_to.frame(job_desc_frame)
        except selenium.common.exceptions.NoSuchElementException:
            logging.critical(f"Couldnt find job frame in {self.worker_nr}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.driver.switch_to.default_content()
        except selenium.common.exceptions.NoSuchWindowException:
            logging.critical(
                f"Cannot switch back to main frame in worker {self.worker_nr}"
            )
