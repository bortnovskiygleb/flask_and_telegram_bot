import requests as req
from bs4 import BeautifulSoup as bs
import re
from requests import ConnectionError


def get_html(url):
    r = req.get(url)
    if r.status_code != 200:
        raise ConnectionError
    return r


def get_weather_by_html(html):
    soup = bs(html.text, 'lxml')
    divs = soup.find_all('li', {'class': ['fact__hour swiper-slide']})
    pattern = r'\d?\d\D\d\d'
    weather = {}
    for div in divs:
        if 'Восход' not in div.find('div', {'class': ['fact__hour-temp']}).get_text() and 'Закат' not in div.find('div',{ 'class': ['fact__hour-temp']}).get_text():
            time = div.find('div', {'class': ['fact__hour-label']}).get_text()
            temp = div.find('div', {'class': ['fact__hour-temp']}).get_text()
            match = re.findall(pattern, time)[0]
            weather[match] = temp
    return weather

def get_weather_by_city(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&type=like&APPID=e778911b6aaa21ee4a3183b181792bf9'
    response = req.get(url).json()
    if(response['cod'] != 200):
        return response['message']
    return f'Now in {city} ' + response['weather'][0]['description'] + ', temperature ' + str(int(response['main']['temp'])-273) +'° C'

def get_weather():
    return get_weather_by_html(get_html("https://yandex.by/pogoda/minsk"))
