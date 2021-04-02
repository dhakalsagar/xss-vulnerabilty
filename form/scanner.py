#!/usr/bin/env pytho

import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
 
 
class Scanner:
    def __init__(self, url, ignore_links):
        self.target_url = url
        self.target_links = []
        self.session = requests.Session()
        self.links_to_ignore = ignore_links
 
    def extract_links_from(self, url):
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"', response.content.decode('utf-8', 'ignore'))
 
    def crawl(self, url=None):
        if url is None:
            url = self.target_url
        href_links = self.extract_links_from(url)
        for link in href_links:
            link = urlparse.urljoin(url, link)
 
            if "#" in link:
                link = link.split("#")[0]
 
            if self.target_url in link and link not in self.target_links and link not in self.links_to_ignore:
                self.target_links.append(link)
                print(link)
                self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.content, features="html.parser")
        return parsed_html.findAll("form")

    def submit_form(self, form, value, url):
        action = form.get("action")
        post_url = urlparse.urljoin(url, action)
        method = form.get("method")

        input_list = form.findAll("input")
        post_data = {}
        for input in input_list:
            input_name = input.get("name")
            input_type = input.get("type")
            input_value = input.get("value")
            if input_type == "text":
                input_value = value


            post_data[input_name] = input_value
        if method == "post":    
            return self.session.post(post_url, data=post_data)
        return self.session.get(post_url, params=post_data)

    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                print("[+] testing form in " + link)
            if "=" in link:
                print("[+] testing " + link)


    def test_xss_in_form(self, form, url):
        test_xss_script = "<sCript>alert('test')</scriPt>"
        response = self.submit_form(form, test_xss_script, url)
        if test_xss_script in response.text:
            return True