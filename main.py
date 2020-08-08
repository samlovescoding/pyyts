import requests
import bs4
import pymongo
import multiprocessing
import fake_useragent
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "https://yts.mx/"
TORRENT_URL = BASE_URL + "movies/{}"
LIST_URL = BASE_URL + "browse-movies?page={}"
STARTING_PAGE = 1
ENDING_PAGE = 908
DB = pymongo.MongoClient('localhost', 27017).yts
USER_AGENT = fake_useragent.UserAgent().chrome
headers = {'User-Agent': USER_AGENT}
driver = webdriver.Chrome(ChromeDriverManager().install())


def get_driver():
    return webdriver.Chrome(ChromeDriverManager().install())


def write(file, data = None, mode="w"):
    if data is None:
        data = file
        file = "write.html"
    f = open(file, mode, encoding='utf-8')
    f.write(data)
    f.close()
    return data


def read(file, mode="r"):
    f = open(file, mode)
    data = f.read()
    f.close()
    return data


def source(url):
    driver.get(url)
    while driver.title == "Just a moment...":
        print("Waiting 1 sec for cloudflare IUAM")
        time.sleep(1)
    data =  driver.page_source
    return data


def soup(url):
    return bs4.BeautifulSoup(source(url), 'html.parser')


def get_soup_from_movie_id(id):
    return soup(TORRENT_URL.format(id))


def get_magnets_from_soup(s):
    magnets = []
    for div in s.findAll('div', {'class': 'modal-torrent'}):
        anchor = div.find('a', {'class': 'magnet-download'})
        quality = div.findAll('span').pop(0).get_text()
        quality_size = div.findAll('p', {'class': 'quality-size'}).pop(1).get_text()
        magnets.append({
            'link': anchor.get('href'),
            'quality': quality.strip(),
            'quality_size': quality_size.strip()
        })
    return magnets


def get_name_from_soup(s):
    h1 = s.find('h1')
    name = h1.get_text()
    return name


def get_year_from_soup(s):
    h2 = s.findAll('h2').pop(0)
    year = h2.get_text()
    return year


def get_genres_from_soup(s):
    h2 = s.findAll('h2').pop()
    genres = h2.get_text().split(' / ')
    return genres


def get_description_from_soup(s):
    div = s.find("div", {'id': 'synopsis'})
    description = div.findAll('p').pop(1).get_text()
    return description


def get_details_from_soup(s, slug):
    movie_info_soup = s.find("div", {'id': "movie-info"})
    return {
        "name" : get_name_from_soup(movie_info_soup),
        "year" : get_year_from_soup(movie_info_soup),
        "genres" : get_genres_from_soup(movie_info_soup),
        "magnets" : get_magnets_from_soup(s),
        'description': get_description_from_soup(s),
        'slug': slug
    }


def download_movie(movie):
    id = movie["slug"]
    n = DB.torrents.count_documents({'slug': id})
    if n == 0:
        print("Downloading", id)
        s = get_soup_from_movie_id(id)
        d = get_details_from_soup(s, id)
        DB.torrents.insert_one(d)
    else:
        print("Skipping", id)


def get_ids_from_list_page(num):
    print("Downloading ids from page", num)
    ids = []
    url = LIST_URL.format(num)
    s = soup(url)
    for anchor in s.findAll('a', {'class': 'browse-movie-link'}):
        link = anchor.get('href')
        id = link.split('/').pop()
        ids.append({
            'slug': id
        })
    DB.ids.insert_many(ids)


def lrange(*args, **kwargs):
    l = []
    for i in range(*args, **kwargs):
        l.append(i)
    return l


def download_ids_parallel():
    with multiprocessing.Pool(10) as p:
        p.map(get_ids_from_list_page, lrange(STARTING_PAGE, ENDING_PAGE+1))


def download_ids():
    for i in range(STARTING_PAGE, ENDING_PAGE+1):
        get_ids_from_list_page(i)


def download_ids_safe():
    print("Downloading sitemap")
    s = soup(BASE_URL + 'sitemap.xml')
    print("Downloaded sitemap")
    for loc in s.findAll('loc'):
        movie_id = loc.get_text().split("/").pop()
        DB.movie_ids.insert_one({
            'slug': movie_id
        })

def download_all_movies():
    for movie in DB.movie_ids.find():
        try:
            download_movie(movie)
        except Exception as e:
            write("log.txt", str(e), "a")
        

download_ids_safe()
download_all_movies()
driver.close()