from pydrive2.auth import GoogleAuth  # type: ignore
from pydrive2.drive import GoogleDrive  # type: ignore

# Step 1: Authenticate and create the PyDrive client
gauth = GoogleAuth()
# This will open a local web server to authenticate your Google account
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Step 2: Create a file object and set its metadata
upload_file = "graph-data.csv"
gfile = drive.CreateFile({"title": "graph-data.csv", "parents": [{"id": "18caB8w7KZjq5kH-i9SDEA_V9qYCeWypL"}]})

# Step 3: Set the content of the file from the local CSV
gfile.SetContentFile(upload_file)


if __name__ == "__main__":
    # Step 4: Upload the file to Google Drive
    gfile.Upload()

    print("File uploaded successfully!")
    print("File ID:", gfile["id"])
