"""This is a sample settings.py file.  A 'settings.py' needs to be included
in the directory where the script runs.  It needs to include the following
attributes.
"""
# This is the API Key your receive from Enphase when you sign for an API Account.
# See the Enphase API documentation for more details.
API_KEY = '6d32223a44baffe9ffa9b9edbff05adc7a'

# This is the User ID from the Enphase Account of the Solar system you are
# collecting data from.
# See the Enphase API documentation for more details.
USER_ID = '2e7a67afed9a51220a'

# This is the System ID of the system you are collecting data from
# See the Enphase API documentation for more details.
SYSTEM_ID = 1223456

# Set to True to collect new data from the Enphase API each time the
# script is run.  False otherwise.
COLLECT = True

# Set to True to create new Plot files each time the script is run.
PLOT = True
