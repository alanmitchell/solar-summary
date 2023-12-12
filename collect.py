#!/usr/bin/env python3
"""Script to collect 5 minute power production data 
from an Enphase Solar PV system.  The script
adds 5 minute power production records to the 'records.csv' file
in this directory.

The script is meant to be run from a Cron job.  It needs a 'settings.py'
file in the script directory to run, and that file should be patterned after
'settings_example.py' found in this repo.

For continual use, you can run the Cron job every 10 minutes and stay within
the Enphase free tier API limits (10,000 API calls per month), becuase each run
of the script will generally call the API once.  If you are loading historical
data into the system, you can probably run the script every minute if you are
loading a couple years of historical data; the script won't exceed the per minute
API limit (10 calls / minute), and you will be done loading data in (total days) / 9
minutes, since one call to the script will load 9 days of data.
"""

import time
from os.path import dirname, join, realpath
from datetime import timedelta, datetime
import requests

import settings

# path to this directory
APP_PATH = dirname(realpath(__file__))

#-----------------------------------------------------------------------------
# Data Collection Portion of the script.

url = 'https://api.enphaseenergy.com/api/v2/systems/{}/'.format(settings.SYSTEM_ID)

# Files that track last record loaded and all records.
FN_LAST_TS = join(APP_PATH, 'last_ts')
FN_RECORDS = join(APP_PATH, 'records.csv')

payload_base = {
    'key': settings.API_KEY,
    'user_id': settings.USER_ID,
}

try:
    start_at = int(open(FN_LAST_TS).read())
except:
    start_at = requests.get(url + 'summary', params=payload_base).json()['operational_at']

payload = payload_base.copy()

for i in range(9):
    time.sleep(2)

    print(start_at)
    payload['start_at'] =  start_at
    res = requests.get(url + 'stats', params=payload).json()

    if 'intervals' not in res:
        break

    recs = list(map(lambda r: (r['end_at'], r['devices_reporting'], r['powr']), res['intervals']))
    if len(recs):
        with open(FN_RECORDS, 'a') as fout:
            for rec in recs:
                fout.write('{},{},{}\n'.format(*rec))
        start_at = recs[-1][0]

    else:
        # sometimes there will be a 24 hour period without any reports, so advance
        # the starting time a day and try again.  Only do this if it will not advance
        # beyond the current time.
        if time.time() > start_at + 24*3600:
            start_at += 24*3600

    # if we are within two weeks of the current time, don't call the API again.
    # If we're within 2 weeks, this is probably normal use of the script as opposed
    # to loading historical data.  If it is the last days of loading historical data,
    # it will only take 14 more runs of the script to finish up, which isn't that long.
    if start_at > time.time() - 3600 * 24 * 14:
        break

open(FN_LAST_TS, 'w').write(str(start_at))
