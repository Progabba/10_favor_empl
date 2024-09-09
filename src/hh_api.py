from pprint import pprint

import requests


class HHAPI:
    def __init__(self):
        self.base_url = 'https://api.hh.ru/employers'

    def get_employers(self, employer_ids):
        employers = []
        for employer_id in employer_ids:
            url = f'{self.base_url}/{employer_id}'
            response = requests.get(url)
            if response.status_code == 200:
                employers.append(response.json())
        return employers

    def get_vacancies(self, employer_id):
        url = f'https://api.hh.ru/vacancies?employer_id={employer_id}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['items']
        return []


if __name__ == '__main__':
    hh_api = HHAPI()
    employer_ids = ['15478', '9301808', '9498120', '4181', '2180', '903111', '745654', '84585', '1781300',
                    '1122462']  # Пример ID работодателей
    employers = hh_api.get_employers(employer_ids)
    for emp in employers:
        pprint(emp)
        print("\n" * 5)
