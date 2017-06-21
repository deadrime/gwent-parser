import pickle
import requests
import urllib.request
from bs4 import BeautifulSoup
import json


class gwent_card:
    def __init__(self):
        self.name = ''
        self.abilities = ''
        self.quote = ''
        self.type = ''
        self.faction = ''
        self.power = ''
        self.rarity = ''
        self.lane = ''
        self.scrap_cost = ''
        self.mill_cost = ''
        self.img_big = ''
        self.img_small = ''

    def to_string(self):
        return self.__dict__


class parser:
    def __init__(self):
        # Самый первый запрос для определения количества страниц
        url = 'http://www.gwentdb.com/cards'
        r = requests.get(url)
        s = BeautifulSoup(r.content, 'html.parser')
        # Находим количество страниц для парсинга
        nav_ul = s.find('ul', 'b-pagination-list')
        self.max_pages = nav_ul.find_all('li')[-2].get_text()
        self.bd = {}  # база данных со всеми картами
        self.path = 'img/'  # путь где лежат картинки

    def parse_cards_from_page(self, page_url):
        r = requests.get(page_url)
        page = BeautifulSoup(r.content, 'html.parser')
        cards = page.findAll('div', 'sw-card-visual-info')

        for card_div in cards:
            card = gwent_card()
            card.img_small = card_div.find('img').get('src')
            card.name = ' '.join((card_div.find('h1').get_text()).split())  # Какого-то хрена там есть лишние пробелы
            card_url = 'http://www.gwentdb.com' + card_div.find('a').get('href')
            info = self.parse_card(card, card_url)  # Парсим остальную инфу со страны карты
            id = card.name
            id = id.replace("'", '').replace(': ', '_').replace(' ', '_').replace('–', '_').replace(' ', '_').replace(':', '_').lower()
            print(id)
            # Если нужно скачать картинки
            # self.download_img(card.img_small, id + '_s')
            # self.download_img(card.img_big, id + '_b')
            self.bd[id] = info

    def parse_card(self, card, url):
        print('Парсинг карты ' + url)
        r = requests.get(url)
        s = BeautifulSoup(r.content, 'html.parser')
        card_div = s.find('div', 'main-card')
        card_abilities = card_div.find('div', 'card-abilities').get_text()
        card.abilities = ' '.join(card_abilities.split())
        card_quote = card_div.find('div', 'sw-card-flavor-text').get_text()
        card.quote = ' '.join(card_quote.split())
        card.type = card_div.find('div', 'card-type').find('a').get_text()
        card.faction = card_div.find('div', 'card-faction').find('a').get_text()
        try:  # для случая, когда нет поля card_power
            card.power = card_div.find('div', 'card-power').find('span').get_text()
        except AttributeError:
            card.power = -1
        card.rarity = card_div.find('div', 'card-rarity').find('span').get_text()
        card.lane = card_div.find('div', 'card-row').find('span').get_text(',')
        crafting = card_div.findAll('div', 'card-crafting-type')
        card.scrap_cost = crafting[0].find('span').get_text().replace('(Premium)', '')
        card.mill_cost = crafting[1].find('span').get_text().replace('(Premium)', '')
        card.img_big = card_div.find('section', 'card-image').find('a').get('href')
        return card.to_string()

    def parse_all(self):
        for i in range(1, int(self.max_pages) + 1):
            page_url = 'http://www.gwentdb.com/cards?page=' + str(i)
            print('Парсинг страницы ' + page_url)
            self.parse_cards_from_page(page_url)  # Парсинг отдельной страницы с картами

    def download_img(self, img_url, img_name):
        filename = self.path + img_name + '.png'
        urllib.request.urlretrieve(img_url, filename)

    def save_pickle(self):
        with open('data.pickle', 'wb') as f:  # сохранение всей этой херни в файл, потом можно и в бд sql
            pickle.dump(self.bd, f)
        f.close()

    def save_json(self):
        with open('data.json', 'wb') as f:
            myjson = json.dumps(self.bd, ensure_ascii=False).encode('utf8')
            f.write(myjson)
        f.close()

    def run(self):
        self.parse_all()
        self.save_json()
        self.save_pickle()

p = parser()
p.run()