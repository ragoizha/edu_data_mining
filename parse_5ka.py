import json
import time
import requests


class StatusCodeError(Exception):
    def __init__(self, txt):
        self.txt = txt


class Parser:
    _params = {
        "records_per_page": 50,
    }
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
        'Accept-Language': 'ru,en;q=0.9',
    }

    def __init__(self, start_url, category_url):
        self.start_url = start_url
        self.category_url = category_url

    @staticmethod
    def _get_response(url, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(url, **kwargs)
                if response.status_code != 200:
                    raise StatusCodeError(f'status {response.status_code}')
                time.sleep(0.1)
                return response
            except (requests.exceptions.ConnectTimeout, StatusCodeError):
                time.sleep(0.25)

    def run(self):
        for category in self.get_categories(self.category_url):
            data = {
                'parent_group_name': category['parent_group_name'],
                'parent_group_code': category['parent_group_code'],
                'products': [],
            }

            self._params['categories'] = category['parent_group_code']

            for products in self.parse(self.start_url):
                data['products'].extend(products)
            self.save_files(data, category['parent_group_code'])

    def parse(self, url):
        while url:
            response = self._get_response(url, params=self._params, headers=self._headers)
            data: dict = response.json()
            url = data['next']
            yield data.get('results', [])

    def get_categories(self, url):
        response = requests.get(url, headers=self._headers)
        return response.json()

    @staticmethod
    def save_files(data: dict, file_name):
        with open(f'products/{file_name}.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parser(
        'https://5ka.ru/api/v2/special_offers/', 'https://5ka.ru/api/v2/categories/'
    )
    parser.run()
