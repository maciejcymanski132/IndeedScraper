from selenium import webdriver
import unittest
import requests
import json


class TestApi(unittest.TestCase):

    def test_job_scraped(self):
        """
        Test if any job were scraped in this attempt
        """
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=software engineer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        for work in d.get('job_offers').keys():
            self.assertTrue(d.get('job_offers').get(work))


    def test_false_job_scraped(self):
        """
        Test if no jobs are scraped with invalid work description
        """
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=61621321'
        response = requests.get(test_url)
        d = json.loads(response.content)
        for work in d['job_offers'].keys():
            self.assertFalse(d.get('job_offers').get(work))


    def test_job_asserting(self):
        """
        Test if jobs scraped for 'software engineer' job description are properly
        asserted to category by ml model
        """
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=software engineer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        self.assertTrue(d.get('job_offers').get('software engineer'))

    def test_job_asserting1(self):
        """
        Test if jobs scraped for 'data scientist' job description are properly
        asserted to category by ml model
        """
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=data scientist'
        response = requests.get(test_url)
        d = json.loads(response.content)
        self.assertTrue(d.get('job_offers').get('data scientist'))

    def test_job_asserting2(self):
        """
        Test if jobs scraped for 'frontend developer' job description are properly
        asserted to category by ml model
        """
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=frontend developer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        self.assertTrue(d.get('job_offers').get('frontend developer'))

    def test_false_job_asserting(self):
        """
        Test if jobs scraped for 'frontend developer' job description are properly
        asserted to category by ml model (reverse test - opposite category)
        """
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=frontend developer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        self.assertFalse(d.get('job_offers').get('software engineer'))

    def test_false_job_asserting1(self):
        """
        Test if jobs scraped for 'software engineer' job description are properly
        asserted to category by ml model (reverse test - opposite category)
        """
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=software engineer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        self.assertFalse(d.get('job_offers').get('frontend developer'))


if __name__ == '__main__':
    unittest.main()