import os
from scrapers import NarouAPI
from scrapers.utils import _write_json

i = 1
while os.path.exists(save_dir:=f"data/narou{i}.json"):
    i += 1

data = NarouAPI.narou_get()
_write_json(save_dir, data)