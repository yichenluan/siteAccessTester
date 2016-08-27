# -*- coding: utf-8 -*-
"""Configure file for siteAccessTester

"""

### Logging

# log directory
LOG_DIR = 'log/'
# log file name
LOG_FILE = '%(netloc)s_%(time)s.log'
# log content format
LOG_FMT = '%(time)s \t %(e_type)s \t %(message)s \t %(url)s'

# Socket time out limit
TIME_OUT = 5

# Exception retry limit
RETRY_LIMIT = 5

# Coroutine number limit
COROUTINE_NUM_LIMIT = 500

# Url to test number limit
URL_TEST_NUM_LIMIT = 1000
