import requests
import os

from .utils import _shape_params

# 参考 : https://github.com/aozorahack/pubserver2
# 参考 : https://github.com/aozorahack/aozora-cli

AOZORAPI_HOST = os.environ.get("AOZORAPI_HOST", "www.aozorahack.net")
AOZORAPI_URL = f"http://{AOZORAPI_HOST}/api/v0.1"

def get_booklist(
    title=None, author=None, fields=None,
    limit=None, skip=None,   after=None
    ) -> requests.Response:
    params = {
        'title' : title, 'author' : author,
        'fields' : fields, 'limit' : limit,
        'skip' : skip, 'after' : after
    }
    params = _shape_params(params)
    return _aozora_get("books", params=params)

def get_bookinfo(book_id:int) -> requests.Response:
    return _aozora_get(f"books/{book_id}")

def get_bookcard(book_id:int) -> requests.Response:
    return _aozora_get(f"books/{book_id}/card")

def get_booktxt(book_id:int) -> requests.Response:
    return _aozora_get(f"books/{book_id}/content?format=txt")

def get_bookhtml(book_id:int) -> requests.Response:
    return _aozora_get(f"books/{book_id}/content?format=html")

def get_personlist(name=None) -> requests.Response:
    params = _shape_params({'name' : name})
    return _aozora_get("persons", params=params)

def get_personinfo(person_id:int) -> requests.Response:
    return _aozora_get(f"persons/{person_id}")

def get_workerlist(name=None) -> requests.Response:
    params = _shape_params({'name' : name})
    return _aozora_get("workers", params=params)

def get_workerinfo(worker_id:int) -> requests.Response:
    return _aozora_get(f"workers/{worker_id}")

def get_ranking(
    year, month, data_type="txt"
    ) -> requests.Response:
    return _aozora_get(f"ranking/{data_type}/{year}/{month:0>2d}")

def _aozora_get(path:str, params={}) -> requests.Response:
    return requests.get(f"{AOZORAPI_URL}/{path}", params=params)