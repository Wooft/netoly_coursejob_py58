import os
from pprint import pprint
import requests
import wget
import json
from ya_di import YaUploader, YandexDisk
from PIL import Image
from tqdm import tqdm
import pathlib
from GDrive import upload_dir


def GetTokensByFile():
    os.chdir(dir_path)
    with open('tokens.json', 'r') as file_obj:
        data = json.load(file_obj)
        vktoken = data['vk.com']
        yatoken = data['yandex.drive']
    return vktoken, yatoken


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_photos_byid(self):
        url = 'https://api.vk.com/method/photos.get'
        albums = {'Фото профиля:': 'profile', 'Фото со стены': 'wall'}
        albums.update(vk.get_albums())
        print(f'Список доступных альбомов: {albums}')
        while True:
            try:
                album = input('Введите идентификатор альбома: ')
                if album in albums.values():
                    break
                else:
                    print('Идентификатор введен неверно, попробуйте снова!')
            except Exception as e:
                print('Неверный формат')
        params = {'owner_id': user_id, 'album_id': album, 'extended': '1', 'photo_sizes': '1'}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_albums(self):
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {'need_system': 1}
        response = requests.get(url, params={**self.params, **params})
        list_of_albums = {}
        dict_j = response.json()
        for elements in dict_j['response']['items']:
            if elements['title'] == 'Сохранённые фотографии' or elements['title'] == 'Фотографии со мной' or elements[
                'id'] == -6 or elements['id'] == -7:
                pass
            else:
                list_of_albums[elements['title']] = str(elements['id'])
        return list_of_albums

    def load_photos(self):
        list_download_photos = []  # создаем список скачаных фото
        count_files = 0  # счетчик количества повторов для фото с одинаковым количество лайков
        ready_upload = []  # Словарь для хранения списка фото, готовых к загрузке
        if 'temp' not in os.listdir(dir_path):
            os.mkdir('temp')
        if len(os.listdir(temp_path)) != 0:
            vk.clear_temp_dir()
        else:
            pass
        os.chdir(temp_path)
        d_photos = vk.get_photos_byid()  # Получаем список фото из профиля
        download_dict = {}
        list_names_photo = []
        for elements in d_photos['response']['items']:  # Сохраняем фото в папку temp, присваиваем каждому фото название в виде количества лайков
            j_dict = {}
            file_info = {}  # Создаем словарь для хранения инфо о файле
            flag = 0  # временная переменная флаг
            list_of_h = []  # список для хранения данных о разрешении фото
            file_info['file_name'] = f'{elements["likes"]["count"]}'
            name_file = file_info['file_name']  # промежуточная переменная для хранения имени файла
            while flag != 1:  # цикл установки уникального имени файла
                if name_file in list_names_photo:  # проверка на то, есть ли новый файл в списке файлов
                    count_files += 1  # увеличиваем счетчик повтора на 1
                    name_file = file_info['file_name']  # переприсваиваем переменную
                    name_file = f"{name_file}({count_files})"  # устанавливаем имя фото на тип likes(count)
                else:
                    file_info['file_name'] = f'{name_file}.jpg'  # если имя файла уникально то изменяем флаг на 1 и прерываем цикл

                    j_dict['file_name'] = file_info['file_name']
                    list_names_photo.append(name_file)
                    flag += 1
            for values in elements['sizes']:  # Получение списка разрешений (по высоте) для каждого фото
                list_of_h.append(values['height'])
            max_heigt = max(list_of_h)  # отбор максимального разрешения для фото
            for values in elements['sizes']:
                if values['height'] == max_heigt:
                    file_info['size'] = values['type']
                    j_dict['size'] = values['type']
                    link = values['url']  # получаем URL для фото в максимальном разрешении
            download_dict[file_info['file_name']] = link
            list_download_photos.append(file_info)
            count_files = 0
            ready_upload.append(j_dict)
        for keys, elements in tqdm(download_dict.items()):
            wget.download(elements, keys)
        print('Все фото скачаны в папку "temp"')
        with open('info.json', 'w+') as file_obj:
            json.dump(ready_upload, file_obj)  # сохраняем метаданных в json файл
    def prepare_photo_to_upload(self):
        os.chdir(temp_path)
        files_list = []  # создание пустого списка ддля того, чтобы добавить в него все фото из папки temp
        d_photos = {}  # словарь для хранения разрешений фото
        while True:
            try:
                answer = input('По умолчанию будет загружено 5 фото, хотите установить другое количество фотографий для выгрузки? (Да/Нет)')
                if answer.lower() == 'да':
                    num_f = int(input("Введите количество фото, которое хотите загрузить: "))
                    break
                if answer.lower() == 'нет':
                    num_f = 5
                    break
            except Exception as e:
                print('Данные введены неверно, попробуйте снова!')
        for files in os.listdir(temp_path):
            if files.endswith(".jpg"):
                files_list.append(files)
        if len(files_list) == 0:
            print('Нет файлов для загрузки')
        elif len(files_list) < num_f:
            num_f = len(files_list)
        for elements in files_list:
            im = Image.open(elements)
            res = im.size[0] * im.size[1]  # вычисление количества пикселей в фото
            d_photos[elements] = res  # сохраняем разрешение в словарь, где ключ - имя фото
        result = sorted(d_photos.items(), key=lambda x: (-x[1], x[0]))  # сортировка словаря и сохранение значений в список кортежей, где максимальные значения разрешений находятся в начале списка
        return result, num_f

    def uploadPhotostoyadi(self):
        os.chdir(temp_path)
        print('Подготовка к загрузке фото на Яндекс Диск')
        vk.create_folder()
        list_to_upload, num_f = vk.prepare_photo_to_upload()
        print(f'Началась загрузка {num_f} фото на Яндекс.диск:')
        for i in tqdm(list_to_upload[0:num_f]):
            vk.uploadFiletoDisk(i[0])
        print('Загрузка прошла успешно!')
        vk.clear_temp_dir()

    def uploadFiletoDisk(self, files):
        vktoken, yatoken = GetTokensByFile()
        file_destination = f'Netology_Project/{files}'
        TOKEN = yatoken
        uploader = YaUploader(token=TOKEN)
        uploader.upload(os.path.join(temp_path, files), file_destination)

    def uploadfiletoGoogle(self):
        print('Подготовка к загрузке фото на Google Drive')
        list_to_upload, num_f = vk.prepare_photo_to_upload()
        print(f'Началась загрузка {num_f} фото на Google Drive:')
        for i in tqdm(list_to_upload[0:num_f]):
            upload_dir(temp_path, i[0])
        print('Загрузка прошла успешно!')
        vk.clear_temp_dir()

    def clear_temp_dir(self):
        while True:
            try:
                answer = input('Вы хотите очистить файлы во временной папке? (Да/Нет)')
                if answer.lower() == 'да':
                    for files in os.listdir(temp_path):
                        os.remove(os.path.join(temp_path, files))
                    break
                elif answer.lower() == 'нет':
                    break
            except Exception as e:
                print('Данные введены неверно, попробуйте снова!')

    def create_folder(self):
        vktoken, yatoken = GetTokensByFile()
        TOKEN = yatoken
        folders = YandexDisk(token = TOKEN)
        while True:
            try:
                answer = input('Хотите создать папку "Netology_Project" для загрузки в неё файлов (да/нет)?')
                if answer.lower() == 'да':
                    response = folders.create_folder('Netology_Project')
                    break
                if answer.lower() == 'нет':
                    response = None
                    break
            except Exception as e:
                print('Данные введены неверно, попробуйте снова!')
        return response


dir_path = pathlib.Path.cwd()
temp_path = os.path.join(dir_path, 'temp')
vktoken, yatoken = GetTokensByFile()
access_token = vktoken
TOKEN = yatoken
user_id = input('Введите ID пользователя: ')
vk = VK(access_token, user_id)

vk.load_photos()
vk.uploadPhotostoyadi()
vk.uploadfiletoGoogle()
