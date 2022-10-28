# -*- coding: utf-8 -*-
TOKEN = ""
GROUP_ID = 0

INTENTS = [
        {
                'name' : 'Дата проведения',
                'tokens' : 'когда сколько дата дату',
                'scenario' : None,
                'answer' : 'Конференция проводится 15 апреля, регистрация начнётся в 10 утра'
        },
        {
                'name' : 'Место проведения',
                'tokens' : 'где место локация адрес метро',
                'scenario' : None,
                'answer' : 'Конференция проводится в павильоне 18Г в Экспоцентре'
        },
        {
                'name' : 'Регистрация',
                'tokens' : 'регист добав',
                'scenario' : 'registration',
                'answer' : None
        }
]

SCENARIOS = {
        'registration' : {
                'first_step' : 'step1',
                'steps' : {
                        'step1' : {
                                'text' : 'Нужно зарегистрироваться. Введите Ваше имя, оно будет написано на бейдже.',
                                'failure_text' : 'Имя должно состоять из 3-30 букв и дефиса. Попробуйте ещё раз.',
                                'handler' : 'handle_name',
                                'next_step' : 'step2'
                        },
                        'step2' : {
                                'text' : 'Введите email, мы отправим на него все данные.',
                                'failure_text' : 'Во введённом адресе ошибка. Попробуйте ещё раз.',
                                'handler' : 'handle_email',
                                'next_step' : 'step3'
                        },
                        'step3': {
                                'text': 'Спасибо за регистрацию {name}! Мы отправили на {email} билет, распечатайте '
                                        'его.',
                                'failure_text': None,
                                'handler': None,
                                'next_step': None
                        }}}}

DEFAULT_ANSWER = 'Не знаю как на это ответить.' 'Могу сказать когда и где пройдёт конференция, а также зарегистрировать ' \
                 'Вас. Просто спросите'


DB_CONFIG = dict(provider='postgres',
                 user='',
                 password='',
                 host='',
                 database='vk_chat_bot')