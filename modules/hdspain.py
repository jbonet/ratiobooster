# coding=utf-8

from base import BaseParser
from libs.torrent import Torrent
from defusedxml import lxml
from lxml import etree
from StringIO import StringIO

import datetime
import requests

class Parser(BaseParser):
    """Parser for HD-Spain torrent list"""

    def __init__(self, config=None, logger=None, name=""):
        super(Parser, self).__init__(logger, name)
        self.config = config
        self.baseUrl = 'https://www.hd-spain.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Host': 'www.hd-spain.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'es-ES,es;q=0.8',
            'Referer': 'https://www.hd-spain.com/index.php?sec=listado',
            'Cookie': config["cookie"]
            }
        self.logger = logger

    def parse(self):
        self.logger.i("Checking HDSpain torrents")
        url = '{baseUrl}index.php?sec=listado'.format(baseUrl=self.baseUrl)
        r = requests.get(url, headers=self.headers)
        if not r.status_code == 200:
            return []

        tree = lxml.parse(StringIO(r.content), parser=etree.HTMLParser())

        results = []

        for index, row in enumerate(tree.xpath('// table[@id="listado"]/tr')):
            # Ignore first row (Headers)
            if index == 0:
                continue
            titulos = row.xpath('./td[@class="titulo"]/a[last()]/text()')
            seeders = self.checkOrZero(row.xpath('./td[@class="usuarios seeds "]/a[last()]/text()'))
            leechers = self.checkOrZero(row.xpath('./td[@class="usuarios leechers  "]/a[last()]/text()'))
            completados = self.checkOrZero(row.xpath('./td[@class="usuarios completados"]/text()'))
            uploadedAt = row.xpath('./td[@class="fecha"]/@title')
            download = row.xpath('./td[@class="descargar"]/a')
            link = download[0].xpath('./@href')[0]
            multiplicadores = download[0].xpath('./b/text()')
            freeleech = False

            if "AudioEditado" in titulos[0] or "R" == titulos[0]:
                titulos = row.xpath('./td[@class="titulo"]/a[last() - 1]/text()')
            title = titulos[0].lstrip()

            if len(multiplicadores) >= 3 and float(multiplicadores[-1]) == 0.0:
                freeleech = True

            date = datetime.datetime.strptime(
                uploadedAt[0].encode('utf-8'), '%A %d %B %Y, %H:%M')

            results.append(Torrent(title=title, link=link, freeleech=freeleech, seeders=seeders, leechers=leechers, completed=completados, date=date))

        return results
    