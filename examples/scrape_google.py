import os
from scrapers import Google

i = 1
while os.path.exists(save_dir:=f"googlesearch{i}"):
    i += 1

google = Google()
google.search("hogehoge")
google.suggest("hogehoge")
google.save(save_dir)