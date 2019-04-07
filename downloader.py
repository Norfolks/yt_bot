import uuid
from io import BytesIO

import requests
import youtube_dl
from PIL import Image




class VideoMeta:
    def __init__(self, meta, file_name, cover):
        self.meta = meta
        self.file_name = file_name
        self.cover = cover


def download_video(video_link):
    id = str(uuid.uuid4())[:7]
    file_id = id + '.ogg'
    ydl_opts = {
        'format': 'worstaudio/worst',  # 'worstaudio/worst', 'bestaudio/best'
        'outtmpl': file_id,
        'audioformat': "aac"

    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_link, download=True)
        # ydl.download([video_link])
        response = requests.get(info_dict['thumbnails'][0]['url'])
        cover_name = id + 'cover.jpeg'
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        new_width, new_height = width, height
        if width > height:
            new_width = height
        else:
            new_height = width

        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        img.crop((left, top, right, bottom))
        img.thumbnail((90, 90))
        img.save(cover_name)

        meta = VideoMeta(info_dict, id + '.ogg', cover_name)


    return meta


if __name__ == '__main__':
    download_video('https://www.youtube.com/watch?v=KwHY7WGwd4c')
