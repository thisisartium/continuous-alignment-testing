import os
import sys

from pydrive2.auth import GoogleAuth  # type: ignore
from pydrive2.drive import GoogleDrive  # type: ignore


def login_with_service_account(credentials_path: str) -> GoogleAuth:
    """
    Google Drive service with a service account.
    note: for the service account to work, you need to share the folder or
    files with the service account email.

    :return: google auth
    """
    settings = {
        "client_config_backend": "service",
        "service_config": {
            "client_json_file_path": credentials_path,
        },
    }
    gauth = GoogleAuth(settings=settings)
    gauth.ServiceAuth()
    return gauth


PARENT_FOLDER_IDS = "PARENT_FOLDER_IDS"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python publish_to_gdrive.py <file_path>")
        print(f"{PARENT_FOLDER_IDS} - comma-separated list of google folder IDs")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    credentials_file_path = os.environ.get("GOOGLE_GHA_CREDS_PATH")
    if not credentials_file_path:
        print("Error: GOOGLE_GHA_CREDS_PATH environment variable is not set.")
        sys.exit(1)

    google_auth = login_with_service_account(credentials_file_path)
    drive = GoogleDrive(google_auth)

    file_name = os.path.basename(file_path)
    parent_ids = os.environ.get(PARENT_FOLDER_IDS)
    if not parent_ids:
        print(f"Error: {PARENT_FOLDER_IDS} environment variable is not set.")
        sys.exit(2)
    parents = [{"id": pid.strip()} for pid in (parent_ids.split(","))]
    gfile = drive.CreateFile({"title": file_name, "parents": parents})

    gfile.SetContentFile(file_path)
    gfile.Upload()

    print("File uploaded successfully!")
    print("File ID:", gfile["id"])
