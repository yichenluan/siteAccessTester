# -*- coding: utf-8 -*-
"""Site Access Tester Handler

This file implement SiteTestHandler class.
"""
import time
import Queue
import threading
import urlparse
import re

import requests
from bs4 import BeautifulSoup
from pybloom import ScalableBloomFilter

import conf
from threadHandler import ThreadHandler
from logHandler import LogHandler
from logHandler import ErrorFormat

__version__ = 'multiThreading'
__author__ = 'huuunnnter@gmail.com'

# site configure
SITE_CONF = None
# http request headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    "Connection": "close",
    }


class SiteTestHandler(object):
    '''Implements a site test handler for site access tester

    '''
    def __init__(self):
        self.curr_url = None
        self.lock = threading.Lock()
        # using bloom filter to check repeat urls
        self.repeat_set = ScalableBloomFilter(
                mode=ScalableBloomFilter.SMALL_SET_GROWTH
                )
        self.domain, self.pattern = self.__gen_domain_pattern()
        self.queue = self.__genQueue()
        self.logger = self.__genLogger()

    def __gen_domain_pattern(self):
        '''generate domain and pattern by SITE_CONF

        '''
        if SITE_CONF is None:
            raise Exception(u'请先注册站点信息')
        domain = SITE_CONF.domain()
        pattern = SITE_CONF.pattern()
        return domain, pattern

    def __genLogger(self):
        '''generate logger

        '''
        Logger = LogHandler(self.domain)
        return Logger.getLogger()

    def __genQueue(self):
        '''generate a queue to store urls waiting be checked

        '''
        queue = Queue.Queue()
        queue.put(self.domain)
        return queue

    def __genNewUrls(self, content):
        '''generate new urls from html content

        '''
        soup = BeautifulSoup(content, 'lxml')
        new_urls = list()
        for tag in soup.findAll('a', href=True):
            location = tag['href']
            if location.startswith('http'):
                url = location
            else:
                # join prefix and href
                url = urlparse.urljoin(self.curr_url, tag['href'])
            if not self.__isValid(url):
                # check url is valid by regrex pattern
                continue
            if not self.__hasRepeated(url):
                # check url has repeated
                new_urls.append(url)
        return new_urls

    def __isValid(self, url):
        for url_pattern in self.pattern:
            if re.search(url_pattern, url) is not None:
                return True
        return False


    def __hasRepeated(self, url):
        with self.lock:
            if url in self.repeat_set:
                return True
            else:
                self.repeat_set.add(url)
                return False

    def __writeToLog(self, err_format):
        '''write error infomation to log file

        '''
        if not err_format:
            return
        self.logger.error(conf.LOG_FMT % 
                {
                    'time': err_format.time,
                    'e_type': err_format.e_type,
                    'url': err_format.url,
                    'message': err_format.message,
                }
            )

    def test(self):
        '''test url function

        '''
        start_time = time.time()
        threads_pool = list()
        THREAD_NUM = conf.THREAD_NUM
        for i in xrange(THREAD_NUM):
            # generate a thread
            worker = ThreadHandler(self.target, self.queue, self.lock, i)
            worker.setDaemon(True)
            worker.start()
            threads_pool.append(worker)

        for worker in threads_pool:
            # waiting all threads finished
            worker.join()

        self.logger.info('Test %(num)s urls, Cost time: %(time)s seconds' % 
                {'num':str(conf.THREAD_TEST_NUM), 'time': (time.time()-start_time)}
            )

    def target(self, url):
        '''target function for thread

        '''
        new_urls = list()
        self.curr_url = url
        retry_time = 0
        while retry_time < conf.RETRY_LIMIT:
            err_format = None
            try:
                url_r = requests.get(
                        url, 
                        timeout=conf.TIME_OUT, 
                        allow_redirects=False,
                        headers = HEADERS,
                    )
                url_r.raise_for_status()
                new_urls = self.__genNewUrls(url_r.text)
            except requests.exceptions.Timeout as err:
                err_format = ErrorFormat('TimeOut', url, err)
            except requests.exceptions.HTTPError as err:
                err_format = ErrorFormat('HTTPError', url, err)
            except requests.exceptions.RequestException as err:
                err_format = ErrorFormat('OtherException', url, err)
            finally:
                if err_format is None:
                    retry_time = conf.THREAD_NUM
                else:
                    retry_time += 1
        if err_format:
            with self.lock:
                self.__writeToLog(err_format)
        return new_urls


def main():

    global SITE_CONF
    from m_sohu import M_SOHU
    # register m.sohu.com to SITE_CONF
    SITE_CONF = M_SOHU

    test_handler = SiteTestHandler()
    test_handler.test()


if __name__ == '__main__':
    main()
