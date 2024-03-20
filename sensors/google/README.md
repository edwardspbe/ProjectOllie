Data collected by sensor to be moved to our Google Drive
Filename: pumpstatus.csv

Content: periodic state of; pump (ON|OFF), LowFloat (ON|OFF), HIGHFLOAT (ON|OFF)
example:  date, time, <pstate>, <lfstate>, <hfstate>

Content2: state change notifications
example: date, time, <object> <oldstate> <newstate> 

Why are we collecting two types of data? 
... what if our monitor fails?
... what if our system isn't being used?
... we need to get notifications should things stop working or at the 
....... very least, if states stop changing.

TODO: Another option would be to input and track the programmable timed 
... dosage state changes.  When our sensor doesn't see the timing changes
... expected, then a notification could be triggered.  We would still need
... to track the state changes though so we understand how much we are 
... pumping.

Notes about Google drive file access... 
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
... allows full access to files only when setting up OAUTH2 access token
...... used for credentials when building service access.

