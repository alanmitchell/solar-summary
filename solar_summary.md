Title: Analysis North Solar Data
Template: page_no_title
URL: /enphase/soloar_summary.html
Save_As: enphase/solar_summary.html

## Data from Analysis North Solar PV System

Analysis North has a 2.85 kW-DC photovoltaic solar system installed on our place
of business in Anchorage, Alaska (Alan Mitchell's house).  The system consists of
ten 285 Watt SW 285 SolarWorld panels coupled to ten Enphase S280 microinverters
with a total capacity of 2.80 kW-AC.
The system is roof-mounted, tilted at 45 degrees and oriented 8 degrees
West of South.

The graphs below summarize the performance of the system to date.  These graphs
are updated every 10 minutes; press F5 to have your browser refresh
the data.

The code for acquiring the solar data and creating this page is available at 
[Alan Mitchell's GitHub site](https://github.com/alanmitchell/solar-summary).

### Recent Production

This shows the daily energy production from the system for the last ten days.  Note that
the most recent day, shown at top, could be a partial day or could be yesterday if no production
has been reported yet today.  (There are sometimes delays in reporting production at the start 
of the day.)

![daily production](images/last10.png?q=1)

Here is a graph of the power production today (thick blue line) and the prior
few days (thinner dashed lines):

![today's production](images/last_day.png?q=1)

### Cumulative Energy Production for the Year

This graph shows the cumulative energy production of the system for the current year
and for all previous years as separate lines.  For example, a value of 300 kWh on the
Y-axis for day number 80 means that a total of 300 kWh were produced for the first 80
days of the year.

![cumulative production](images/cum_kwh.png?q=1)

This graph below is the same as above except it does not show days of the year beyond the
current day.

![cumulative production](images/cum_kwh_partial.png?q=1)

### Monthly Energy and Power

This graph shows the total number of kWh produced in each month;
each year is shown on a separate line so monthly comparisons between years
are possible.  Note that the most recent month is usually a partial month so will
appear to have a low value.

![monthly production](images/by_month_by_year.png?q=1)

This graph shows the peak power production that has occurred in each month.  It finds
the peak power across *all* of the years of data for each month.

![monthly peak power](images/max_power.png?q=1)

Below, an average production profile is shown for each month.  The Y-axis value is average
power in Watts produced for the hour (0 - 23) shown on the X-axis.

![monthly profiles](images/monthly_profile.png?q=1)

### Spread of Daily Production Values

This boxplot show the spread and the median daily energy production values for each
month.

![monthly box plot](images/monthly_box.png?q=1)

In the plot below, each dot is data from one day.  The Y-axis value is the kWh energy
produced during the day, and the X-axis value is the day of the year.  So, the graph also
is good at showing the distribution of daily energy production values that occur at
different times of the year.

![daily production](images/daily_production.png?q=1)

### Record-Setting Days

Here is the day where the most kWh were produced:

![day with maximum energy](images/max_energy_day.png?q=1)

Here is the day that had the highest 5 minute power production.  This is generally
a day where the solar noon sun comes out from behind some clouds.  As well as the 
solar panels receiving the direct sun, they also receive substantial radiation from
sun rays redirected as they pass through the clouds adjacent to the sun.

![day with maximum peak power](images/max_power_day.png?q=1)

### An Important Number: Normalized kWh per Year

Here is a graph of an important performance number for the system.  If you
take the production of the system for a year in kWh (AC delivered to the grid) 
and then divide by 
the rated capacity of the system in kW (rated DC panel capacity), you have a useful figure of
merit for the system.  For example, a normalized production of 850 kWh-AC / kW-DC
means that each 1 kW of rated capacity in this system produces 850 kWh-AC of electricity
for the year. For this particular system, this number will vary depending upon 
how sunny the year is, dirt and snow accumulation on the panels,
and due to general degradation of output over time.  When
comparing to other systems, the number will vary due to additional factors such 
location of the system, tilt and orientation, shading, etc.

The graph below plots this normalized production on rolling year basis.  The 
first point shown below is for October 1, 2017 and has a value of about
848 kWh / kW.  That means for the 365 days prior to October 1, 2017, the system
produced 848 kWh for each 1 kW of installed capacity.  Each additional point
on the line indicates the normalized production for the 365 days preceding the
date on the horizontal axis.

![rolling normalized production](images/rolling_yr_kwh.png?q=1)

---

<p>
Powered by: <a href="http://enphase.com"><img alt="Enphase Logo" src="images/Powered_By_Enphase_Logo.png" width="200"></a>
</p>
Solar data is acquired through use of the Enphase API (application programming interface).  
All data analysis and graphing is custom programming done by Analyis North and is available at 
[Alan Mitchell's GitHub site](https://github.com/alanmitchell/solar-summary).
