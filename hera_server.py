#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author liutaihua(defage@gmail.com)
'''
hera 服务启动入口
'''

import re
import sys

if '--pool=gevent' in sys.argv:
    print 'use gevent mod'
    from gevent import monkey
    monkey.patch_all()

from celery.__main__ import main

if __name__ == '__main__':
    #sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
