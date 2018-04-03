# solar-summary

Collects 5 minute power production data from a solar PV system using Enphase
microinverters.  Summarizes the energy and power production data from that system
in a series of plots.

The results of the script can be seen on the 
[Analysis North Solar Data page](http://analysisnorth.com/enphase/solar_summary.html).

See the doc string in the `summarize.py` script for more information on configuration of
the script.

As well as adding 5 minute power production records to the `records.csv` file created
by the script, this script creates a number of summary plots and saves them into the 
`output` subdirectory beneath the directory where the script is located.

The `solar_summary.md` file is a Markdown file that describes and displays the plots
created by this script.  It is formatted to be used with the 
[Pelican static web site generation system](http://docs.getpelican.com/en/stable/).  It assumes
that the plot images created by this script are present in an `images` directory located beneath
the Pelican web page.
