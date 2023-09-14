#!/usr/bin/env python3
#
# Author:
#  Tamas Jos (@skelsec)
#

import logging

logger = logging.getLogger('asysocks')
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False