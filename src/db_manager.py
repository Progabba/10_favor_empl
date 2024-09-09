import psycopg2
from config import config
from src.db_setup import DBPostgres

class DBManager(DBPostgres):
    def __init__(self, dbname: str, params: dict):
        super().__init__(dbname, params)

    def get_companies_and_vacancies_count(self):
        try:
            # Создаем подключение к базе данных
            conn = psycopg2.connect(dbname=self.dbname, **self.params)
            with conn.cursor() as cur:
                # Выполняем запрос для получения количества вакансий у каждой компании
                cur.execute("""
                    SELECT employers.name, COUNT(vacancies.id) AS vacancies_count
                    FROM employers
                    LEFT JOIN vacancies ON employers.id = vacancies.employer_id
                    GROUP BY employers.name;
                """)
                # Возвращаем результат запроса
                result = cur.fetchall()
                return result
        except psycopg2.Error as e:
            # Обрабатываем ошибки выполнения запроса
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            conn.close()

    def get_all_vacancies(self):
        try:
            conn = psycopg2.connect(dbname=self.dbname, **self.params)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT employers.name, vacancies.title, vacancies.salary, vacancies.url
                    FROM vacancies
                    JOIN employers ON vacancies.employer_id = employers.id;
                """)
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            conn.close()

    def get_avg_salary(self):
        try:
            conn = psycopg2.connect(dbname=self.dbname, **self.params)
            with conn.cursor() as cur:
                cur.execute("SELECT AVG(salary) FROM vacancies;")
                return cur.fetchone()
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None
        finally:
            conn.close()

    def get_vacancies_with_higher_salary(self):
        avg_salary = self.get_avg_salary()[0]
        try:
            conn = psycopg2.connect(dbname=self.dbname, **self.params)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT title, salary FROM vacancies
                    WHERE salary > %s;
                """, (avg_salary,))
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            conn.close()

    def get_vacancies_with_keyword(self, keyword):
        try:
            conn = psycopg2.connect(dbname=self.dbname, **self.params)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT title FROM vacancies
                    WHERE title ILIKE %s;
                """, (f'%{keyword}%',))
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []
        finally:
            conn.close()

if __name__ == '__main__':
    params = config()
    db_name = 'test_3'
    manager = DBManager(db_name, params=params)

    print("Компании и количество вакансий:")
    print(manager.get_companies_and_vacancies_count())

    print("Все вакансии:")
    print(manager.get_all_vacancies())

    print("Средняя зарплата:")
    print(manager.get_avg_salary())

    print("Вакансии с зарплатой выше средней:")
    print(manager.get_vacancies_with_higher_salary())

    print("Вакансии с ключевым словом 'Vacancy':")
    print(manager.get_vacancies_with_keyword('Vacancy'))
