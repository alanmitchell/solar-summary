#!/usr/local/bin/python3.6
"""Script to collect and summarize 5 minute power production data 
from an Enphase Solar PV system.  The data collection portion of the
script adds 5 minute power production records to the 'records.csv' file
in this directory.  The plotting portion of the script creates a number
of data summary plots that are saved into the 'output' subdirectory.

The script is meant to be run from a Cron job.  It needs a 'settings.py'
file in the script directory to run, and that file should be patterned after
'settings_example.py' found in this repo.

For continual use, you can run the Cron job every 10 minutes and stay within
the Enphase free tier API limits (10,000 API calls per month), becuase each run
of the script will generally call the API twice.  If you are loading historical
data into the system, you can probably run the script every minute if you are
loading a couple years of historical data; the script won't exceed the per minute
API limit (10 calls / minute), and you will be done loading data in (total days) / 9
calls to the script, since one call to the script will load 9 days of data.

(Note that with some additional code, we could reduce the number of API calls per
script run to 1 instead of 2.  Test for a small number of records returned, like
3 or less, and then don't call again if so.)

There are some plotting commands (e.g. tick spacing, axis limits) that improve 
formatting for my particular solar system; you will need to change those 
(or delete those) for your system.

The script requires the Pandas, Requests, and Matplotlib Python packages to be
present on the system.
"""

import time
from os.path import dirname, join, realpath
from datetime import timedelta, datetime
import pandas as pd
import requests
import matplotlib
matplotlib.use('Agg')
from matplotlib.pyplot import *

import settings

# path to this directory
APP_PATH = dirname(realpath(__file__))

#-----------------------------------------------------------------------------
# Data Collection Portion of the script.

url = 'https://api.enphaseenergy.com/api/v2/systems/{}/'.format(settings.SYSTEM_ID)

# Files that track last record loaded and all records.
FN_LAST_TS = join(APP_PATH, 'last_ts')
FN_RECORDS = join(APP_PATH, 'records.csv')

if settings.COLLECT:

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

    open(FN_LAST_TS, 'w').write(str(start_at))

#-----------------------------------------------------------------------------
# Plot creation portion of the script

MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def get_data(use_dst=True):
    """ Read the data, delete device count column.
    Rembmer that the timestamps mark the end of the interval
    Make a Date/Time field, Alaska Time, and use it for the 
    index.  Fill out missing 5 minute intervals with 0s.
    If 'use_dst' is True, account for Daylight Savings Time.
    Drop the 'usecols' parameter to get the 'device_count' column
    as well.
    """
    dfd = pd.read_csv(FN_RECORDS, usecols=['ts', 'power'])
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

def save_plot(file_name):
    """Saves the current Matplotlib figure to the file 'file_name'
    in the PNG format (with a .png extension) in the 'output subdirectory.  
    Prior to saving, executes the tight_layout() command to reduce 
    whitesapce around the plot area of the figure.
    """
    tight_layout()
    savefig(join(APP_PATH, 'output/{}.png'.format(file_name)))

# 'style' the plot like fivethirtyeight.com website
style.use('bmh')

rcParams['figure.figsize']= (10, 7)   # set Chart Size
rcParams['font.size'] = 14            # set Font size in Chart

