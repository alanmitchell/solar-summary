# solar-summary

Collects 5 minute power production data from a solar PV system using Enphase
microinverters.  Creates an HTML document that summarized the data with a
series of graphs.

The results of the script can be seen on the 
[Analysis North Solar Data page](http://analysisnorth.com/docs/mtn-lake-solar/).

Requirements for the server that creates the HTML document:

* The HTML document is created with the [Quarto](https://quarto.org/) publishing
system. Quarto must be installed on the server creating this document.  
* A Python virtual environment also needs to be set up in
the `env` directory of the repository.  That environment must have the Python
packages from `requirements.txt`.
* A `cron` task should be set up to run the `process.sh` file in this
repository every 20 minutes.

