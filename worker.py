import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
from PIL import Image
import PIL
import matplotlib.pyplot as plt
import numpy as np
TEXTURE_DIR = 'dataset/pict_dataset/'
now_array = []
koef = 4
def save_texture(data, name):
  f = open(name, 'wb')

  # Storing the image data inside the data variable to the file
  f.write(data)
  f.close()


def load_sample(file):
  image = Image.open(file)
  image.format = "PNG"
  image.load()
  return image.convert('RGBA')


def get_mean_color(pict):
    x = np.array(pict, dtype='float32')
    me = x.mean(axis=1).mean(axis=0)
    if int(me[-1] != 255):
        return 'delete'
    return me


def reshape_ar(length, array):
    new_array = [[array[i][j] for j in range(0, len(array[i]), len(array[i]) // length)] for i in
                 range(0, len(array), len(array) // length)]
    new_image = Image.fromarray(np.array(new_array)).convert('RGB')
    # new_image.show()
    plt.imshow(new_image)
    # plt.show()
    return new_image


def delete_png(path):
    os.remove(path)


def clear_folder(folder = TEXTURE_DIR):
    import shutil

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


class Dataset():
    def __init__(self, files):
        # download list
        self.data = []
        for i in range(len(files)):
            image = load_sample(files[i])
            mean_color = get_mean_color(image)
            if str(mean_color)=='delete':
              delete_png(files[i])
            else:
              self.data.append([mean_color, files[i].name])
              resh_im = reshape_ar(16, np.array(image))
              resh_im.save(TEXTURE_DIR + files[i].name)

    def get_close_color(self, color):
        block = []
        loss = 99999
        for colors in self.data:
            new_loss = (np.square(color - colors[0][:-1])).mean()
            #print(color, colors[0], loss)
            if new_loss <= loss:
                block = colors
                loss = new_loss
        return block


def change_image(image, k):
    new_image = []
    for i in range(0, len(image), k):
      new_image.append([])
      for j in range(0, len(image[0]), k):
        color = image[i:i+k, j:j+k].mean(axis=1).mean(axis=0)
        new_image[i//k].append(color)
    return np.array(new_image)


def download_textures():
    st_accept = "text/html"  # говорим веб-серверу,
    # что хотим получить html
    # имитируем подключение через браузер Mozilla на macOS
    st_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
    # формируем хеш заголовков
    headers = {
        "Accept": st_accept,
        "User-Agent": st_useragent
    }

    link = 'https://minecraft.fandom.com/wiki/List_of_block_textures'
    # отправляем запрос с заголовками по нужному адресу
    req = requests.get(link, headers)
    # считываем текст HTML-документа
    src = req.text
    src = src[:src.find(
        '<h4><span class="mw-headline" id="Elements"')]  # Убираем лишние данные(хим. элементы, анимированные и удаленные текстуры)
    soup = BeautifulSoup(src, 'lxml')

    pictures = soup.find_all("li", class_="gallerybox")
    for p in pictures:
        inf = p.find('a', class_='image')
        href = inf['href']
        title = inf['title']
        img_data = requests.get(href).content
        save_texture(img_data, TEXTURE_DIR + title.replace(' ', '_').replace('/', '_') + '.png')
        #print(href, title.replace(' ', '_'))


def transform_image(name):
    global now_array
    train_val_files = sorted(list(Path(TEXTURE_DIR).rglob('*.png')))
    dataset = Dataset(train_val_files)
    image = Image.open(name)
    image.convert('RGB')
    image.load()

    #plt.imshow(image)
    #plt.show()

    array = change_image(np.array(image), koef)
    width = len(array)
    height = len(array[0])

    array = array.reshape(width * height, 3)

    new_array = []
    for i in range(len(array)):
        colors = dataset.get_close_color(array[i])
        new_array.append(colors[1])
    fin_ar = np.reshape(np.array(new_array), (height, width), order='F')
    new_image = Image.new('RGB', (height * 16, width * 16))
    now_array = fin_ar
    for i in range(len(fin_ar)):
        for j in range(len(fin_ar[0])):
            texture = Image.open(TEXTURE_DIR + fin_ar[i][j])
            new_image.paste(texture, (i * 16, j * 16))
    return new_image


def get_block(ind1, ind2):
    if len(now_array)!=0:
        return(now_array[ind1][ind2])
    return('')

#clear_folder()
#download_textures()