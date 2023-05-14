#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/timezone.py
# By:          Samuel Duclos
# For          Myself
# Description: Timezone offset calculation.

# Library imports.
from datetime import datetime
from pytz import timezone, UTC
import time

# Function definitions.
def get_timezone_offset_in_seconds() -> float:
    """Return the offset in seconds of the local timezone."""
    tz = timezone(time.tzname[0])
    offset_s = tz.utcoffset(datetime.now()).total_seconds()
    offset_s = int(abs(offset_s))
    return offset_s
