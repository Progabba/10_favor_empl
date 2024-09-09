from pprint import pprint

from config import config
from src.db_filler import DB_filler
from src.hh_api import HHAPI
from src.db_setup import  DBPostgres

from src.db_manager import DBManager

def main():
    # Инициализация базы данных
    params = config()
    dbname = 'test_4'
    db_test = DBPostgres(dbname, params=params)
    db_test.create_db()
    db_test.create_table()

    # Получение данных с API и заполнение БД
    hh_api = HHAPI()
    employer_ids = ['15478', '9301808', '9498120', '4181', '2180', '903111', '745654', '84585', '1781300', '1122462']  # Пример ID работодателей
    employers = hh_api.get_employers(employer_ids)
    db_filler = DB_filler(dbname, params)
    db_filler.fill_db(employers)

    # Работа с БД
    db_manager = DBManager(dbname, params)

    # Пример использования методов DBManager
    print("Компании и количество вакансий:")
    pprint(db_manager.get_companies_and_vacancies_count())

    print("Все вакансии:")
    pprint(db_manager.get_all_vacancies())
    #
    print("Средняя зарплата:")
    pprint(db_manager.get_avg_salary())

    print("Вакансии с зарплатой выше средней:")
    pprint(db_manager.get_vacancies_with_higher_salary())

    print("Вакансии с ключевым словом 'python':")
    pprint(db_manager.get_vacancies_with_keyword('python'))

if __name__ == '__main__':
    main()
