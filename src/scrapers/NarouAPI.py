import os
import json
import requests
import gzip

from .utils import _shape_params

# see https://dev.syosetu.com/man/api/

NAROU_URL = "https://api.syosetu.com/novelapi/api/"

NAROU_BIGGENRE = {
    "恋愛" : 1,
    "ファンタジー" : 2,
    "文芸" : 3,
    "SF" : 4,
    "その他" : 99,
    "ノンジャンル" : 98
}

NAROU_GENRE = {
    '異世界〔恋愛〕': 101, '現実世界〔恋愛〕': 102,
    'ハイファンタジー〔ファンタジー〕': 201, 'ローファンタジー〔ファンタジー〕': 202,
    '純文学〔文芸〕': 301, 'ヒューマンドラマ〔文芸〕': 302, '歴史〔文芸〕': 303,
    '推理〔文芸〕': 304, 'ホラー〔文芸〕': 305, 'アクション〔文芸〕': 306, 'コメディー〔文芸〕': 307,
    'VRゲーム〔SF〕': 401, '宇宙〔SF〕': 402, '空想科学〔SF〕': 403, 'パニック〔SF〕': 404,
    '童話〔その他〕': 9901, '詩〔その他〕': 9902, 'エッセイ〔その他〕': 9903,
    'リプレイ〔その他〕': 9904, 'その他〔その他〕': 9999,
    'ノンジャンル〔ノンジャンル〕': 9801
}

def narou_get(of=None, lim=20, st=0, order="hyoka", **kwargs):
    compress_level = 5
    params = {
        'gzip': compress_level,
        'out' : "json",
        'of' : of,
        'lim' : lim,
        'st' : st,
        'order' : order
    }
    params.update(kwargs)
    params = _shape_params(params)
    content =  requests.get(NAROU_URL, params=params).content
    with open("temp.gz", 'wb') as f:
        f.write(content)
    with gzip.open("temp.gz", 'rb', compress_level) as f:
        res_json = json.loads(f.read())
    os.remove("temp.gz")
    return res_json

if __name__ == "__main__":
    from .utils import logger, _read_json, _write_json
    _write_json("narou.json", narou_get())