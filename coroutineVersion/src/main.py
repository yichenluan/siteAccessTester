# -*- coding: utf-8 -*-
"""Site Access Tester Handler

This file implement SiteTestHandler class.
"""
import time
import re
import urlparse
import urllib2
import socket

import gevent
from gevent import monkey;monkey.patch_all()
from gevent.queue import Queue
from gevent.pool import Pool
from gevent.coros import BoundedSemaphore
from bs4 import BeautifulSoup
from pybloom import ScalableBloomFilter

import conf
from logHandler import LogHandler
from logHandler import ErrorFormat

__version__ = 'coroutine'
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
        self.url_count = 0
        self.sem = BoundedSemaphore(1)
        self.domain, self.pattern = self.__gen_domain_pattern()
        # using bloom filter to check repeat urls
        self.repeat_set = ScalableBloomFilter(
                mode=ScalableBloomFilter.SMALL_SET_GROWTH
                )
        self.pool = self.__genPool()
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

    def __genQueue(self):
        '''generate a queue to store urls waiting be checked

        '''
        queue = Queue()
        queue.put(self.domain)
        return queue
    
    def __genLogger(self):
        '''generate logger

        '''
        Logger = LogHandler(self.domain)
        return Logger.getLogger()

    def __genPool(self):
        '''generate a coroutine pool

        '''
        pool = Pool(conf.COROUTINE_NUM_LIMIT)
        return pool

    def __isValid(self, url):
        for url_pattern in self.pattern:
            if re.search(url_pattern, url) is not None:
                return True
        return False

    def __hasRepeated(self, url):
        if url in self.repeat_set:
            return True
        else:
            # coroutine lock
            self.sem.acquire()
            self.repeat_set.add(url)
            self.sem.release()
            return False

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
        while  self.url_count < conf.URL_TEST_NUM_LIMIT:
            if not self.queue.empty():
                curr_url = self.queue.get()
                self.pool.spawn(self.coroutine, curr_url)
            else:
                time.sleep(1)
        self.logger.info('Test %(num)s urls, Cost time: %(time)s seconds' % 
                {'num':str(conf.URL_TEST_NUM_LIMIT), 'time': (time.time()-start_time)}
            )

    def coroutine(self, url):
        '''target function for coroutine run

        '''
        self.curr_url = url
        request = urllib2.Request(url.encode('utf-8'), headers = HEADERS)
        # implement a opener which don't allowed redirect
        opener = urllib2.build_opener(RedirctHandler)
        retry_time = 0
        new_urls = list()
        while retry_time < conf.RETRY_LIMIT:
            err_format = None
            try:
                response = opener.open(request, timeout=conf.TIME_OUT)
                content = response.read()
                new_urls = self.__genNewUrls(content)
            except urllib2.HTTPError as err:
                if err.code not in (301, 302):
                    err_format = ErrorFormat('HTTPError', url, err)
            except urllib2.URLError as err:
                err_format = ErrorFormat('URLError', url, err)
            except socket.timeout as err:
                err_format = ErrorFormat('TimeOut', url, err)
            except Exception as err:
                err_format = ErrorFormat('OtherException', url, err)
            finally:
                if err_format is None:
                    retry_time = conf.RETRY_LIMIT
                else:
                    retry_time += 1
            for new_url in new_urls:
                self.queue.put(new_url)
            self.sem.acquire()
            self.url_count += 1
            if err_format:
                self.__writeToLog(err_format)
            self.sem.release()


class RedirctHandler(urllib2.HTTPRedirectHandler):
    '''Implement a redirect handler which don't allowed redirect

    '''
    def http_error_301(self, req, fp, code, msg, headers):
        pass
    def http_error_302(self, req, fp, code, msg, headers):
        pass


def main():

    global SITE_CONF
    from m_sohu import M_SOHU
    SITE_CONF = M_SOHU

    test_handler = SiteTestHandler()
    test_handler.test()


if __name__ == '__main__':
    main()
