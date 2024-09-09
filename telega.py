import asyncio
import logging
import os
from aiogram.filters import Command

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

from config import config
from src.db_filler import DB_filler
from src.hh_api import HHAPI
from src.db_setup import DBPostgres
from src.db_manager import DBManager

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not API_TOKEN:
    raise ValueError("Telegram bot token not found in environment variables")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

params = config()
current_dbname = None

# Определение состояний ФСМ
class JobSearchStates(StatesGroup):
    set_db = State()
    set_ids = State()
    set_keyword = State()



@dp.message(Command(commands=['start']))
async def start(message: Message):
    await message.answer("Привет! Я бот для получения информации о вакансиях. Используйте кнопку ниже:\n"
                        "/set_db <название_базы> - установить название базы данных\n")


@dp.message(Command(commands=['set_db']))
async def set_dbname(message: Message, state: FSMContext):
    await message.answer("Введите название базы данных:")
    await state.set_state(JobSearchStates.set_db)

@dp.message(JobSearchStates.set_db)
async def process_dbname(message: Message, state: FSMContext):
    global current_dbname  # Сначала объявляем переменную как глобальную
    dbname = f'db_{message.text}'  # Название базы данных идет после команды
    current_dbname = dbname  # Теперь можем присвоить ей значение
    db_test = DBPostgres(dbname, params=params)
    db_test.create_db()
    db_test.create_table()

    await message.reply(f"База данных '{dbname}' создана и готова к использованию.")
    await state.clear()
    await message.answer("/set_ids - установить ID компаний\n")
#
#
@dp.message(Command(commands=['set_ids']))
async def set_employer_ids(message: Message, state: FSMContext):
    await message.answer("Введите список ID компаний, разделенных запятыми \n например '15478', '9301808', '9498120', '4181', '2180', '903111', '745654', '84585', '1781300', '1122462':")
    await state.set_state(JobSearchStates.set_ids)

@dp.message(JobSearchStates.set_ids)
async def process_ids(message: Message, state: FSMContext):
    # Получаем список ID и убираем лишние пробелы
    ids = message.text.split(',')
    ids = [id_.strip().strip("'") for id_ in ids]  # Очищаем от пробелов и апострофов
    print(ids)  # Выводим список ID для проверки



    await message.answer(f"Вы ввели следующие ID: {', '.join(ids)}")

    hh_api = HHAPI()
    employers = hh_api.get_employers(ids)
    db_filler = DB_filler(current_dbname, params)
    db_filler.fill_db(employers)

    await message.reply("Данные о работодателях добавлены в базу данных.")
    await state.clear()
    await message.answer("/companies - получить список компаний и количество вакансий\n"
                        "/vacancies - получить все вакансии\n"
                        "/avg_salary - получить среднюю зарплату\n"
                        "/high_salary - получить вакансии с зарплатой выше средней\n"
                        "/keyword <ключевое слово> - получить вакансии по ключевому слову")
#
#
@dp.message(Command(commands=['companies']))
async def get_companies(message: Message):
    db_manager = DBManager(current_dbname, params)
    result = db_manager.get_companies_and_vacancies_count()
    print(result)
    response = "\n".join([f"{name}: {count} вакансий" for name, count in result])
    await message.answer(response or "Нет данных")
    await message.answer("/companies - получить список компаний и количество вакансий\n"
                        "/vacancies - получить все вакансии\n"
                        "/avg_salary - получить среднюю зарплату\n"
                        "/high_salary - получить вакансии с зарплатой выше средней\n"
                        "/keyword <ключевое слово> - получить вакансии по ключевому слову")
#
#
@dp.message(Command(commands=['vacancies']))
async def get_companies(message: Message):
    db_manager = DBManager(current_dbname, params)
    result = db_manager.get_all_vacancies()

    if not result:
        await message.reply("Нет данных")
        return

    # Формируем ответ
    response_parts = []
    response = ""
    for name, title, salary, url in result:
        vacancy_info = f"{name} - {title}: {salary} - {url}\n"
        if len(response + vacancy_info) > 4000:  # Лимит символов в одном сообщении
            response_parts.append(response)
            response = vacancy_info
        else:
            response += vacancy_info
    if response:
        response_parts.append(response)

    # Отправляем каждую часть отдельно
    for part in response_parts:
        await message.reply(part)

    # Отправляем команды в конце
    await message.answer("/companies - получить список компаний и количество вакансий\n"
                         "/vacancies - получить все вакансии\n"
                         "/avg_salary - получить среднюю зарплату\n"
                         "/high_salary - получить вакансии с зарплатой выше средней\n"
                         "/keyword <ключевое слово> - получить вакансии по ключевому слову")
#
#
@dp.message(Command(commands=['avg_salary']))
async def get_companies(message: Message):
    db_manager = DBManager(current_dbname, params)
    result = db_manager.get_avg_salary()
    await message.reply(f"Средняя зарплата: {result[0] if result[0] else 'Нет данных'}")
    await message.answer("/companies - получить список компаний и количество вакансий\n"
                         "/vacancies - получить все вакансии\n"
                         "/avg_salary - получить среднюю зарплату\n"
                         "/high_salary - получить вакансии с зарплатой выше средней\n"
                         "/keyword <ключевое слово> - получить вакансии по ключевому слову")
#
#
@dp.message(Command(commands=['high_salary']))
async def get_companies(message: Message):

    db_manager = DBManager(current_dbname, params)
    result = db_manager.get_vacancies_with_higher_salary()
    response = "\n".join([f"{title}: {salary}" for title, salary in result])
    await message.reply(response or "Нет данных")
    await message.answer("/companies - получить список компаний и количество вакансий\n"
                         "/vacancies - получить все вакансии\n"
                         "/avg_salary - получить среднюю зарплату\n"
                         "/high_salary - получить вакансии с зарплатой выше средней\n"
                         "/keyword <ключевое слово> - получить вакансии по ключевому слову")
#
#
@dp.message(Command(commands=['keyword']))
async def set_keyword(message: Message, state: FSMContext):
    await message.answer("Введите ключевое слово для поиска вакансий")
    await state.set_state(JobSearchStates.set_keyword)


@dp.message(JobSearchStates.set_keyword)
async def process_companies(message: Message):
    # Получаем аргумент из текста сообщения после команды /keyword
    keyword = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
    keyword = keyword.strip()

    db_manager = DBManager(current_dbname, params)
    result = db_manager.get_vacancies_with_keyword(keyword)

    # Создаем ответ в виде строки
    response = "\n".join([f"{title}" for title, in result])

    # Определяем максимальный размер сообщения (4096 символов)
    max_message_length = 4096
    if len(response) > max_message_length:
        # Разбиваем сообщение на части по 4096 символов
        for i in range(0, len(response), max_message_length):
            await message.reply(response[i:i + max_message_length])
    else:
        await message.reply(response or "Нет данных")

    await message.answer("/companies - получить список компаний и количество вакансий\n"
                         "/vacancies - получить все вакансии\n"
                         "/avg_salary - получить среднюю зарплату\n"
                         "/high_salary - получить вакансии с зарплатой выше средней\n"
                         "/keyword <ключевое слово> - получить вакансии по ключевому слову")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
