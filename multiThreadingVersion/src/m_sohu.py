# -*- coding: utf-8 -*-
"""Site Configure

This file implements m.sohu.com class which provides domain and url pattern.
"""

class M_SOHU(object):
    '''m.sohu.com configure class

    rewrite this class to adjust requirement.
    '''
    @classmethod
    def domain(cls):
        return 'http://m.sohu.com'

    @classmethod
    def pattern(cls):
        '''url regrex pattern for m.sohu.com

        '''
        url_pattern = [
            '^https?://([\w.]*.)?m.([\w.]*.)?sohu.com[\S.]*$',
        ]
        return url_pattern
