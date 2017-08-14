# coding=utf-8

class Torrent:

    def __init__(self, title=None, link=None, freeleech=False, seeders=0, leechers=0, completed=0, date=None):
        self.title = title.encode('utf-8')
        self.link = link
        self.freeleech = freeleech
        self.seeders = seeders
        self.leechers = leechers
        self.completed = completed
        self.date = date

    def __str__(self):
        return 'Torrent={title=%s, link=%s, freelech=%s, seeders=%d, leechers=%d, completed=%d, date=%s}' % (self.title, self.link, self.freeleech, self.seeders, self.leechers, self.completed, self.date)