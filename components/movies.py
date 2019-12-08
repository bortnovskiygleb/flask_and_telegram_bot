import requests
from bs4 import BeautifulSoup as bs


def get_html(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise requests.ConnectionError
    return r


def get_list_movies(html):
    soup = bs(html.text, 'lxml')
    premieres = soup.find('div', {'class': ['events-block js-cut_wrapper']})
    rows = premieres.find_all('ul', {'class': ['b-lists list_afisha col-5']})
    movies = []
    for row in rows:
        articles = row.find_all('li', {'class': ['lists__li']})
        for art in articles:
            movies.append(art.find('a', {'class': ['name']}).find('span').get_text())
    return movies

def get_movies():
    return get_list_movies(get_html("https://afisha.tut.by/film/"))

def get_movies_with_img():
    html = get_html("https://afisha.tut.by/film/")
    soup = bs(html.text, 'lxml')
    premieres = soup.find('div', {'class': ['events-block js-cut_wrapper']})
    rows = premieres.find_all('ul', {'class': ['b-lists list_afisha col-5']})
    movies = {}
    for row in rows:
        articles = row.find_all('li', {'class': ['lists__li']})
        for art in articles:
            movies[art.find('a', {'class': ['name']}).find('span').get_text()] = art.find('a', {'class': ['media']}).find('img').get('src')
    return movies
