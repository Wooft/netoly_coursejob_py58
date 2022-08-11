from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

def upload_dir(dir_path = '', file_name = ''):
    try:
        drive = GoogleDrive(gauth)
        my_file = drive.CreateFile({'title': f'{file_name}'})
        my_file.SetContentFile(os.path.join(dir_path, file_name))
        my_file.Upload()
    except Exception as _ex:
        return 'Error'