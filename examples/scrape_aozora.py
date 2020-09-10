import os
import sys
sys.path.append("../src")
from scrapers import AozoraBunkoScraper

i = 1
while os.path.exists(save_dir:=f"data/aozorabooks{i}"):
    i += 1

aozora = AozoraBunkoScraper(save_dir)
aozora.get_ranking_books(maximum=5)
aozora.save()