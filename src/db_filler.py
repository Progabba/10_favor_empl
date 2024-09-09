import psycopg2

from config import config
from src.db_setup import DBPostgres
from src.hh_api import HHAPI
from src import hh_api


class DB_filler(DBPostgres):
    def __init__(self, dbname: str, params: dict):
        super().__init__(dbname, params)

    def fill_db(self, employers):
        api = HHAPI()
        # Подключаемся к новой базе данных
        conn = psycopg2.connect(dbname=self.dbname, **self.params)
        cur = conn.cursor()

        # Заполняем таблицу работодателей
        for employer in employers:
            cur.execute("INSERT INTO employers (name) VALUES (%s) RETURNING id", (employer['name'],))
            employer_id = cur.fetchone()[0]

            # Получаем вакансии для каждого работодателя
            vacancies = api.get_vacancies(employer['id'])
            for vacancy in vacancies:
                salary = vacancy['salary']['from'] if vacancy['salary'] else None
                cur.execute("""
                    INSERT INTO vacancies (title, salary, url, employer_id)
                    VALUES (%s, %s, %s, %s)
                """, (vacancy['name'], salary, vacancy['alternate_url'], employer_id))

        conn.commit()
        cur.close()
        conn.close()


if __name__ == "__main__":
    params = config()
    db_name = 'test_3'

    # Создаем базу данных и таблицы
    db_setup = DBPostgres(db_name, params)
    db_setup.create_db()
    db_setup.create_table()

    # Пример списка работодателей для тестирования
    employers = [
        {"name": "Company f", "id": 1},
        {"name": "Company B", "id": 2}
    ]

    # Вызов функции заполнения базы данных
    db_filler = DB_filler(db_name, params)
    db_filler.fill_db(employers)