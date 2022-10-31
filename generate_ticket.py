import io

import requests
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

TEMPLATE_PATH = 'files/ticket_base.png'
FONT_PATH = 'files/Roboto-Regular.ttf'
FONT_SIZE = 40
BLACK = (0, 0, 0, 255)
NAME_OFFSET = (142 , 315)
EMAIL_OFFSET = (152 , 450)
AVATAR_SIZE = 130
AVATAR_OFFSET = (279 , 211)

def generate_ticket(name, email):
    base = Image.open(TEMPLATE_PATH).convert('RGBA')
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    draw = ImageDraw.Draw(base)
    draw.text(NAME_OFFSET, name, font=font, fill=BLACK)
    draw.text(EMAIL_OFFSET, email, font=font, fill=BLACK)

    correct_url = f'https://avatars.dicebear.com/api/adventurer/{email}.com.png?size={AVATAR_SIZE}'
    response = requests.get(url=correct_url)
    # with io.open('face.jpg', 'wb') as f:
    #     f.write(response.content)
    avatar_file_like = BytesIO(response.content) # для того, чтобы не сохранять изображение на компьютер
    avatar = Image.open(avatar_file_like)
    base.paste(avatar, AVATAR_OFFSET)

    temp_file = BytesIO() # снова создаём псевдофайл
    base.save(temp_file, 'png') # пишем в него, как будто это вайловый дискриптор
    temp_file.seek(0) # устанавливаем курсор в начало файла

    return temp_file

generate_ticket('defd', 'dss@dgh.tu')



