import pickle
import requests
import urllib.request
from bs4 import BeautifulSoup
import json


class gwent_card:
    def __init__(self):
        self.name = ''  # Название
        self.text = ''  # Описание
        self.quote = ''  # Цитата
        self.rarity = ''  # Редкость, Common/Rare/Epic/Legendary
        self.group = ''  # Бронзовая, серебрянная, золотая...
        self.type = ''  # Тип, например - Machine
        self.faction = ''  # Фракция, Neutral - нейтральная
        self.strength = ''  # -1, если это заклинание/погода
        self.position = ''  # Позиция, если Event - то заклинаение/погода\
        self.loyalty = ''
        self.craft_cost = ''  # Создание
        self.mill_cost = ''  # Распыление
        self.mechanics = []
        # self.img_big = ''
        # self.img_small = ''

    def to_string(self):
        return self.__dict__


class parser:
    def __init__(self):
        # Самый первый запрос для определения количества страниц
        url = 'http://gwentify.com/cards/?view=table'
        r = requests.get(url)
        s = BeautifulSoup(r.content, 'html.parser')
        # Находим количество страниц для парсинга
        nav_ul = s.find('ul', 'pagination')
        self.max_pages = nav_ul.find('a', 'last').get('href').split('/')[5]
        print(self.max_pages)
        self.bd = {}  # база данных со всеми картами
        self.path = 'img/'  # путь где лежат картинки

    def parse_cards_from_page(self, page_url):
        r = requests.get(page_url)
        page = BeautifulSoup(r.content, 'html.parser')
        cards = page.findAll('a', 'card-link')

        for card_div in cards:
            card = gwent_card()
            # card.img_small = card_div.find('img').get('src')
            card.name = card_div.find('strong').get_text() # Какого-то хрена там есть лишние пробелы
            print(card.name)
            card_url = card_div.get('href')
            info = self.parse_card(card, card_url)  # Парсим остальную инфу со страны карты
            id = card.name.replace("'", '').replace(': ', '_').replace(' ', '_').replace('–', '_').replace(' ', '_').replace(':', '_').lower()
            # print(id)
            # Если нужно скачать картинки
            # self.download_img(card.img_small, id + '_s')
            # self.download_img(card.img_big, id + '_b')
            self.bd[id] = info

    def parse_card(self, card, url):
        print('Парсинг карты ' + url)
        r = requests.get(url)
        s = BeautifulSoup(r.content, 'html.parser')
        card_div = s.find('main', 'site-main')
        card_abilities = card_div.find('div', 'card-text').get_text()
        card.text = ' '.join(card_abilities.split())

        try:
            card.quote = card_div.find('p', 'flavor').get_text()
        except Exception:
            card.quote = ''

        card_stats = card_div.find('ul', 'card-cats').findAll('li')

        for stat in card_stats:
            card.__dict__[stat.get_text().split(': ')[0].lower()] = stat.get_text().split(': ')[1]  # Говнокод, суть в том, что card.power = '0'

        card_cost = card_div.findAll('ul', 'card-cats')[1].findAll('li')
        card.craft_cost = card_cost[0].get_text().split(': ')[1].split(' (Premium)')[0]
        card.mill_cost = card_cost[1].get_text().split(': ')[1].split(' (Premium)')[0]
        card_mechanic = card_div.findAll('ul', 'card-cats')[2].findAll('strong')
        for m in card_mechanic:
            print(m.get_text())
            card.mechanics.append(m.get_text())
        print(card.__dict__)
        return card.to_string()

    def parse_all(self):
        for i in range(1, int(self.max_pages) + 1):
            if i == 1:
                page_url = 'http://gwentify.com/cards/?view=table'
            else:
                page_url = 'http://gwentify.com/cards/page/'+str(i)+'/?view=table'
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
#p.run()
card = gwent_card()

p.parse_card(card,'http://gwentify.com/cards/zoltan-chivay/')