# -*- coding: utf-8 -*-

import time

class Printer:
    """Basic class for printing messages"""

    def __init__(self, debug):
        self.debug = debug

    def _print(self, string, tipo):
        tipo = tipo[:4] + '.' if len(tipo) > 5 else tipo
        if tipo not in "DEBUG" or self.debug:
            print("%s | %-5s | ->  %s" % (str(time.strftime("%H:%M:%S")),
                                          tipo, string))

    def d(self, string):
        self._print(string, "DEBUG")

    def e(self, string):
        self._print(string, "ERROR")

    def i(self, string):
        self._print(string, "INFO")

    def w(self, string):
        self._print(string, "WARNING")