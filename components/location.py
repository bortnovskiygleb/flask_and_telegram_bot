import requests
from config import API_KEY


def get_json(url):
    request = requests.get(url)
    response = request.json()
    return response


def get_cafes(x, y):
    url = f'https://search-maps.yandex.ru/v1/?text=cafe&bbox={x-0.00899},{y-0.00899}~{x+0.00899},{y+0.0089}&lang=ru_RU&rspn=1&results=10&apikey={API_KEY}'
    cafe_list = get_json(url)["features"]
    cafes = {}
    for i in range(len(cafe_list)):
        cafes[cafe_list[i]['properties']['name']] = cafe_list[i]['properties']['description']
    return cafes


def get_pharmacies(x, y):
    url = f'https://search-maps.yandex.ru/v1/?text=pharmacy&bbox={x-0.00899},{y-0.00899}~{x+0.00899},{y+0.0089}&lang=ru_RU&rspn=1&results=10&apikey={API_KEY}'
    pharmacy_list = get_json(url)["features"]
    pharmacies = {}
    for i in range(len(pharmacy_list)):
        pharmacies[pharmacy_list[i]['properties']['name']] = pharmacy_list[i]['properties']['description']
    return pharmacies


def get_atms(x,y):
    url = f'https://search-maps.yandex.ru/v1/?text=ATM&bbox={x-0.00899},{y-0.00899}~{x+0.00899},{y+0.0089}&lang=ru_RU&rspn=1&results=10&apikey={API_KEY}'
    atm_list = get_json(url)["features"]
    atms = {}
    for i in range(len(atm_list)):
        atms[atm_list[i]['properties']['name']] = atm_list[i]['properties']['description']
    return atms
