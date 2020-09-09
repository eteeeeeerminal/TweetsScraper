import sys
sys.path.append("../src")
from scrapers import AozoraBunkoAPI

print(AozoraBunkoAPI.get_booktxt(2093).text)