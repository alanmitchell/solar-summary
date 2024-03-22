#!/usr/bin/env python3
"""Script to collect 5 minute power production data 
from an Enphase Solar PV system.  The script
adds 5 minute power production records to the 'records.db' SQLite file
in this directory.

The script is meant to be run from a Cron job.  It needs a 'settings.py'
file in the script directory to run, and that file should be patterned after
'settings_example.py' found in this repo.

For continual use, you can run the Cron job every 1 hour and stay within
the Enphase free tier API limits (1,000 API calls per month), becuase each run
of the script will generally call the API once. There is also a 10 calls / minute
limit, but this script is only designed to make one call.
"""

from pathlib import Path
from base64 import b64encode

import sqlite3
import requests
import pandas as pd

import settings

# path to this directory
APP_PATH = Path(__file__).parent.absolute()

def get_refreshed_tokens():
    """Acquires and puts new Access and Refresh tokens in the appropriate files.
    """
    url = 'https://api.enphaseenergy.com/oauth/token'
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': open(APP_PATH / 'refresh.txt').read(),
    }
    client_id_secret = f'{settings.CLIENT_ID}:{settings.CLIENT_SECRET}'.encode('utf-8')
    c_id_secret_encoded = b64encode(client_id_secret).decode('utf-8')
    headers = {
        'Authorization': f'Basic {c_id_secret_encoded}'
    }
    result = requests.post(url, params=payload, headers=headers).json()
    access_token = result['access_token']
    open('access.txt', 'w').write(access_token)
    open('refresh.txt', 'w').write(result['refresh_token'])
    return access_token

# API URI for call that fetches 5 minute power production records.
url = f'https://api.enphaseenergy.com/api/v4/systems/{settings.SYSTEM_ID}/telemetry/production_micro'

payload = {
    'key': settings.API_KEY,
    'granularity': 'week'
}


access_token = open(APP_PATH / 'access.txt').read()
headers = {
    'Authorization': f'Bearer {access_token}'
}

conn = sqlite3.connect(APP_PATH / 'records.db')
cursor = conn.cursor()

try:
    cursor.execute('SELECT MAX(ts) FROM power')
    rows = cursor.fetchall()
    start_at = rows[0][0]
except:
    # database may be empty, get time of first record in API.
    start_at = requests.get(url, params=payload, headers=headers).json()['operational_at']

# start at 35 minutes prior to last record, in case last few records have been updated
# in the API
payload['start_at'] = start_at - 35 * 60
print(payload['start_at'])

results = requests.get(url, params=payload, headers=headers)
if results.status_code != 200:
    access_token = get_refreshed_tokens()
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    results = requests.get(url, params=payload, headers=headers)

results = results.json()

if len(results['intervals']):
    df = pd.DataFrame(results['intervals'])
    df.rename(columns={'end_at': 'ts', 'devices_reporting': 'device_count', 'powr': 'power'}, inplace=True)
    df = df[['ts', 'device_count', 'power']]
    for ix, record in df.iterrows():
        ts = int(record['ts'])
        device_count = int(record['device_count'])
        power = int(record['power'])
        # First, try to update the existing record
        cursor.execute("""
            UPDATE power
            SET device_count = ?, power = ?
            WHERE ts = ?""", (device_count, power, ts))

        if cursor.rowcount == 0:
            # If no rows were updated, this record doesn't exist, so insert it
            cursor.execute("""
                INSERT INTO power (ts, device_count, power)
                VALUES (?, ?, ?)""", (ts, device_count, power))

    conn.commit()

conn.close()

# payload['start_at'] =  start_at
# res = requests.get(url + 'stats', params=payload).json()

# if 'intervals' not in res:
#     break

# recs = list(map(lambda r: (r['end_at'], r['devices_reporting'], r['powr']), res['intervals']))
# if len(recs):
#     with open(FN_RECORDS, 'a') as fout:
#         for rec in recs:
#             fout.write('{},{},{}\n'.format(*rec))
#     start_at = recs[-1][0]

# else:
#     # sometimes there will be a 24 hour period without any reports, so advance
#     # the starting time a day and try again.  Only do this if it will not advance
#     # beyond the current time.
#     if time.time() > start_at + 24*3600:
#         start_at += 24*3600

