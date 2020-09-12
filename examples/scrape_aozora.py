import os
from scrapers import AozoraBunkoScraper

i = 1
while os.path.exists(save_dir:=f"data/aozorabooks{i}"):
    i += 1

aozora = AozoraBunkoScraper(save_dir)
aozora.get_thepersons_books("夢野久作", maximum=5)
aozora.save()