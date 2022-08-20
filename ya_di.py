import requests
from pprint import pprint


class YandexDisk:

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def get_file_list(self):
        files_url = "https://cloud-api.yandex.net/v1/disk/resources/files"
        headers = self.get_headers()
        response = requests.get(files_url, headers=headers)
        return response.json()

    def get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'  # ссылка на загрузку
        headers = self.get_headers()
        params = {'path': "Netology_Project/1.txt", 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params)
        pprint(response.json())
        return response.json()

    def up_file(self, disk_file_path, filename):
        response_href = self.get_upload_link(disk_file_path=disk_file_path)
        url = response_href.get("href", "")
        response = requests.put(url, data=open(filename, 'rb'))
        response.raise_for_status()
        if response.status_code != 201:
            print('Загрузка произошла с ошибкой')

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def upload(self, file_path: str, file_destinetion: str, file_name):
        uurl = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = ({'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(self.token)})
        params = {'path': file_destinetion, 'overwrite': 'true'}
        answer = requests.get(uurl, headers=headers, params=params)
        url = answer.json().get("href", "")
        response = requests.put(url, data=open(file_path, 'rb'))
        response.raise_for_status()
        if response.status_code != 201:
            print('Загрузка произошла с ошибкой')
