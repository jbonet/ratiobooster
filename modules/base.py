# -*- coding: utf-8 -*-

import locale

class BaseParser(object):
    def __init__(self, logger=None, name="BaseParser"):
        locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
        self.name = name
        self.logger = logger
        logger.d("Initialized %s parsing..." % (name))

    def checkOrZero(self, item):
        data = 0
        try:
            data = int(item[0])
        except IndexError:
            pass
        return data