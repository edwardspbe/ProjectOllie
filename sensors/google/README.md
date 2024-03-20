Notes on "copy to Google drive" routine and exercise to get this working with OAUTH2

Script: quickstart.py
Original program comes from google examples; first file used to quickly listing 
files on your "drive", second used to MediaFileUpload() a file to the drive.
1. first file used OAUTH2, with read_only scope. 
2. second used "default" authentication (didn't implement), but uses local hidden
   file with default google drive creds.

Notes about Google drive file access... 
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
... allows full access to files only when setting up OAUTH2 access token
...... used for credentials when building service access.
... important to use the correct mediatype and scope
