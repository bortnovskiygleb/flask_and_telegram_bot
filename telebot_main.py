import telebot
from config import TOKEN
from components import get_movies_with_img, get_money, get_weather, get_cafes, get_pharmacies, get_atms

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
    button_geo = telebot.types.KeyboardButton("Отправить местоположение", request_location=True)
    keyboard.row("/movies", "/courses", "/weather")
    keyboard.row(button_geo)
    bot.send_message(message.chat.id, 'Вот что я могу делать!', reply_markup=keyboard)


@bot.message_handler(commands=['movies'])
def show_movies(message):
    chat_id = message.chat.id
    movies = get_movies_with_img()
    bot.send_message(chat_id, 'Cписок фильмов идущих в кино:\n')
    bot.send_chat_action(message.from_user.id, 'upload_photo')
    photos = []
    for name, img in movies.items():
        photos.append(telebot.types.InputMediaPhoto(img, name))
    for i in range(len(photos) // 10):
        bot.send_media_group(chat_id, photos[i * 10:i * 10 + 10], disable_notification=True)
    bot.send_media_group(chat_id, photos[len(photos) // 10 * 10:len(photos)], disable_notification=True)


@bot.message_handler(commands=['courses'])
def show_courses(message):
    chat_id = message.chat.id
    courses_list = get_money()
    courses_str = 'Курсы валют сегодня:\n'
    for i in range(len(courses_list)):
        courses_str += f'{courses_list[i]["Cur_OfficialRate"]} рублей за 1 {courses_list[i]["Cur_Name"]}\n'
    bot.send_message(chat_id, courses_str)


@bot.message_handler(commands=['weather'])
def show_weather(message):
    chat_id = message.chat.id
    weather_list = get_weather()
    weather_str = 'Погода на 24 часа:\n'
    for time, temperature in weather_list.items():
        weather_str += f'В {time} температура {temperature}\n'
    bot.send_message(chat_id, weather_str)


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        x = message.location.longitude
        y = message.location.latitude
        cafes = get_cafes(x, y)
        outer = 'Список ближайших кафе:\n'
        for name, description in cafes.items():
            outer += f'{name} --- {description}\n'
        outer += '\n'
        pharmacies = get_pharmacies(x, y)
        outer += 'Список ближайших аптек:\n'
        for name, description in pharmacies.items():
            outer += f'{name} --- {description}\n'
        outer += '\n'
        atms = get_atms(x, y)
        outer += 'Список ближайших банкоматов:\n'
        for name, description in atms.items():
            outer += f'{name} --- {description}\n'
        bot.send_message(message.chat.id, outer)


bot.polling(none_stop=True, interval=0)
