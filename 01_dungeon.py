# -*- coding: utf-8 -*-

# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет две локации и один монстр
# (то есть в коренном json-объекте содержится список, содержащий два json-объекта, одного монстра и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье,
# готовый к следующей попытке (игра начинается заново).
#
# Гарантируется, что искомый путь только один, и будьте аккуратны в рассчетах!
# При неправильном использовании библиотеки decimal человек, играющий с вашим скриптом рискует никогда не найти путь.
#
# Также, при каждом ходе игрока ваш скрипт должен запоминать следущую информацию:
# - текущую локацию
# - текущее количество опыта
# - текущие дату и время (для этого используйте библиотеку datetime)
# После успешного или неуспешного завершения игры вам необходимо записать
# всю собранную информацию в csv файл dungeon.csv.
# Названия столбцов для csv файла: current_location, current_experience, current_date
#
#
# Пример взаимодействия с игроком:
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло времени: 00:00
#
# Внутри вы видите:
# — Вход в локацию: Location_1_tm1040
# — Вход в локацию: Location_2_tm123456
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали переход в локацию Location_2_tm1234567890
#
# Вы находитесь в Location_2_tm1234567890
# У вас 0 опыта и осталось 0.0987654321 секунд до наводнения
# Прошло времени: 20:00
#
# Внутри вы видите:
# — Монстра Mob_exp10_tm10
# — Вход в локацию: Location_3_tm55500
# — Вход в локацию: Location_4_tm66600
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали сражаться с монстром
#
# Вы находитесь в Location_2_tm0
# У вас 10 опыта и осталось -9.9012345679 секунд до наводнения
#
# Вы не успели открыть люк!!! НАВОДНЕНИЕ!!! Алярм!
#
# У вас темнеет в глазах... прощай, принцесса...
# Но что это?! Вы воскресли у входа в пещеру... Не зря матушка дала вам оберег :)
# Ну, на этот-то раз у вас все получится! Трепещите, монстры!
# Вы осторожно входите в пещеру... (текст умирания/воскрешения можно придумать свой ;)
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло уже 0:00:00
# Внутри вы видите:
#  ...
#  ...
#
# и так далее...

field_names = ['current_location', 'current_experience', 'current_date']
# если изначально не писать число в виде строки - теряется точность!
import datetime
import collections
import json
from decimal import Decimal, ROUND_FLOOR
import re
import time
import csv


