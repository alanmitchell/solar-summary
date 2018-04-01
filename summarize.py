#!/usr/local/bin/python
"""Script to collect 5 minute power production data from an Enphase system.
"""
import time
from os.path import dirname, join, realpath
from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import requests
from matplotlib.pyplot import *

import settings

# 'style' the plot like fivethirtyeight.com website
style.use('bmh')

rcParams['figure.figsize']= (10, 7)   # set Chart Size
rcParams['font.size'] = 14            # set Font size in Chart

url = 'https://api.enphaseenergy.com/api/v2/systems/{}/'.format(settings.SYSTEM_ID)

# path to this directory
APP_PATH = dirname(realpath(__file__))

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
    recs = map(lambda r: (r['end_at'], r['devices_reporting'], r['powr']), res['intervals'])
    if len(recs):
        with open(FN_RECORDS, 'a') as fout:
            for rec in recs:
                fout.write('{},{},{}\n'.format(*rec))
        start_at = recs[-1][0]
    else:
        # sometimes there will be a 24 hour period without any reports, so advance
        # the starting time a day and try again.
        start_at += 24*3600

open(FN_LAST_TS, 'w').write(str(start_at))

# Analyzes 5 minute Production Data from 11400 Mtn Lake System

MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def get_data(use_dst=True):
    # Read the data, delete device count column.
    # Rembmer that the timestamps mark the end of the interval
    # Make a Date/Time field, Alaska Time, and use it for the 
    # index.  Fill out missing 5 minute intervals with 0s.
    # If 'use_dst' is True, account for Daylight Savings Time.
    # Drop the 'usecols' parameter to get the 'device_count' column
    # as well.
    dfd = pd.read_csv('http://analysisnorth.com/enphase/records.csv', usecols=['ts', 'power'])
    dfd['dts'] = pd.to_datetime(dfd.ts, unit='s')
    dfd.drop(['ts'], axis=1, inplace=True)
    if not use_dst:
        akst_adj = timedelta(hours=9)
        dfd['dts'] = dfd.dts - akst_adj
    dfd.set_index('dts', inplace=True)
    dfd = dfd.asfreq('5T', fill_value=0.0)
    if use_dst:
        dfd.index = dfd.index.tz_localize('UTC').tz_convert('US/Alaska').tz_localize(None)

    return dfd

df = get_data(use_dst=True)

# kWh for last ten days
dfd = df.resample('1D').sum()/12000.
dfd.columns=['kWh']
dfdt = dfd.tail(10)
dfdt.index = dfdt.index.astype(str).str[:10]
dfdt.tail(10).plot.barh(legend=False)
ylabel('Date')
xlabel('kWh produced in Day')
savefig('output/last10.png')

# Plot Last Day present
df[str(dfd.index[-1].date())].plot(legend=False)
ylabel('Power Produced Today, Watts')
xlabel('Time')
df_sum = df.resample('1M').sum() / 12000.
df_sum.columns = ['kWh']
df_sum.plot(marker='o', linewidth=1, legend=False)
ylabel('kWh in Month')
xlabel('Month')
savefig('output/last_day.png')

dfm = df.resample('1M').sum() / 12000.
dfm['mo'] = dfm.index.month
dfm['yr'] = dfm.index.year
dfmp = pd.pivot_table(dfm, values='power', index='mo', columns='yr')
dfmp.plot(marker='o', linewidth=1)
xticks(range(0,13))
gca().set_xticklabels([''] + MONTH_NAMES)
ylabel('kWh in Month')
xlabel('Month')
savefig('output/by_month_by_year.png')

dfd = df.resample('1D').sum() / 12000.
dfd['day_of_year'] = dfd.index.dayofyear
dfd['yr'] = dfd.index.year
dfdp = pd.pivot_table(dfd, values='power', index='day_of_year', columns='yr')
dfdp.drop([2016], axis=1, inplace=True)   # doesn't start at beginning of year
dfdp.cumsum().plot()
ylabel('Cumulative kWh')
xlabel('Day of Year')
ylim(0, 2500);
savefig('output/cum_kwh.png')


dfcs = dfdp.cumsum().dropna()
lr = dfcs.iloc[-1]
ahead = lr[2018] - lr[2017]
print(f"2018 kWh - 2017 kWh: {ahead:.0f} kWh")
dfcs.plot()
xlabel('Day of Year');
ylabel('Cumulative kWh');
savefig('output/cum_kwh_partial.png')

dfb = df.copy()
dfb['Hour'] = dfb.index.hour
dfb['mo'] = dfb.index.month
dfbp = dfb.pivot_table(values='power', index='Hour', columns='mo', aggfunc='mean')
dfbp.columns = MONTH_NAMES
dfbp.plot(subplots=True, layout=(4, 3), figsize=(12, 16), sharex=True, sharey=True)
yticks(range(0, 3000, 500));

dfb.groupby('mo').agg('max')['power'].plot(marker='o', linewidth=1)
ylabel('Maximum Power Production, Watts')
xticks(range(0,13))
gca().set_xticklabels([''] + MONTH_NAMES);

dfd = df.resample('1D').sum() / 12000.
dfd.columns = ['Daily kWh']
dfd['mo'] = dfd.index.month
dfd.boxplot(by='mo')

gca().set_xticklabels(MONTH_NAMES)
xlabel('')
ylabel('kWh in Day')
title('')

dfd = df.resample('1D').sum() / 12000.
dfd.columns = ['kWh']
dfd['day_of_year'] = dfd.index.dayofyear
dfd.plot.scatter(x='day_of_year', y='kWh', s=4)
ylabel('kWh in Day')
xlabel('Day of Year');

# Highest Energy Day
print(dfd.kWh.idxmax())
df['2017-06-15'].plot();

