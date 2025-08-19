import dropbox
import requests
import base64
import os
from tqdm import tqdm

target_path = "/ENGIN-NERS RWS/RWSlite-data-collection/"

class OnlineDB:

    def __init__(self, key, secret, name):
        self.APP_KEY = key
        self.APP_SECRET = secret
        self.STATION_NAME = name
        self.refresh_token = self.init_refresh_token()
    
    def __str__(self):
        return self.STATION_NAME
    
    def init_refresh_token(self):
        refresh_token = ''

        for x in os.listdir():
            if x == 'key':
                with open("key") as f:
                    refresh_token = f.read()

        if not refresh_token:
            initial_access_token, refresh_token = self.get_initial_access_token()
            print("Initial access token:", initial_access_token)
            print("Refresh token:", refresh_token)
            with open("key", 'w+') as f:
                f.write(refresh_token)
            long_lived_access_token = self.refresh_access_token(refresh_token)
            print("Long-lived access token:", long_lived_access_token)
        
        return refresh_token


    # get short-lived access token for user authorization
    def get_initial_access_token(self):
        auth_url = 'https://www.dropbox.com/oauth2/authorize'
        token_url = 'https://api.dropbox.com/oauth2/token'

        auth_url += f'?client_id={self.APP_KEY}&response_type=code&token_access_type=offline'

        print(f"Visit this URL to get an authorization code: {auth_url}")
        auth_code = input("Enter the authorization code: ")

        data = {
            'code': auth_code,
            'grant_type': 'authorization_code',
        }
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{self.APP_KEY}:{self.APP_SECRET}".encode()).decode()}',
        }
        response = requests.post(token_url, data=data, headers=headers)
        response_data = response.json()

        return response_data.get('access_token'), response_data.get('refresh_token')

    # refresh to get longer access token
    def refresh_access_token(self, refresh_token):
        token_url = 'https://api.dropbox.com/oauth2/token'

        data = {
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{self.APP_KEY}:{self.APP_SECRET}".encode()).decode()}',
        }
        response = requests.post(token_url, data=data, headers=headers)
        response_data = response.json()

        print("Long-lived access token:", response_data.get('access_token'))
        return response_data.get('access_token')

    def upload(self,
        file_path,
        timeout=900,
        chunk_size=4 * 1024 * 1024,
    ):
        access_token = self.refresh_access_token(self.refresh_token)
        path = f"{target_path}{self.STATION_NAME}-{file_path}"
        dbx = dropbox.Dropbox(access_token, timeout=timeout)
        with open(file_path, "rb") as f:
            file_size = os.path.getsize(file_path)
            if file_size <= chunk_size:
                print(dbx.files_upload(f.read(), path))
            else:
                with tqdm(total=file_size, desc="Uploaded") as pbar:
                    upload_session_start_result = dbx.files_upload_session_start(
                        f.read(chunk_size)
                    )
                    pbar.update(chunk_size)
                    cursor = dropbox.files.UploadSessionCursor(
                        session_id=upload_session_start_result.session_id,
                        offset=f.tell(),
                    )
                    commit = dropbox.files.CommitInfo(path=path)
                    while f.tell() < file_size:
                        if (file_size - f.tell()) <= chunk_size:
                            print(
                                dbx.files_upload_session_finish(
                                    f.read(chunk_size), cursor, commit
                                )
                            )
                        else:
                            dbx.files_upload_session_append(
                                f.read(chunk_size),
                                cursor.session_id,
                                cursor.offset,
                            )
                            cursor.offset = f.tell()
                        pbar.update(chunk_size)
    
    #TODO
    def get(self, start, end, timeout=900, chunk_size=4*1024*1024):
        print("drop box time TODO")
        access_token = self.refresh_access_token(self.refresh_token)
        dbx = dropbox.Dropbox(access_token, timeout=timeout)
        files = [entry for entry in dbx.files_list_folder(target_path)]
        
