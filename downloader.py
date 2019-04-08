import os
import uuid
from io import BytesIO

import requests
import youtube_dl
from PIL import Image
from pydub import AudioSegment


class VideoMeta:
    def __init__(self, meta, file_name, cover):
        self.meta = meta
        self.file_name = file_name
        self.cover = cover


def download_worst(video_link):
    id = str(uuid.uuid4())[:7]
    file_id = id + '.wav'
    ydl_opts = {
        'format': 'worstaudio/worst',  # 'worstaudio/worst', 'bestaudio/best'
        'outtmpl': file_id,
        'audioformat': "aac"

    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_link, download=True)
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

        meta = VideoMeta(info_dict, file_id, cover_name)

    return meta


def download_best(video_link):
    id = str(uuid.uuid4())[:7]
    file_id = id + '.wav'
    ydl_opts = {
        'format': 'bestaudio/best',  # 'worstaudio/worst', 'bestaudio/best'
        'outtmpl': file_id,
        'audioformat': "mp3"

    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_link, download=True)
        response = requests.get(info_dict['thumbnails'][0]['url'])
        cover_name = id + 'cover.jpeg'
        img = Image.open(BytesIO(response.content))
        original_cover = "orginal_cover.jpeg"
        img.save("orginal_cover.jpeg")
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
        AudioSegment.from_file(file_id).export(file_id, format="mp3",
                                               tags={"title": info_dict.get('title'),
                                                     "artist": info_dict.get('uploader')},
                                               cover=original_cover
                                               )
        os.remove(original_cover)

        meta = VideoMeta(info_dict, file_id, cover_name)

    return meta


def download_video(video_link, quality=None):
    if quality is None or quality == 'min':
        return download_worst(video_link)
    else:
        return download_best(video_link)


if __name__ == '__main__':
    download_video('https://www.youtube.com/watch?v=KwHY7WGwd4c')
