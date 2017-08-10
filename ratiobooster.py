#!/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
from requests_toolbelt.multipart.encoder import MultipartEncoder
from StringIO import StringIO
import datetime
import locale
import os
import re
import requests
import time
import yaml

cfg = None
already_downloaded = None
hdsBaseUrl = 'https://www.hd-spain.com/'
hdsHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Host': 'www.hd-spain.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-ES,es;q=0.8',
        'Referer': 'https://www.hd-spain.com/index.php?sec=listado',
    }

output_folder = "./downloads"

def getHdsHeaders():
    headers = hdsHeaders
    headers["Cookie"] = cfg["hdSpain"]["cookie"]
    return headers


def main():
    now = datetime.datetime.fromtimestamp(time.time())
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
    url = hdsBaseUrl + 'index.php?sec=listado'
    r = requests.get(url, headers=getHdsHeaders())
    tree = etree.parse(StringIO(r.content), etree.HTMLParser())

    to_download = []

    if cfg["freeleech_only"]:
        print "Freelech Only mode is: ON"

    for index, row in enumerate(tree.xpath('// table[@id="listado"]/tr')):
        # Ignore first row (Headers)
        if index == 0: continue
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
        titulo = titulos[0].lstrip()

        if len(multiplicadores) >= 3 and float(multiplicadores[-1]) == 0.0:
                freeleech = True
        
        date = datetime.datetime.strptime(uploadedAt[0].encode('utf-8'), '%A %d %B %Y, %H:%M')
        
        if cfg["freeleech_only"]:
                if not freeleech:
                    download = False

        if already_downloaded.find(titulo) != -1:
            # print "Ya se ha descargado: ", titulo, "  <---No se hace nada"
            download = False

        if (now - date).days > cfg["maxdays"] and cfg["maxdays"] != -1:
            download = False
        
        if download: 
            if (seeders <= cfg["maxseeds"] or cfg["maxseeds"] == 0) and (completados <= cfg["maxcompleted"] or cfg["maxcompleted"] == -1) and leechers >= cfg["minleechers"]: 
                torrent = requests.get(hdsBaseUrl + link, headers=getHdsHeaders(), stream=True)
                if torrent.status_code == 200:
                    fname = re.findall("filename=(.+)", torrent.headers['content-disposition'])
                    filename = fname[0].strip('"')
                    to_download.append(filename)
                    writeFile(torrent.content, filename, titulo)
            else:
                pass
                # print "Este torrent no cumple con los requisitos de descarga."
        else:
            # Torrent is NOT Freeleech and Freeleech Only is ON, so we do not download.
            pass
        
    if not to_download:
        print "Ningún torrent cumple los requisitos."

def writeFile(data, filename, torrent_title):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print "Saving %s to %s" % (filename, output_folder)
    with open("%s/%s" % (output_folder, filename), 'wb') as f:
        f.write(data)
    with open("./.already_downloaded", 'ab') as f:
        f.write(title+'\n')

def readAlreadyDownloaded():
    import mmap
    with open(".already_downloaded", 'r') as f:
        return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)


if __name__ == '__main__':
    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        output_folder = cfg["downloads_folder"]

    already_downloaded = readAlreadyDownloaded()
    main()