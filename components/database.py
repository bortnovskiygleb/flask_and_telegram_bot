import pymysql
from components import get_money_on_date, get_weather, get_money, get_movies
import requests
from bs4 import BeautifulSoup as bs
from requests import ConnectionError
from config import PASSWORD
import calendar
from datetime import timedelta


def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password=PASSWORD,
        charset='utf8mb4',
        db='graduation_project_base',
        cursorclass=pymysql.cursors.DictCursor
    )


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_html(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise requests.ConnectionError
    return r


def select_money_by_date(year, month, day, cursor):
    date = f'{year}-{month}-{day}'
    sql = f"select name, value from courses where date='{date}'"

    cursor.execute(sql)
    money = {}
    for row in cursor:
        money[row['name']] = row['value']
    return money


def select_courses_by_date(year, month, day):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            return select_money_by_date(year, month, day, cursor)
    except pymysql.err.InternalError:
        return -1
    except IndexError:
        return -1
    finally:
        connection.close()


def select_weather_by_date(year, month, day):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            date = f"{year}-{month}-{day}"
            cursor.execute(f"select day_temperature,night_temperature from weather where date='{date}'")
            return cursor.fetchall()[0]
    except pymysql.err.InternalError:
        return -1
    except IndexError:
        return -1
    finally:
        connection.close()


def select_movies_by_date(year, month, day):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            date = f"{year}-{month}-{day}"
            cursor.execute(f"select name from movies where date='{date}'")
            return cursor.fetchall()
    except pymysql.err.InternalError:
        return -1
    except IndexError:
        return -1
    finally:
        connection.close()


def insert_current_weather_in_database():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            list_weather = get_weather()
            cursor.execute("TRUNCATE TABLE current_weather")
            for time, temp in list_weather.items():
                params = (time, temp)
                cursor.execute("INSERT INTO current_weather (time, temperature) VALUES (%s, %s)", params)
            connection.commit()
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def select_current_weather():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT time, temperature FROM current_weather")
            return cursor.fetchall()
    except pymysql.err.InternalError:
        return -1
    finally:
        connection.close()


def insert_current_courses_in_database():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            list_courses = get_money()
            cursor.execute("TRUNCATE TABLE current_courses")
            for money in list_courses:
                params = (money["Cur_OfficialRate"], money["Cur_Name"])
                cursor.execute("INSERT INTO current_courses (course, name) VALUES (%s, %s)", params)
            connection.commit()
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def select_current_courses():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT course, name FROM current_courses")
            return cursor.fetchall()
    except pymysql.err.InternalError:
        return -1
    finally:
        connection.close()


def insert_current_movies_in_database():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            list_movies = get_movies()
            cursor.execute("TRUNCATE TABLE current_movies")
            for movie in list_movies:
                cursor.execute("INSERT INTO current_movies (name) VALUES (%s)", movie)
            connection.commit()
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def select_current_movies():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM current_movies")
            return cursor.fetchall()
    except pymysql.err.InternalError:
        return -1
    finally:
        connection.close()


def delete_movies_in_database(cur_datetime):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            dif4 = cur_datetime.day + 31 * 3
            delta4 = timedelta(days=dif4)
            old_date4 = cur_datetime - delta4
            old_monthrange4 = calendar.monthrange(old_date4.year, old_date4.month)[1]

            cursor.execute(f"DELETE FROM movies WHERE date BETWEEN '{old_date4.year}-{old_date4.month}-1' AND '{old_date4.year}-{old_date4.month}-{old_monthrange4}'")

            connection.commit()
            return 1
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def update_movies_in_database(start_date, end_date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            for single_date in daterange(start_date, end_date):
                url = f'https://www.kinopoisk.ru/premiere/ru/date/{single_date.year}-{single_date.month}-{single_date.day}/'
                html = get_html(url)
                soup = bs(html.text, 'lxml')
                blocks = soup.find_all('div', {'class': ['premier_item']})
                for block in blocks:
                    name = block.find('span', {'class': ['name']}).find('a').get_text()
                    params = (name, f'{single_date.year}-{single_date.month}-{single_date.day}')
                    cursor.execute("INSERT INTO movies (name, date) VALUES (%s, %s)", params)

            connection.commit()
            return 1
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def delete_weather_in_database(cur_datetime):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            dif4 = cur_datetime.day + 31 * 3
            delta4 = timedelta(days=dif4)
            old_date4 = cur_datetime - delta4
            old_monthrange4 = calendar.monthrange(old_date4.year, old_date4.month)[1]

            cursor.execute(f"DELETE FROM weather WHERE date BETWEEN '{old_date4.year}-{old_date4.month}-1' AND '{old_date4.year}-{old_date4.month}-{old_monthrange4}'")
            connection.commit()
            return 1
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def update_weather_in_database(start_date, end_date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            for single_date in daterange(start_date, end_date):
                url = f"https://pogoda.mail.ru/prognoz/minsk/{single_date.day}-{single_date.strftime(r'%B').lower()}/#{single_date.year}"
                html = get_html(url)
                soup = bs(html.text, 'lxml')
                blocks = \
                soup.find_all('div', {'class': ['cols__column__item cols__column__item_2-1 cols__column__item_2-1_ie8']})[0]
                temperature = blocks.find_all('div', {'class': {'day__temperature'}})

                day_temperature = temperature[2].get_text()
                night_temperature = temperature[0].get_text()
                params = (day_temperature, night_temperature, f'{single_date.year}-{single_date.month}-{single_date.day}')
                cursor.execute("INSERT INTO weather (day_temperature, night_temperature, date) VALUES (%s, %s, %s)", params)

            connection.commit()
            return 1
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def delete_courses_in_database(cur_datetime):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            dif4 = cur_datetime.day + 31 * 3
            delta4 = timedelta(days=dif4)
            old_date4 = cur_datetime - delta4
            old_monthrange4 = calendar.monthrange(old_date4.year, old_date4.month)[1]

            cursor.execute(f"DELETE FROM courses WHERE date BETWEEN '{old_date4.year}-{old_date4.month}-1' AND '{old_date4.year}-{old_date4.month}-{old_monthrange4}'")

            connection.commit()
            return 1
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def update_courses_in_database(start_date, end_date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            for single_date in daterange(start_date, end_date):
                list_courses = get_money_on_date(f'{single_date.day}-{single_date.month}-{single_date.year}')
                for course in list_courses:
                    money = (course['Cur_Name'], course['Cur_OfficialRate'], course['Date'].split('T')[0])
                    cursor.execute("INSERT INTO courses (name, value, date) VALUES (%s, %s, %s)", money)

            connection.commit()
            return 1
    except pymysql.err.InternalError:
        return -1
    except ConnectionError:
        return -1
    finally:
        connection.close()


def update_information_time(hour, minute, second):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:

            cursor.execute(
                f"UPDATE update_information SET time='{hour}:{minute}:{second}'")

            connection.commit()
            return 1
    except pymysql.err.InternalError:
        return -1
    finally:
        connection.close()


def select_time():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:

            cursor.execute(
                f"SELECT time FROM update_information")

            return cursor.fetchone()['time']
    except pymysql.err.InternalError:
        return -1
    finally:
        connection.close()


def update_information_date(year, month, day):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:

            cursor.execute(
                f"UPDATE update_information SET date='{year}-{month}-{day}'")

            connection.commit()
            return 1
    except pymysql.err.InternalError:
        return -1
    finally:
        connection.close()


def select_date():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:

            cursor.execute(
                f"SELECT date FROM update_information")

            return cursor.fetchone()['date']
    except pymysql.err.InternalError:
        return -1
    finally:
        connection.close()
