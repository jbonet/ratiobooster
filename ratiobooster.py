#!/bin/env python
# coding=utf-8

from joblib import Parallel, delayed
from libs import printer

import argparse
import datetime
import importlib
import os
import re
import requests
import time
import yaml

NUM_JOBS = 8
VERBOSITY_LEVEL = 0

cfg = None
already_downloaded = None

output_folder = None
logger = None
now = datetime.datetime.fromtimestamp(time.time())

def check_download(parser, torrent):
    download = True

    if parser.config["freeleech_only"]:
        if not torrent.freeleech:
            download = False

    if already_downloaded.find(torrent.title) != -1:
        logger.d("Already downloaded torrent!")
        download = False

    if (now - torrent.date).days > parser.config["maxdays"] and parser.config["maxdays"] != -1:
        download = False

    if download:
        if (torrent.seeders <= parser.config["maxseeds"] or parser.config["maxseeds"] == 0) and (
                torrent.completed <= parser.config["maxcompleted"] or parser.config["maxcompleted"] == -1) and torrent.leechers >= parser.config["minleechers"]:
            r = download_torrent(parser, torrent)
            if r.status_code == 200:
                fname = re.findall(
                    "filename=(.+)",
                    r.headers['content-disposition'])
                filename = fname[0].strip('"')
                writeFile(r.content, filename, torrent.title)
                return True

    return False

def download_torrent(parser, torrent):
    url = '{baseUrl}{link}'.format(baseUrl=parser.baseUrl, link=torrent.link )
    r = requests.get(url, headers=parser.headers, stream=True)
    return r

def writeFile(data, filename, torrent_title):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    logger.i("Saving %s to %s" % (filename, output_folder))
    with open("%s/%s" % (output_folder, filename), 'wb') as f:
        f.write(data)
    with open("./.already_downloaded", 'ab') as f:
        f.write(torrent_title + '\n')

def readAlreadyDownloaded():
    import mmap
    if not os.path.exists('.already_downloaded'):
        with open('.already_downloaded', 'w') as f:
            f.write('Already downloaded torrents:')
    with open('.already_downloaded', 'r') as f:
        return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

def load_parsers():
    parsers = []
    logger.d("Loading parsers...")
    for trackerDict in cfg["trackers"]:
        for tracker, tracker_config in trackerDict.iteritems():
            logger.d("Loading parser for: %s" % tracker)
            if not tracker_config["enabled"]:
                logger.d("Parser for %s is disabled. Skipping..." % tracker)
                continue
            mod = importlib.import_module('modules.%s' % (tracker))

            tracker_config["name"] = tracker
            for param in ["minleechers", "maxseeds", "maxcompleted", "freeleech_only", "maxdays"]:
                if param not in tracker_config:
                    tracker_config[param] = cfg[param]

            logger.d("%s parser was loaded." % tracker)
            parsers.append(mod.Parser(tracker_config, logger, tracker))
    return parsers

def par2(parser, torrent):
    return check_download(parser, torrent)

def par1(parser):
        results = Parallel(n_jobs=NUM_JOBS, verbose=VERBOSITY_LEVEL, backend="threading")(delayed(par2)(parser, torrent)
        for torrent in parser.parse())

        return True if True in results else False


def start(parsers):
    if cfg["freeleech_only"]:
        logger.d("Freeleech Only mode is: ON")

    results = Parallel(n_jobs=NUM_JOBS, verbose=VERBOSITY_LEVEL, backend="threading")(delayed(par1)(parser)
        for parser in parsers)

    if not True in results:
        logger.i("Ningún torrent cumple el filtro")

if __name__ == '__main__':

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-c', '--config', metavar="custom_config.yml", help="Loads the specified config file",
                        default="config.yml")
    argparser.add_argument('-d', '--debug', action='store_true',
                        help='Enables Debug mode (Verbose)', default=False)

    args = argparser.parse_args()
    logger = printer.Printer(args.debug)

    if os.path.exists(args.config):
        with open(args.config, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            output_folder = cfg["downloads_folder"]
        already_downloaded = readAlreadyDownloaded()
        start(load_parsers())
    else:
        logger.e('The specified config file (%s) does not exist!' % (args.config))