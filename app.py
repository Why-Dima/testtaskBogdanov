from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from extensions import ConvertException, MoneyConverter
import requests
import json
import os
import random

from conf import TOKEN, money, cities, TOKENWEATHER


# cities = ['London', 'Moscow']

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    text = 'В этом боте ты можешь узнать прогноз погоды, курс валюты' \
           '\n Чтобы узнать курс введите в именительном падеже:' \
           '\n - Имя валюты из которой нужно перевести' \
           '\n - Имя валюты в которую нужно перевести' \
           '\n - Количество переводимой валюты' \
           '\n Список всех доступных валют:/values' \
           '\n Чтобы узнать погоду в городе:' \
           '\n выбери город /city'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f'Прислать картинку', callback_data='картинка'), 
               types.InlineKeyboardButton(f'Отправить опрос', callback_data='опрос'))
    await message.bot.send_message(message.from_user.id, text, reply_markup=markup)

@dp.message_handler(commands=['values'])
async def values(message: types.Message):
    text = 'Доступные валюты:'
    for i in money.keys():#итерируемся по словарю и выводим ключи, это наши доступные валюты
        text = '\n'.join((text, i))
    await message.bot.send_message(message.from_user.id, text)

@dp.message_handler(commands=['city'])
async def city(message: types.Message):
    listcities = []
    markup = types.InlineKeyboardMarkup(row_width=2)
    for city in cities:#итерируемся по скиску городов и добавляем их в кнопки
        city_append = types.InlineKeyboardButton(f'{city}', callback_data=city)
        listcities.append(city_append)
    markup.add(*listcities)
    await message.bot.send_message(message.chat.id, 'Выберите город в котором хотите узнать погоду:',
                                reply_markup=markup)    

@dp.callback_query_handler(lambda call: True)
async def weather(call):
    if call.message.text == 'Выберите город в котором хотите узнать погоду:':
        for city in cities:#Итерируемся по спику с городами
            if call.data == city:#Если город из списка совпадает с нажатой кнопкой, то отправляем запрос с выбранным городом
                r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={TOKENWEATHER}&units=metric')
                print(city)
                bases = json.loads(r.content)['main']['temp']
                await bot.send_message(call.message.chat.id, f'Температура в {city}: {bases} °C')
    elif call.data == 'картинка':
        photo = open('image/' + random.choice(os.listdir('image')), 'rb')#выводим случайную каритнку из папки с помощью библиотеки random
        await bot.send_photo(call.message.chat.id, photo, caption = 'Держи')
    elif call.data == 'опрос':#отправляем опрос в групповой чат
        await bot.send_poll(chat_id=0000, question = 'Как дела?', options = ['Хорошо', 'Отлично'])#вместо 0000 нужно подставить id группового чата
    
@dp.message_handler(content_types=['text', ])
async def convert(message: types.Message):
    try:#Проверяем данные валют, которые ввел пользователь
        values = message.text.lower().split(' ')
        if len(values) != 3:
            raise ConvertException('Параметров больше трёх')
        quote, base, amount = values
        total_base = MoneyConverter.get_price(quote, base, amount)
    except ConvertException as e:
        await message.bot.send_message(message.chat.id, f'Ошибка пользователя\n{e}')
    except Exception as e:
        await message.bot.send_message(message.chat.id, f'Не удалось обработать команду\n{e}')
    else:#Если ошибок не обнаружено, то выводим курс
        total_base = float(total_base) * float(amount)#считаем цену валюты перемножая курс и введенное нами значение
        text = f'Цена {amount} {quote} в {base} = {"%.2f" % total_base}'
        await message.bot.send_message(message.chat.id, text)
    

if __name__ == '__main__':
    executor.start_polling(dp)

