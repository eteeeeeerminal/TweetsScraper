import os
import sys
sys.path.append("../src")
from scrapers import Google

i = 1
while os.path.exists(save_dir:=f"googlesearch{i}"):
    i += 1

google = Google()
google.search("apex")
google.save(save_dir)