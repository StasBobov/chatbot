import random

import requests
import vk_api
import logging

from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import handlers
from models import UserState, Registration

log = logging.getLogger('bot')

try:
    import settings
except ImportError:
    exit("DO cp settings.py.default settings.py")


def configure_logging():
    log.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(name)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename='bot.log', encoding='UTF-8', mode='w')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(message)s', datefmt='%d-%m-%Y %H:%M'))  # TODO
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)


class Bot:
    """ Бот-синебот для vk.com с поддержкой IP "Товарищ майор - удалённый доступ" """

    def __init__(self, group_id, token):
        """

        :param group_id: групп ID из группы vk
        :param token: секретный токен
        """
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """ Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Вот, что пошло не так: ')

    @db_session
    def on_event(self, event):
        """
        Обрабатывает события
        :param event: VkBotMessageEvent object
        :return:
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            return
        # user_id = event.message['from_id']
        user_id = event.object['message']['from_id']
        # text = event.message['text']
        text = event.object['message']['text']
        state = UserState.get(user_id=str(user_id))

        if state is not None:
            # продолжаем сценарий
            self.continue_scenario(user_id=user_id, text=text, state=state)
        else:
            # ищем новый интент
            for intent in settings.INTENTS: # пробегаемся по нашим паттернам
                for token in intent['tokens'].split(): # проверяем каждый токен в паттерне
                    if text.lower().find(token) != -1:
                        if intent['answer']:
                            self.send_text(text_to_send=intent['answer'], user_id=user_id)
                            log.debug('Пользователь с ID: %d интересовался нашим мероприятием', user_id)
                        else:
                            self.start_scenario(user_id, intent['scenario'], text)
                        return
            else:
                self.send_text(text_to_send=settings.DEFAULT_ANSWER, user_id=user_id)

    def send_text(self, text_to_send, user_id):
        self.api.messages.send(peer_id=user_id,
                               message=text_to_send,
                                random_id=random.randint(0, 2 ** 20))

    def send_image(self, image, user_id):
        # получаем доступ к серверу
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        # передаём файл
        upload_data = requests.post(url=upload_url, files={'photo' : ('image.png', image, 'image/png')}).json()
        # сохраняем файл
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        # отправляем файл пользователю
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(peer_id=user_id,
                               attachment=attachment,
                               random_id=random.randint(0, 2 ** 20))

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            # отформатировали текст при помощи значений state.context
            self.send_text(text_to_send=step['text'].format(**context), user_id=user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_image(image=image, user_id=user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step=step, user_id=user_id, text=text, context={})
        # self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step, context={})
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})


    def continue_scenario(self, user_id, text, state):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler']) # находит функцию handle_name или handle_event
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
                log.debug('Пользователь с ID: %d, внёс информацию: %s', user_id,
                          state.context)
            else:
                log.debug('Зарегистрировался пользователь с ID: %d, name: %s, с email: %s', user_id,
                          state.context['name'], state.context['email'])
                Registration(name=state.context['name'], email=state.context['email'])
                state.delete()
        else:
            text_to_send = step['failure_text'].format(**state.context)
            self.send_text(text_to_send=text_to_send, user_id=user_id)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id=settings.GROUP_ID, token=settings.TOKEN)
    bot.run()
