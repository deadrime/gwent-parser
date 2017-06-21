import pickle
import postgresql
import configparser
import json
conf = configparser.RawConfigParser()


class bd:
    def __init__(self):
        self.user = ''
        self.host = ''
        self.database = ''
        self.port = 0
        self.password = ''
        self.cards_bd = None
        self.load_config()
        self.load_bd()

    def load_bd(self):
        try:
            self.cards_bd = pickle.load(open("data.pickle", "rb"))
        except Exception as msg:
            print(msg)
            raise SystemExit

    def load_config(self):
        conf = configparser.RawConfigParser()
        try:
            conf.read("config.conf")
            self.user = conf['BD']['user']
            self.host = conf['BD']['host']
            self.database = conf['BD']['database']
            self.port = conf['BD']['port']
            self.password = conf['BD']['password']
        except Exception as msg:
            print(msg)
            raise SystemExit
        else:
            print('Успешное подключение к ' + self.host + ':' + self.port + '/' + self.database)

    def push_all_cards(self):
        with postgresql.open(user=self.user, host=self.host, database=self.database, port=self.port, password=self.password) as db:
            for obj in self.cards_bd:
                insert_card = db.prepare("INSERT INTO card (id, name,abilities,quote,type,faction,power,rarity,lane,scrap_cost,mill_cost,img_s,img_l)"
                                         " VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)")
                card = self.cards_bd[obj]
                print(card['power'])
                if card['power'] == 'none':
                    card['power'] = -1
                insert_card(
                    obj,
                    card['name'],
                    card['abilities'],
                    card['quote'],
                    card['type'],
                    card['faction'],
                    int(card['power']),
                    card['rarity'],
                    card['lane'],
                    int(card['scrap_cost'].split('/')[0]),
                    int(10),
                    card['img_big'],
                    card['img_small']
                )

    def save_json(self):
        with open('data.json', 'wb') as f:
            myjson = json.dumps(self.cards_bd, ensure_ascii=False).encode('utf8')
            f.write(myjson)
        f.close()

    def print_bd(self):
        for card in self.cards_bd:
            print(self.cards_bd[card])

new_bd = bd()
new_bd.print_bd()