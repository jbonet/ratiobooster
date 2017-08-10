# -*- coding: utf-8 -*-

from libs.torrent import Torrent
from lxml import etree
from StringIO import StringIO

import datetime
import locale
import requests

class Parser:
    """Parser for HD-Spain torrent list"""

    def __init__(self, config, logger):
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        self.config = config
        self.baseUrl = baseUrl = 'https://www.hd-spain.com/'
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

    def download_torrent(self, torrent):
        url = '{baseUrl}{link}'.format(baseUrl=self.baseUrl, link=torrent.link )
        r = requests.get(url, headers=self.headers, stream=True)
        return r

    def parse(self):
        self.logger.d("Starting HD-Spain parsing...")
        url = '{baseUrl}index.php?sec=listado'.format(baseUrl=self.baseUrl)
        r = requests.get(url, headers=self.headers)
        tree = etree.parse(StringIO(r.content), etree.HTMLParser())

        results = []

        for index, row in enumerate(tree.xpath('// table[@id="listado"]/tr')):
            # Ignore first row (Headers)
            if index == 0:
                continue
            titulos = row.xpath('./td[@class="titulo"]/a[last()]/text()')
            seeders = row.xpath('./td[@class="usuarios seeds "]/a[last()]/text()')
            leechers = row.xpath('./td[@class="usuarios leechers  "]/a[last()]/text()')
            completados = row.xpath('./td[@class="usuarios completados"]/text()')
            uploadedAt = row.xpath('./td[@class="fecha"]/@title')
            download = row.xpath('./td[@class="descargar"]/a')
            link = download[0].xpath('./@href')[0]
            multiplicadores = download[0].xpath('./b/text()')
            freeleech = False
            download = True
            seeders = int(seeders[0])
            completados = int(completados[0])
            leechers = int(leechers[0])

            if "AudioEditado" in titulos[0] or "R" == titulos[0]:
                titulos = row.xpath('./td[@class="titulo"]/a[last() - 1]/text()')
            title = titulos[0].lstrip()

            if len(multiplicadores) >= 3 and float(multiplicadores[-1]) == 0.0:
                freeleech = True

            date = datetime.datetime.strptime(
                uploadedAt[0].encode('utf-8'), '%A %d %B %Y, %H:%M')

            results.append(Torrent(title=title, link=link, freeleech=freeleech, seeders=seeders, leechers=leechers, completed=completados, date=date))

        return results 