import os
from pprint import pprint
import requests
import wget
import json
from ya_di import YaUploader
from PIL import Image
from tqdm import tqdm
from GDrive import upload_dir

def GetTokensByFile():
    with open('/home/wooft/PycharmProjects/API VK/tokens.json', 'r') as file_obj:
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
       us_id = int(input('Введите ID пользователя: '))
       print(f'Список доступных альбомов: {albums}')
       while True:
           try:
               album = input('Введите идентификатор альбома: ')
               if album == 'profile' or album == 'wall':
                   break
               else:
                   print('Введены неверные данные, попробуйте снова!')
           except Exception as e:
               print('Неверный формат')
       params = {'owner_id': us_id, 'album_id': album, 'extended': '1', 'photo_sizes': '1'}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

   def get_albums(self):
       url = 'https://api.vk.com/method/photos.getAlbums'
       us_id = int(input('Введите ID пользователя: '))
       params = {'need_system': 1}
       response = requests.get(url, params={**self.params, **params})
       list_of_albums = []
       pprint(response.json())
       dict_j = response.json()
       for elements in dict_j['response']['items']:
           list_of_albums.append(elements['title'])
       print(list_of_albums)

   def load_photos(self):
       list_download_photos = [] #создаем список скачаных фото
       count = 0  # счетчик порядкового номера фото
       count_files = 0  # счетчик количества повторений фала для фото с одинаковым количество лайков
       ready_upload = {} #Словарь для хранения списка фото, готовых к загрузке
       if 'temp' not in os.listdir():
           os.mkdir('temp')
       files_list = os.listdir('/home/wooft/PycharmProjects/API VK/temp') #Получение списка файлов временной длиректории
       os.chdir('/home/wooft/PycharmProjects/API VK/temp')
       d_photos = vk.get_photos_byid() #Получаем список фото из профиля
       for elements in d_photos['response']['items']: #Сохраняем фото в папку temp, присваиваем каждому фото название в виде количества лайков
           files_temp_list = [] #пустой список
           file_info = {} #Создаем словарь для хранения инфо о файле
           flag = 0  # временная переменная флаг
           list_of_h = [] #список для хранения данных о разрешении фото
           file_info['file_name'] = f'{elements["likes"]["count"]}'
           files_temp_list = os.listdir('/home/wooft/PycharmProjects/API VK/temp') #получение спсика файлов
           name_file = file_info['file_name'] #промежуточная переменная для хранения имени файла
           while flag != 1: #цикл установки уникального имени файла
               if f"{name_file}.jpg" in files_temp_list: #проверка на то, есть ли новый файл в списке файлов
                   count_files += 1 #увеличиваем счетчик повтора на 1
                   name_file = file_info['file_name'] #переприсваиваем переменную
                   name_file = f"{name_file}({count_files})" #устанавливаем имя фото на тип likes(count).jpg
               else:
                   file_info['file_name'] = f'{name_file}.jpg' #если имя файла уникально то изменяем флаг на 1 и прерываем цикл
                   flag += 1
           count += 1
           for values in elements['sizes']: #Получение списка разрешений (по высоте) для каждого фото
               list_of_h.append(values['height'])
           max_heigt = max(list_of_h) #отбор максимального разрешения для фото
           for values in elements['sizes']:
               if values['height'] == max_heigt:
                   file_info['size'] = values['type']
                   link = values['url'] #получаем URL для фото в максимальном разрешении
           wget.download(link, file_info['file_name'])
           pprint(f"Фотография № {count} из {d_photos['response']['count']} скачана успешно")
           list_download_photos.append(file_info)
           count_files = 0
       print('Все фото скачаны в папку "temp"')
       with open('info.json', 'w+') as file_obj:
           json.dump(ready_upload, file_obj) #сохраняем метаданных в json файл

   def prepare_photo_to_upload(self):
       files_list = []  # создание пустого списка ддля того, чтобы добавить в него все фото из папки temp
       counter = 0
       d_photos = {}  # словарь для хранения разрешений фото
       while True:
           try:
               answer = input('По умолчанию будет загружено 5 фото, хотите установить другое количество фотографий для выгрузки? (Да/Нет)')
               if answer == 'Да':
                   num_f = int(input("Введите количество фото, которое хотите загрузить: "))
                   break
               if answer == 'Нет':
                   num_f = 5
                   break
           except Exception as e:
               print('Неверный формат')
       os.chdir('/home/wooft/PycharmProjects/API VK/temp')
       for files in os.listdir('/home/wooft/PycharmProjects/API VK/temp'):
           if files.endswith(".jpg"):
               files_list.append(files)
       if len(files_list) == 0:
           print('Нет файлов для загрузки')
       for elements in files_list:
           im = Image.open(elements)
           res = im.size[0] * im.size[1] #вычисление количества пикселей в фото
           d_photos[elements] = res #сохраняем разрешение в словарь, где ключ - имя фото
       result = sorted(d_photos.items(), key=lambda x: (-x[1], x[0])) #сортировка словаря и сохранение значений в список кортежей, где максимальные значения разрешений находятся в начале списка
       return result, num_f

   def uploadPhotostoyadi(self):
       print('Подготовка к загрузке фото на Яндекс Диск')
       list_to_upload, num_f = vk.prepare_photo_to_upload()
       print(f'Началась загрузка {num_f} фото на Яндекс.диск:')
       for i in tqdm(list_to_upload[0:num_f]):
           vk.uploadFiletoDisk(i[0])
       print('Загрузка прошла успешно!')

   def uploadFiletoDisk(self, files):
       vktoken, yatoken = GetTokensByFile()
       path_to_file = f'/home/wooft/PycharmProjects/API VK/temp/{files}'
       file_destination = f'Netology_Project/{files}'
       TOKEN = yatoken
       uploader = YaUploader(token=TOKEN)
       uploader.upload(path_to_file, file_destination)

   def uploadfiletoGoogle(self):
       print('Подготовка к загрузке фото на Google Drive')
       dir_path = '/home/wooft/PycharmProjects/API VK/temp'
       list_to_upload, num_f = vk.prepare_photo_to_upload()
       print(f'Началась загрузка {num_f} фото на Google Drive:')
       for i in tqdm(list_to_upload[0:num_f]):
           upload_dir(dir_path, i[0])
       print('Загрузка прошла успешно!')
       while True:
           try:
               answer = input('Вы хотите очистить файлы во временной папке? (Да/Нет)')
               if answer == 'Да':
                   for files in os.listdir(dir_path):
                       os.remove(files)
                   break
               if answer == 'Нет':
                   break
           except Exception as e:
               print('Неверный формат ввода')

vktoken, yatoken = GetTokensByFile()
access_token = vktoken
user_id = '15565301'
vk = VK(access_token, user_id)

vk.load_photos()
vk.uploadPhotostoyadi()
vk.uploadfiletoGoogle()
