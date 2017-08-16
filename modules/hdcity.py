# coding=utf-8

from base import BaseParser
from libs.torrent import Torrent
from defusedxml import lxml
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
        self.logger.i("Checking HDCity torrents")
        url = '{baseUrl}index.php?page=torrents'.format(baseUrl=self.baseUrl)
        r = requests.get(url, headers=self.headers)
        if not r.status_code == 200:
            return []

        tree = lxml.parse(StringIO(r.content), parser=html.HTMLParser())
        results = []
        for index, row  in enumerate(tree.xpath('// form[@name="deltorrent"]/tr/td/table/tr')):
            # Ignore first row (Headers) and last (Empty row)
            if index == 0 or index == 36:
                continue
            title = row.xpath('./td[2]/a/text()')[0].lstrip()
            freeleech = True if row.xpath('./td[2]/img[@title="Gold 100% Free"]') else False
            seeders = self.checkOrZero(row.xpath('./td[6]/a/text()'))
            leechers = self.checkOrZero(row.xpath('./td[7]/a/text()'))
            completed = self.checkOrZero(row.xpath('./td[8]/a/text()'))      
            link = row.xpath('./td[3]/a/@href')[0]
            uploadedAt = row.xpath('./td[5]/text()')
            date = datetime.datetime.strptime(
                uploadedAt[0].encode('utf-8'), '%d/%m/%Y')

            results.append(Torrent(title=title, link=link, freeleech=freeleech, seeders=seeders, leechers=leechers, completed=completed, date=date))

        return results