if settings.PLOT:

    df = get_data(use_dst=True)

    # kWh bar graph for last ten days' production
    dfd = df.resample('1D').sum()/12000.
    dfd.columns=['kWh']
    dfdt = dfd.tail(10)
    dfdt.index = dfdt.index.astype(str).str[:10]
    dfdt.tail(10).plot.barh(legend=False)
    ylabel('Date')
    xlabel('kWh produced in Day')
    save_plot('last10')

    # Plot last few days in data set.
    clf()
    num_of_days = 5
    for i in range(num_of_days):
        dt_str = str(dfd.index[-(i+1)].date())
        df_1day = df[dt_str]
        if i==0:
            plot(df_1day.index.time, df_1day.power, linewidth=3, label=dt_str)
        else:
            plot(df_1day.index.time, df_1day.power, linewidth=1.2, linestyle='--', label=dt_str)        
            
    xticks(pd.date_range('0:00', '22:00', freq='2H').time, range(0, 24, 2))
    legend()
    ylabel('Power Produced Today, Watts')
    xlabel('Hour of Day')
    save_plot('last_day')

    # Total Monthly Energy production by month and separate lines
    # for each year.
    dfm = df.resample('1M').sum() / 12000.
    dfm['mo'] = dfm.index.month
    dfm['yr'] = dfm.index.year
    dfmp = pd.pivot_table(dfm, values='power', index='mo', columns='yr')
    dfmp.plot(marker='o', linewidth=1)
    xticks(range(0,13))
    gca().set_xticklabels([''] + MONTH_NAMES)
    ylabel('kWh in Month')
    xlabel('Month')
    save_plot('by_month_by_year')

    # Cumulative kWh for each year, by Day-of-Year
    dfd = df.resample('1D').sum() / 12000.
    dfd['day_of_year'] = dfd.index.dayofyear
    dfd['yr'] = dfd.index.year
    dfdp = pd.pivot_table(dfd, values='power', index='day_of_year', columns='yr')
    dfdp.drop([2016], axis=1, inplace=True)   # doesn't start at beginning of year
    dfdp.cumsum().plot()
    ylabel('Cumulative kWh')
    xlabel('Day of Year')
    ylim(0, 2500);
    save_plot('cum_kwh')

    # Zoomed in version of the above, just up to the current day.
    dfcs = dfdp.cumsum().dropna()
    lr = dfcs.iloc[-1]
    ahead = lr[2018] - lr[2017]
    print('2018 kWh - 2017 kWh: {:.0f} kWh'.format(ahead))
    dfcs.plot()
    xlabel('Day of Year');
    ylabel('Cumulative kWh');
    save_plot('cum_kwh_partial')

    # Separate Hourly profile for each month.
    dfb = df.copy()
    dfb['Hour'] = dfb.index.hour
    dfb['mo'] = dfb.index.month
    dfbp = dfb.pivot_table(values='power', index='Hour', columns='mo', aggfunc='mean')
    dfbp.columns = MONTH_NAMES
    dfbp.plot(subplots=True, layout=(4, 3), figsize=(12, 16), sharex=True, sharey=True)
    yticks(range(0, 3000, 500));
    save_plot('monthly_profile')

    # Maximum power production that has occurred in each month.
    clf()
    dfb.groupby('mo').agg('max')['power'].plot(marker='o', linewidth=1, figsize=(10, 7))
    ylabel('Maximum Power Production, Watts')
    xticks(range(0,13))
    gca().set_xticklabels([''] + MONTH_NAMES);
    save_plot('max_power')

    # Box plot of daily energy production for each month.
    dfd = df.resample('1D').sum() / 12000.
    dfd.columns = ['Daily kWh']
    dfd['mo'] = dfd.index.month
    dfd.boxplot(by='mo')
    gca().set_xticklabels(MONTH_NAMES)
    xlabel('')
    ylabel('kWh in Day')
    title('')
    save_plot('monthly_box')

    # Every day's energy production plotted against Day-of-Year
    dfd = df.resample('1D').sum() / 12000.
    dfd.columns = ['kWh']
    dfd['day_of_year'] = dfd.index.dayofyear
    dfd.plot.scatter(x='day_of_year', y='kWh', s=4)
    ylabel('kWh in Day')
    xlabel('Day of Year');
    save_plot('daily_production')

    # Plot the Highest Energy Day
    imax = dfd.kWh.idxmax()
    d = str(imax)[:10]
    max_e = dfd.loc[imax].kWh
    df[d].plot(legend=False)
    title('Day with Most Energy: {}, {:.1f} kWh'.format(d, max_e))
    xlabel('Time')
    ylabel('Power, Watts');
    save_plot('max_energy_day')

    # Plot the Highest Power Day
    imax = df.power.idxmax()
    d = str(imax)[:10]
    max_p = df.loc[imax].power
    df[d].plot(legend=False)
    title('Day with Maximum Peak Power: {}, {:.0f} Watts'.format(d, max_p))
    xlabel('Time')
    ylabel('Power, Watts')
    save_plot('max_power_day')

    # Plot rolling sum of AC kWh Produced per DC kW installed
    (df.resample('1D').sum() / 12000. / settings.SYSTEM_KW).rolling(365).sum().plot(legend=False)
    xlabel('End of 365 Day Period')
    ylabel('AC kWh Produced / DC kW installed')
    save_plot('rolling_yr_kwh')
