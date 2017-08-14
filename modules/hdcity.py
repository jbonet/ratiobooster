# -*- coding: utf-8 -*-

from base import BaseParser
from libs.torrent import Torrent
from lxml import html
from StringIO import StringIO

import datetime
import requests

class Parser(BaseParser):
    """Parser for HDCity torrent list"""

    def __init__(self, config=None, logger=None, name=""):
        super(Parser, self).__init__(logger, name)
        self.config = config
        self.baseUrl = 'https://www.hdcity.li/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Host': 'hdcity.li',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'es-ES,es;q=0.8',
            'Referer': 'https://hdcity.li/',
            'Cookie': config["cookie"]
            }
        self.logger = logger

    def parse(self):
        url = '{baseUrl}index.php?page=torrents'.format(baseUrl=self.baseUrl)
        r = requests.get(url, headers=self.headers)
        if not r.status_code == 200:
            return []

        tree = html.fromstring(r.content)
        
        for element in tree.xpath('//*[@class="b-content"]/table/tr'):
            print html.tostring(element)

        #print html.tostring(tree.xpath('.//*[@class="b-content"]/table')[0])

        for index in enumerate([1]):
            # Ignore first row (Headers)
            if index == 0:
                continue


        results = []
        return results