from config import BannerSetting, UrlSet, PhotoQuerySetting
from PIL import Image, ImageDraw, ImageFont
from io import StringIO, BytesIO
# from six import StringIO

import requests
import dotenv
import os

dotenv.load_dotenv()


def getRandomBackground():
    url = UrlSet.getRamdomPhoto + \
        f'?query={PhotoQuerySetting.query}&count={PhotoQuerySetting.count}'

    request = requests.get(url, headers={
        "Authorization": f'Client-ID {os.getenv("ACCESS_KEY")}'
    })

    photo_data = request.json()

    # fit=crop : to crop photo to fit the specified width and height
    photo_url_list = [photo['urls']['raw'] +
                      f'&w={BannerSetting.width}&h={BannerSetting.height}&fit=crop' for photo in photo_data]

    print(photo_url_list)

    return photo_url_list


def generateBanner(title, bg_url, count):
    request = requests.get(bg_url)
    background_image = Image.open(BytesIO(request.content))

    black_layer = Image.new(
        "RGBA", (BannerSetting.width, BannerSetting.height))
    black_draw = ImageDraw.Draw(black_layer, "RGBA")
    black_draw.rectangle(xy=(0, 0, BannerSetting.width,
                         BannerSetting.height), fill=(0, 0, 0, 100))
    black_layer.putalpha(150)

    logo = Image.open('assets/logo/sciwork.png',)
    logo = logo.resize((logo.width//2, logo.height//2))
    logo_placement = (
        BannerSetting.width // 2 - logo.width // 2,
        BannerSetting.height // 2 - logo.height // 2 - BannerSetting.logo_height_shift,
    )

    banner = Image.new("RGBA", (BannerSetting.width,
                       BannerSetting.height), color=10)
    banner.paste(background_image, (0, 0))
    banner.paste(Image.alpha_composite(banner, black_layer))
    banner.paste(logo, logo_placement, mask=logo)

    font = ImageFont.truetype(
        'assets/font/YanoneKaffeesatz-Regular.ttf', size=50)
    event_title = title
    event_title_box = ImageDraw.Draw(banner)
    event_title_box.text((
        BannerSetting.width // 2,
        BannerSetting.height // 2 + BannerSetting.title_height_shift,
    ), text=event_title, font=font, fill=(255, 255, 255), anchor="ma")

    filename = f'output/{title}_{count}.png'
    banner.save(filename)


if __name__ == "__main__":

    if not os.path.isdir('output'):
        os.makedirs('output')

    event_title = os.getenv("EVENT_TITLE")

    background_urls = getRandomBackground()
    for index, url in enumerate(background_urls):
        generateBanner(event_title, url, index)
