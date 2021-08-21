from selenium import webdriver
import unittest
import requests
import json

class TestApi(unittest.TestCase):

    def test_job_scraped(self):
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=software engineer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        for work in d['job_offers'].keys():
            if d['job_offers'][work]:
                return 1
        return 0

    def test_false_job_scraped(self):
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=61621321'
        response = requests.get(test_url)
        d = json.loads(response.content)
        for work in d['job_offers'].keys():
            if d['job_offers'][work]:
                return 0
        return 1

    def test_job_asserting(self):
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=software engineer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        if not d['job_offers']['software engineer']:
            return 0
        return 1

    def test_job_asserting1(self):
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=data scientist'
        response = requests.get(test_url)
        d = json.loads(response.content)
        if not d['job_offers']['data scientist']:
            return 0
        return 1

    def test_job_asserting2(self):
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=frontend developer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        if not d['job_offers']['frontend developer']:
            return 0
        return 1

    def test_false_job_asserting(self):
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=frontend developer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        if not d['job_offers']['software engineer']:
            return 1
        return 0

    def test_false_job_asserting1(self):
        test_url = 'http://127.0.0.1:5000/jobs?workers=2&pages=2&work=software engineer'
        response = requests.get(test_url)
        d = json.loads(response.content)
        if not d['job_offers']['frontend developer']:
            return 1
        return 0


if __name__ == '__main__':
    unittest.main()