#!/bin/env python
# -*- coding: utf-8 -*-

from libs import printer
from lxml import etree
from StringIO import StringIO

import datetime
import importlib
import locale
import os
import re
import requests
import time
import yaml

cfg = None
already_downloaded = None

output_folder = "./downloads"
logger = None
now = datetime.datetime.fromtimestamp(time.time())

# El parser devolvera una lista [{"title": titulo, "link": link, "freelech": True}] por cada torrent parseado. El modulo original seguira siendo el que llame a la descarga.
def check_download(parser, torrent):
    download = True

    if parser.config["freeleech_only"]:
        if not torrent.freeleech:
            download = False

    if already_downloaded.find(torrent.title) != -1:
        # print "Ya se ha descargado: ", titulo, "  <---No se hace nada"
        download = False

    if (now - torrent.date).days > parser.config["maxdays"] and parser.config["maxdays"] != -1:
        download = False

    if download:
        if (torrent.seeders <= parser.config["maxseeds"] or parser.config["maxseeds"] == 0) and (
                torrent.completed <= parser.config["maxcompleted"] or parser.config["maxcompleted"] == -1) and torrent.leechers >= parser.config["minleechers"]:
            r = parser.download_torrent(torrent)
            if r.status_code == 200:
                fname = re.findall(
                    "filename=(.+)",
                    r.headers['content-disposition'])
                filename = fname[0].strip('"')
                writeFile(r.content, filename, torrent.title)
                return True
        else:
            pass
            # print "Este torrent no cumple con los requisitos de
            # descarga."
    else:
        # Torrent is NOT Freeleech and Freeleech Only is ON, so we do not
        # download.
        pass

    return False


def writeFile(data, filename, torrent_title):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print "Saving %s to %s" % (filename, output_folder)
    with open("%s/%s" % (output_folder, filename), 'wb') as f:
        f.write(data)
    with open("./.already_downloaded", 'ab') as f:
        f.write(torrent_title + '\n')


def readAlreadyDownloaded():
    import mmap
    with open('.already_downloaded', 'r') as f:
        return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)


def load_parsers():
    parsers = []
    for trackerDict in cfg["trackers"]:
        for tracker, tracker_config in trackerDict.iteritems():
            logger.d(tracker)
            mod = importlib.import_module('modules.%s' % (tracker))

            for param in ["minleechers", "maxseeds", "maxcompleted", "freeleech_only", "maxdays"]:
                if param not in tracker_config:
                    tracker_config[param] = cfg[param]
            
            parsers.append(mod.Parser(tracker_config, logger))
    return parsers
           
def start(parsers):
    to_download = False
    if cfg["freeleech_only"]:
        logger.d("Freelech Only mode is: ON")

    for parser in parsers:
        for torrent in parser.parse():
            if check_download(parser, torrent):
                to_download = True

    if not to_download:
        logger.i("Ningún torrent cumple el filtro")

if __name__ == '__main__':
    with open('config.yml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        output_folder = cfg["downloads_folder"]

    logger = printer.Printer(True)
    already_downloaded = readAlreadyDownloaded()
    start(load_parsers())
