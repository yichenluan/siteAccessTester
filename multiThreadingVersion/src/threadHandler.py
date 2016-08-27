# -*- coding: utf-8 -*-
""" Thread Handler

This file implements ThreadHandler class.
"""
import threading
import time

import conf

__version__ = 'multiThreading'
__author__ = 'huuunnnter@gmail.com'

# url number has already tested
done_url_num = 0


class ThreadHandler(threading.Thread):
    '''Implements a thread handler class for multithreading.

    '''
    def __init__(self, target, queue, lock, name):
        super(ThreadHandler, self).__init__()
        self.target = target
        self.queue = queue
        self.lock = lock
        self.name = name

    def run(self):
        '''Rewrite run function for thread running

        '''
        global done_url_num
        while done_url_num < conf.THREAD_TEST_NUM:
            if not self.queue.empty():
                curr_url = self.queue.get()
                new_urls = self.target(curr_url)
                # thread lock
                with self.lock:
                    done_url_num += 1
                if new_urls:
                    for url in new_urls:
                        self.queue.put(url)

                self.queue.task_done()
            else:
                time.sleep(1)
