# -*- coding=utf8 -*-
import sys

from multiThreadingVersion.src.main import main as t_main
from coroutineVersion.src.main import main as c_main


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # use coroutine version as default
        c_main()
        sys.exit()
    if sys.argv[1].startswith('-'):
        option = sys.argv[1][1:]
        if option == 't':
            # multiThreadingVersion
            t_main()
        elif option == 'c':
            #coroutineVersion
            c_main()
        else:
            print 'Please choose t or c version'
    else:
        print 'Unknown option'
