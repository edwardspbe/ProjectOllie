import os.path, sys
import mimetypes

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
#SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def main():
  if len(sys.argv) <= 1:
    print("Syntax Error: %s <file1_to_copy, file2_to_copy, ...>", sys.argv[0])
 
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)

    for i in range(1, len(sys.argv)):
      print(sys.argv[i], end = " ")
      file_metadata = {"name": sys.argv[i]}
      #mt = mimetypes.guess_type(sys.argv[i])
      #print(mt)
      #media = MediaFileUpload(sys.argv[i], mimetype=mt)
      media = MediaFileUpload(sys.argv[i], mimetype="text/plain")
      file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
      )
      print(f'File ID: {file.get("id")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return 



if __name__ == "__main__":
  main()
