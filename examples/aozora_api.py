from scrapers import AozoraBunkoAPI

aozora = AozoraBunkoAPI()
print(aozora.get_ranking(2020, 1).json())
print(aozora.get_bookinfo(2093).json())