class Dungeon:
    def __init__(self):
        self.re_mob = r'[M]\w{,2}|[Bb]\w{,3}'
        self.re_location = r'Location_\w\d*|Hatch'
        self.re_time = r'(\d+\.\d+)|(\d+$)'
        self.re_exp = r'\d+'

        self.remaining_time = '123456.0987654321'
        self.total_exp = 0
        self.csv_file = 'dungeon.csv'

        self.item_list = []

        time_play = datetime.datetime.now()
        self.csv_list = []
        self.current_time = time_play.strftime("%Y-%m-%d-%H.%M.%S")
        self.current_location = None

        self.exit_the_game = ''

    def write_csv_file(self):
        '''
        Запись результатов игры в файл в формате .csv
        '''
        self.csv_list = [{
            'current_location': self.current_location,
            'current_experience': self.total_exp,
            'current_date': self.current_time
        }]
        with open(self.csv_file, 'w') as dungeon_game_data_file:
            writer = csv.DictWriter(dungeon_game_data_file, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(self.csv_list)

    def unpack(self, data_file):
        '''
        Распаковка JSON - файла
        :return: python - объект
        '''
        with open(data_file, 'r') as game_file:
            self.data_game = json.load(game_file)
        return self.data_game

    def location_items(self):
        '''
        Функция сбора данных о локации
        :param location: передает словарь где Локация - ключ, значение - предметы в локации
        :return: возвращает список предметов в локации
        '''
        location = self.data_game
        self.item_list.clear()
        for key, sub_lines in location.items():
            if isinstance(key, str):
                self.inner_location = key
                print('Now you are in', self.inner_location)
                self.current_location = self.inner_location
                print('You have', self.total_exp, ' exp, and', self.remaining_time,
                      ' time.')

            for item in sub_lines:
                if isinstance(item, dict):
                    for keys_ in item.keys():
                        self.item_list.append(keys_)

            if isinstance(sub_lines, list):
                for item in sub_lines:

                    if isinstance(item, str):
                        self.item_list.append(item)

        return self.item_list

    def action_in_location(self):
        '''
        функция обработки данных о Локации
        :param item_list: список данных о Локации
        :return: возвращает выбор пользователя и словарь выбора действий
        '''
        self.action_dict = collections.defaultdict(int)
        count = 0
        for any in self.item_list:
            if any:
                count += 1
                if 'Mob' in any:
                    self.action_dict[count] = any
                    print('Fight with', any, '. Press - ', count)

                elif 'Location' or 'Hatch' in any:
                    self.action_dict[count] = any
                    print('Move to', any, '. Press - ', count)

        print('For Exit press - ', count + 1)
        count += 1
        self.action_dict[count] = 'Exit'

        while True:
            if self.check_answer():
                break

        self.user_action()

    def user_action(self):
        '''
        Функция обработки ответа пользователя
        :param action_dict: словарь выбора действий в локации
        :param user_answer: ответ пользователя о действии
        :param total_exp: общий опыт игрока
        :param remaining_time: оставшееся время игрока
        :return: возвращает словарь оставшихся действий или выбор игрока
        '''
        user_answer = int(self.user_answer)
        for keys, values in self.action_dict.items():

            if '_exp' in values and user_answer == keys:
                mob_exp = re.search(self.re_exp, values)
                time_fight = re.search(self.re_time, values)
                mob_exp = int(mob_exp[0])
                time_fight = time_fight[0]

                self.total_exp += mob_exp
                self.remaining_time = Decimal(self.remaining_time, ) - Decimal(time_fight)

                print('----------------------------')
                print('You are winner!!!')
                print('Exp: ', self.total_exp, 'Time: ', self.remaining_time)

                for key in self.action_dict.keys():
                    if key == user_answer:
                        del self.item_list[user_answer - 1]

                self.action_in_location()  # вызов функции действий игрока если была выбрана атака на Моба
                break

            elif 'Location' in values and user_answer == keys:
                time_to_move = re.search(self.re_time, values)
                self.remaining_time = Decimal(self.remaining_time) - Decimal(time_to_move[0])

                self.location_str = values
                print('You are going to location: ', self.location_str)
                print('Exp: ', self.total_exp, 'Time: ', self.remaining_time)
                location = self.search()

                return location

            elif 'Hatch' in values and user_answer == keys:
                time_loc = re.search(self.re_time, values)
                if Decimal(self.remaining_time) > Decimal(time_loc[0]):
                    if self.total_exp >= 280:
                        print('Winner! You are out.')
                        self.write_csv_file()
                        self.exit_the_game = 'Exit'
                        self.exit()
                    else:
                        if len(self.action_dict) < 3:
                            print('Not enough time to open a hatch...stupid death...')
                            time.sleep(2)
                            print('What is wrong?? You are still alive?! Or again alive???'
                                  ' Never mind, go ahead warrior!')

                            self.write_csv_file()

                            self.unpack('rpg.json')  # погнали заново
                            self.remaining_time = '123456.0987654321'
                            self.total_exp = 0
                            self.start_the_game()
                        else:
                            print('You have not enough exp for this, but there is a couple Mobs, fight with them boy!')
                            self.action_in_location()


            elif 'xit' in values and user_answer == keys:
                self.write_csv_file()
                self.exit_the_game = 'Exit'
                self.exit()
                break

    def check_answer(self):
        '''
        Проверка ввода ответа от пользователя
        '''
        self.user_answer = input('Choose your act: ')

        if len(self.user_answer) != 1 or self.user_answer.isdigit() is False:
            print('Really?!?! Are you sure man?? What did you type here?? '
                  'Try again and let the force be with you!')

        if len(self.user_answer) == 1 and int(self.user_answer) not in self.action_dict.keys():
            print('Really?!?! Are you sure man?? What did you type here?? '
                  'Try again and let the force be with you!')
        else:
            return True

    def search(self):
        '''
        Функция поиска нужной (игрок выбрал) Локации в общем списке
        :param place: словарь в котором надо искать
        :param location_str: строка-ключ какую локацию надо найти
        :return: возвращает словарь где ключ-выбраная игроком локация, значение-предметы в Локации
        '''
        self.location = {}
        for values in self.data_game.values():
            for name in values:
                if isinstance(name, dict):
                    for key, value in name.items():
                        if self.location_str in key:
                            self.location[key] = value
                            self.data_game = self.location
                            return self.data_game

    def exit(self):
        """
        Выход из игры
        """
        if 'Exit' in self.exit_the_game:
            return True

    def start_the_game(self):
        '''
        Запуск игры
        :return:
        '''
        while True:
            print('--------------------------------')
            if self.exit():
                print('Exiting..........')
                break

            self.location_items()
            self.action_in_location()


dungeon = Dungeon()
dungeon.unpack('rpg.json')
dungeon.start_the_game()

# Учитывая время и опыт, не забывайте о точности вычислений!
#зачет!