import psycopg2
from config import config

class DBPostgres:
    """Класс для создания и удаления базы данных в postgresSQL"""

    def __init__(self, dbname: str, params: dict):
        self.dbname = dbname
        self.params = params

    def create_db(self):
        """функция создания базы данных"""

        #Подключаемся к базе данных
        conn = psycopg2.connect(dbname="postgres", **self.params)
        conn.autocommit = True
        cur = conn.cursor()

        #Создаем базу данных, но перед этим удаляем если есть с таким названием"""
        cur.execute(f"DROP DATABASE IF EXISTS {self.dbname};")
        cur.execute(f"CREATE DATABASE {self.dbname};")
        conn.close()
    def create_table(self):
        """Подключаемся к базе данных"""
        conn = psycopg2.connect(dbname=self.dbname, **self.params)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                salary INT,
                url TEXT,
                employer_id INT REFERENCES employers(id)
            );
        """)

        conn.commit()
        cur.close()
        conn.close()


if __name__ == "__main__":
    params = config()
    db_test = DBPostgres('test_2', params=params)
    db_test.create_db()
    db_test.create_table()