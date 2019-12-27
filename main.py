from flask import Flask, render_template, request
from components import *
from datetime import datetime
import datetime

app = Flask(__name__)


@app.route('/')
def index():
    up_date = select_date()
    hours = select_time().total_seconds() // 3600
    new_date = datetime.datetime.now().date()
    if datetime.datetime.today().month - up_date.month == 1 or datetime.datetime.today().month - up_date.month == -11:
        delete_movies_in_database(new_date)
        delete_weather_in_database(new_date)
        delete_courses_in_database(new_date)
        update_movies_in_database(up_date, new_date)
        update_weather_in_database(up_date, new_date)
        update_courses_in_database(up_date, new_date)
        update_information_date(new_date.year, new_date.month, new_date.day)
    elif new_date.day != up_date.day:
        update_movies_in_database(up_date, new_date)
        update_weather_in_database(up_date, new_date)
        update_courses_in_database(up_date, new_date)
        update_information_date(new_date.year, new_date.month, new_date.day)
    if abs(datetime.datetime.now().hour - hours) > 0:
        insert_current_weather_in_database()
        insert_current_courses_in_database()
        insert_current_movies_in_database()
        new_time = datetime.datetime.now()
        update_information_time(new_time.hour, new_time.minute, new_time.second)

    return render_template('index.html')


@app.route('/movies')
def movies():
    list_movies = select_current_movies()
    return render_template(
        'movies.html',
        list_movies=list_movies
    )


@app.route('/courses')
def courses():
    list_courses = select_current_courses()
    return render_template(
        'courses.html',
        courses=list_courses,
        today=datetime.datetime.now().date()
    )


@app.route('/weather')
def weather():
    list_weather = select_current_weather()
    three_hours_weather = dict()
    c = 0
    for i in list_weather:
        if c == 3:
            break
        three_hours_weather[i['time']] = i['temperature']
        c += 1
    return render_template(
        'weather.html',
        weather=list_weather,
        three_hours_weather=three_hours_weather
    )


@app.route('/process_weather_by_city', methods=['POST'])
def process_weather_by_city():
    list_weather = select_current_weather()
    three_hours_weather = dict()
    c = 0
    for i in list_weather:
        if c == 3:
            break
        three_hours_weather[i['time']] = i['temperature']
        c += 1
    city = request.form['city']
    city_weather = get_weather_by_city(city)
    return render_template(
        'weather.html',
        weather=list_weather,
        three_hours_weather=three_hours_weather,
        city_weather=city_weather
    )


@app.route('/process_courses', methods=['POST'])
def process_courses():
    list_courses = select_current_courses()
    date = request.form['date'].split('-')
    courses_date = select_courses_by_date(date[0], date[1], date[2])
    error = ''
    if courses_date == -1:
        error = 'Неправильный формат ввода'
        courses_date = []
    return render_template(
        'courses.html',
        courses=list_courses,
        today=datetime.datetime.now().date(),
        courses_date=courses_date,
        error=error
    )


@app.route('/process_weather', methods=['POST'])
def process_weather():
    list_weather = select_current_weather()
    three_hours_weather = dict()
    c = 0
    for i in list_weather:
        if c == 3:
            break
        three_hours_weather[i['time']] = i['temperature']
        c += 1
    date = request.form['date'].split('-')
    weather_date = select_weather_by_date(date[0], date[1], date[2])
    error = ''
    if weather_date == -1:
        error = 'Неправильный формат ввода'
        weather_date = {'day_temperature': '', 'night_temperature': ''}
    return render_template(
        'weather.html',
        weather=list_weather,
        three_hours_weather=three_hours_weather,
        weather_date_day=weather_date['day_temperature'],
        weather_date_night=weather_date['night_temperature'],
        error=error
    )


@app.route('/process_movies', methods=['POST'])
def process_movies():
    list_movies = select_current_movies()
    date = request.form['date'].split('-')
    movies_date = select_movies_by_date(date[0], date[1], date[2])
    error = ''
    if movies_date == -1:
        error = 'Неправильный формат ввода'
        movies_date = []
    elif not movies_date:
        error = 'В этот день премьер не было'
        movies_date = []
    return render_template(
        'movies.html',
        list_movies=list_movies,
        movies_date=movies_date,
        error=error
    )


if __name__ == "__main__":
    cur_time = datetime.datetime.now()
    update_information_time(cur_time.hour - 1, cur_time.minute, cur_time.second)
    app.run(debug=True)
