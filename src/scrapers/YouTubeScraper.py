import requests
import logging
import codecs
import json

# 参考 : https://github.com/pusaitou/mikochiku_alarm

from .utils import _get_item

class YouTubeScraper:
    headers = {
        'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) '
                     'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                     'CriOS/69.0.3497.91 Mobile/15E148 Safari/605.1',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.5',
        'x-youtube-client-name': '2',
        'x-youtube-client-version': '2.20200410'
    }

    p_contents = [
        'response',
        'contents',
        'singleColumnBrowseResultsRenderer',
        'tabs',
        1,
        'tabRenderer',
        'content',
        'sectionListRenderer',
        'contents',
        0,
        'itemSectionRenderer',
        'contents'
    ]

    px_vid = [
        'compactVideoRenderer',
        'videoId',
    ]

    px_status = [
        'compactVideoRenderer',
        'thumbnailOverlays',
        0,
        'thumbnailOverlayTimeStatusRenderer',
        'style'
    ]

    def __init__(self):
        self.live_chats = None
        self.video_chats = None

    def extract_video_ids(self, info, only_live=True):
        # ページから取得した情報から必要な情報だけ抜き取る

        contents = _get_item(info, self.p_contents) or []

        return [_get_item(c, self.px_vid) for c in contents
                if (not only_live) or _get_item(c, self.px_status) == 'LIVE']

    def get_video_pages(self, channel_id):
        url = f'https://m.youtube.com/channel/{channel_id}/videos'
        params = {'view':2, 'flow':'list', 'pbj':1}
        response = requests.get(url, params=params, headers=self.headers)

        return response.json()

    def get_live_chats(self, video_id):
        pass

    def get_video_comments(self, video_id):
        pass

    def save(self):
        pass